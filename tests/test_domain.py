from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Permission
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection, connections, transaction
from django.db.migrations.executor import MigrationExecutor
from django.db.models.deletion import ProtectedError
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from apps.accounts import policies
from apps.audit.models import AuditEvent
from apps.common.services import Conflict
from apps.intake.models import (
    CareRequest,
    ConsentRecord,
    RequestAssignment,
    RequestReview,
    RequestedService,
    ServiceType,
)
from apps.intake import services as intake
from apps.patients.models import (
    PatientCase,
    AuthorizedContact,
    CarePlan,
    CaseAssignment,
)
from apps.patients import services as patients
from apps.interventions.models import StaffMember, Intervention, InterventionEvent
from apps.interventions import services as interventions
from apps.notifications.models import NotificationOutbox, NotificationAttempt

DATA = dict(
    requester_name="Demandeur FICTIF",
    requester_phone="000000000",
    relationship="proche fictif",
    beneficiary_name="Bénéficiaire FICTIF",
    city="Ville test",
    proposed_contact_name="Contact déclaré fictif",
    proposed_contact_phone="000000001",
)
CONSENT = dict(
    purpose="test-synthetique",
    notice_version="test-v1",
    legal_basis="simulation exclusivement",
    declarant_capacity="simulation",
    agreed=True,
)


class Fixtures:
    def setUp(self):
        self.root = get_user_model().objects.create_superuser("root@example.invalid")
        self.other_root = get_user_model().objects.create_superuser(
            "other@example.invalid"
        )
        self.member = get_user_model().objects.create_user(
            "member@example.invalid", is_staff=True
        )
        self.service, _ = ServiceType.objects.get_or_create(
            code="domicile", defaults={"label": "Accompagnement à domicile"}
        )

    def grant(self, user, *codes):
        for code in codes:
            app, codename = code.split(".")
            user.user_permissions.add(
                Permission.objects.get(content_type__app_label=app, codename=codename)
            )

    def request(self):
        return intake.create_request(
            actor=self.root, data=DATA, consent=CONSENT, service_ids=[self.service.pk]
        )

    def reviewing(self):
        obj = self.request()
        return intake.transition_request(
            actor=self.root, request_id=obj.pk, target="review", expected_version=0
        )

    def case(self):
        obj = self.reviewing()
        return intake.accept_request(
            actor=self.root, request_id=obj.pk, expected_version=1
        )

    def plan(self):
        case = self.case()
        plan = patients.replace_plan(
            actor=self.root,
            case_id=case.pk,
            expected_version=0,
            starts_on=timezone.localdate(),
            frequency="ponctuel",
            service_ids=[self.service.pk],
        )
        return case, plan


class DomainTests(Fixtures, TestCase):
    def test_creation_consent_and_no_real_delivery(self):
        obj = self.request()
        self.assertEqual(obj.status, "new")
        self.assertEqual(len(obj.reference), 32)
        self.assertNotEqual(obj.reference, obj.pk.hex)
        self.assertEqual(obj.consents.count(), 1)
        self.assertEqual(obj.services.count(), 1)
        self.assertEqual(NotificationOutbox.objects.count(), 2)
        self.assertEqual(
            set(NotificationOutbox.objects.values_list("status", flat=True)),
            {"blocked"},
        )
        self.assertEqual(NotificationAttempt.objects.count(), 0)
        self.assertNotIn(DATA["requester_name"], str(obj))
        self.assertEqual(AuditEvent.objects.first().action, "request.created")

    def test_creation_whitelist_and_validation_atomic(self):
        for data in [
            {**DATA, "status": "accepted"},
            {**DATA, "beneficiary_age": 121},
            {**DATA, "latitude": 10},
            {**DATA, "context": "x" * 1001},
        ]:
            with self.assertRaises(ValidationError):
                intake.create_request(
                    actor=self.root,
                    data=data,
                    consent=CONSENT,
                    service_ids=[self.service.pk],
                )
        self.assertEqual(CareRequest.objects.count(), 0)
        self.assertEqual(ConsentRecord.objects.count(), 0)
        self.assertEqual(NotificationOutbox.objects.count(), 0)
        with self.assertRaises(ValidationError):
            intake.create_request(
                actor=self.root, data=DATA, consent={}, service_ids=[self.service.pk]
            )
        self.assertEqual(CareRequest.objects.count(), 0)

    def test_creation_requires_active_staff_and_permission(self):
        for actor in [AnonymousUser(), self.member]:
            with self.assertRaises(PermissionDenied):
                intake.create_request(
                    actor=actor,
                    data=DATA,
                    consent=CONSENT,
                    service_ids=[self.service.pk],
                )
        get_user_model().objects.filter(pk=self.root.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.request()

    def test_uniqueness_and_ranges_enforced_by_database(self):
        obj = self.request()
        for kwargs in [
            {"reference": obj.reference},
            {"beneficiary_age": 121},
            {"latitude": 91, "longitude": 0},
            {"status": "invented"},
        ]:
            with self.assertRaises(IntegrityError), transaction.atomic():
                CareRequest.objects.create(**{**DATA, **kwargs})
        with self.assertRaises(IntegrityError), transaction.atomic():
            RequestedService.objects.create(request=obj, service=self.service)
        with self.assertRaises(IntegrityError), transaction.atomic():
            ServiceType.objects.create(code=self.service.code, label="doublon")

    def test_allowed_deletion_and_protected_relations(self):
        empty = CareRequest.objects.create(**DATA)
        RequestedService.objects.create(request=empty, service=self.service)
        empty.delete()  # draft-like raw fixture without consent/history; link cascades
        self.assertFalse(RequestedService.objects.exists())
        obj = self.request()
        with self.assertRaises(ProtectedError):
            obj.delete()
        with self.assertRaises(ProtectedError):
            self.service.delete()
        with self.assertRaises(ProtectedError):
            self.root.delete()

    def test_acceptance_requires_review_and_is_idempotent(self):
        obj = self.request()
        with self.assertRaises(Conflict):
            intake.accept_request(
                actor=self.root, request_id=obj.pk, expected_version=0
            )
        intake.transition_request(
            actor=self.root, request_id=obj.pk, target="review", expected_version=0
        )
        case = intake.accept_request(
            actor=self.root, request_id=obj.pk, expected_version=1
        )
        duplicate = intake.accept_request(
            actor=self.root, request_id=obj.pk, expected_version=1
        )
        self.assertEqual(case.pk, duplicate.pk)
        self.assertEqual(PatientCase.objects.count(), 1)
        self.assertEqual(RequestReview.objects.filter(to_status="accepted").count(), 1)
        self.assertEqual(AuthorizedContact.objects.count(), 0)
        self.assertEqual(CaseAssignment.objects.count(), 1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            PatientCase.objects.create(request_id=obj.pk)

    def test_conversion_failure_rolls_back_all_writes(self):
        obj = self.reviewing()
        baseline = AuditEvent.objects.count()
        with patch(
            "apps.intake.services.queue_blocked",
            side_effect=RuntimeError("synthetic failure"),
        ):
            with self.assertRaises(RuntimeError):
                intake.accept_request(
                    actor=self.root, request_id=obj.pk, expected_version=1
                )
        obj.refresh_from_db()
        self.assertEqual(obj.status, "review")
        self.assertEqual(obj.version, 1)
        self.assertFalse(PatientCase.objects.exists())
        self.assertFalse(CaseAssignment.objects.exists())
        self.assertEqual(AuditEvent.objects.count(), baseline)
        self.assertEqual(NotificationOutbox.objects.count(), 2)

    def test_forbidden_and_stale_transitions(self):
        obj = self.reviewing()
        for target, version in [("new", 1), ("accepted", 1), ("refused", 0)]:
            with self.assertRaises(Conflict):
                intake.transition_request(
                    actor=self.root,
                    request_id=obj.pk,
                    target=target,
                    expected_version=version,
                )
        intake.transition_request(
            actor=self.root, request_id=obj.pk, target="refused", expected_version=1
        )
        with self.assertRaises(Conflict):
            intake.accept_request(
                actor=self.root, request_id=obj.pk, expected_version=2
            )

    def test_deferred_database_acceptance_consistency(self):
        obj = self.request()
        with self.assertRaises(IntegrityError), transaction.atomic():
            PatientCase.objects.create(request=obj)
            with connection.cursor() as cursor:
                cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
        with self.assertRaises(IntegrityError), transaction.atomic():
            CareRequest.objects.filter(pk=obj.pk).update(status="accepted")
            with connection.cursor() as cursor:
                cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")

    def test_history_cannot_be_rewritten_even_by_queryset(self):
        obj = self.reviewing()
        for model, field in [
            (AuditEvent, "action"),
            (ConsentRecord, "purpose"),
            (RequestReview, "orientation"),
        ]:
            item = model.objects.first()
            with self.assertRaises(ValidationError):
                item.save()
            with self.assertRaises(IntegrityError), transaction.atomic():
                model.objects.filter(pk=item.pk).update(**{field: "tampered"})
            with self.assertRaises(IntegrityError), transaction.atomic():
                model.objects.filter(pk=item.pk).delete()
        self.assertNotIn("FICTIF", str(list(AuditEvent.objects.values())))

    def test_contact_is_explicit_and_revocable(self):
        case = self.case()
        self.assertFalse(case.authorized_contacts.exists())
        contact = patients.authorize_contact(
            actor=self.root,
            case_id=case.pk,
            name="FICTIF",
            phone="000",
            relationship="test",
            scope="organisation",
        )
        self.assertEqual(contact.verified_by, self.root)
        self.assertIsNone(contact.revoked_at)
        patients.revoke_contact(actor=self.root, contact_id=contact.pk)
        contact.refresh_from_db()
        self.assertIsNotNone(contact.revoked_at)
        with self.assertRaises(ValidationError):
            patients.authorize_contact(
                actor=self.root,
                case_id=case.pk,
                name="FICTIF",
                phone="000",
                relationship="test",
                scope="",
            )

    def test_plan_versioning_and_unique_active(self):
        case, plan = self.plan()
        with self.assertRaises(IntegrityError), transaction.atomic():
            CarePlan.objects.create(
                case=case, version=2, starts_on=timezone.localdate(), frequency="test"
            )
        with self.assertRaises(Conflict):
            patients.replace_plan(
                actor=self.root,
                case_id=case.pk,
                expected_version=0,
                starts_on=timezone.localdate(),
                frequency="test",
                service_ids=[self.service.pk],
            )
        second = patients.replace_plan(
            actor=self.root,
            case_id=case.pk,
            expected_version=1,
            starts_on=timezone.localdate(),
            frequency="test",
            service_ids=[self.service.pk],
        )
        plan.refresh_from_db()
        self.assertFalse(plan.active)
        self.assertEqual(second.version, 2)
        with self.assertRaises(IntegrityError), transaction.atomic():
            CarePlan.objects.create(
                case=case,
                version=2,
                active=False,
                starts_on=timezone.localdate(),
                frequency="test",
            )

    def test_intervention_lifecycle_and_overlap(self):
        case, plan = self.plan()
        staff = StaffMember.objects.create(display_name="Intervenant fictif")
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=1)
        obj = interventions.schedule(
            actor=self.root,
            plan_id=plan.pk,
            staff_id=staff.pk,
            service_id=self.service.pk,
            start=start,
            end=end,
        )
        with self.assertRaises(Conflict):
            interventions.schedule(
                actor=self.root,
                plan_id=plan.pk,
                staff_id=staff.pk,
                service_id=self.service.pk,
                start=start,
                end=end,
            )
        with self.assertRaises(Conflict):
            patients.transition_case(
                actor=self.root, case_id=case.pk, target="closed", expected_version=1
            )
        interventions.transition(
            actor=self.root,
            intervention_id=obj.pk,
            target="done",
            expected_version=0,
            actual_start=start,
            actual_end=end,
            note="Observation fictive",
        )
        interventions.correct_note(
            actor=self.root,
            intervention_id=obj.pk,
            expected_version=1,
            note="Correction fictive",
            effective_at=end,
        )
        self.assertEqual(InterventionEvent.objects.count(), 3)
        with self.assertRaises(IntegrityError), transaction.atomic():
            InterventionEvent.objects.update(note="tampered")
        with self.assertRaises(Conflict):
            interventions.transition(
                actor=self.root,
                intervention_id=obj.pk,
                target="planned",
                expected_version=2,
            )
        patients.transition_case(
            actor=self.root, case_id=case.pk, target="closed", expected_version=1
        )
        case.refresh_from_db()
        self.assertIsNotNone(case.closed_at)
        with self.assertRaises(Conflict):
            patients.transition_case(
                actor=self.root, case_id=case.pk, target="active", expected_version=2
            )

    def test_intervention_database_time_constraints(self):
        case, plan = self.plan()
        staff = StaffMember.objects.create(display_name="FICTIF")
        now = timezone.now()
        for attrs in [
            {"scheduled_end": now - timedelta(hours=1)},
            {"status": "done"},
            {"actual_start": now},
        ]:
            with self.assertRaises(IntegrityError), transaction.atomic():
                Intervention.objects.create(
                    **{
                        "plan": plan,
                        "staff": staff,
                        "service": self.service,
                        "scheduled_start": now,
                        "scheduled_end": now + timedelta(hours=1),
                        **attrs,
                    }
                )


class AuthorizationTests(Fixtures, TestCase):
    def test_role_and_assignment_both_required(self):
        obj = self.reviewing()
        other = self.request()
        self.grant(self.member, "intake.view_carerequest", "intake.change_carerequest")
        self.assertFalse(policies.visible_requests(self.member).exists())
        intake.assign_request(
            actor=self.root,
            request_id=obj.pk,
            user_id=self.member.pk,
            can_process=False,
        )
        self.assertEqual(list(policies.visible_requests(self.member)), [obj])
        with self.assertRaises(PermissionDenied):
            intake.transition_request(
                actor=self.member,
                request_id=obj.pk,
                target="refused",
                expected_version=1,
            )
        intake.assign_request(
            actor=self.root, request_id=obj.pk, user_id=self.member.pk, can_process=True
        )
        intake.transition_request(
            actor=self.member, request_id=obj.pk, target="refused", expected_version=1
        )
        with self.assertRaises(PermissionDenied):
            policies.get_request(self.member, other.pk)
        self.member.user_permissions.clear()
        self.assertFalse(policies.visible_requests(self.member).exists())

    def test_triage_only_unassigned_and_no_self_escalation(self):
        obj = self.request()
        self.grant(
            self.member,
            "intake.view_carerequest",
            "intake.triage_unassigned",
            "intake.assign_request",
        )
        self.assertTrue(
            policies.visible_requests(self.member).filter(pk=obj.pk).exists()
        )
        with self.assertRaises(PermissionDenied):
            intake.assign_request(
                actor=self.member,
                request_id=obj.pk,
                user_id=self.member.pk,
                can_process=True,
            )
        intake.assign_request(
            actor=self.root, request_id=obj.pk, user_id=self.other_root.pk
        )
        self.assertFalse(policies.visible_requests(self.member).exists())

    def test_cases_never_globally_visible_to_staff(self):
        case = self.case()
        other = self.case()
        self.grant(
            self.member, "patients.view_patientcase", "patients.change_patientcase"
        )
        self.assertFalse(policies.visible_cases(self.member).exists())
        patients.assign_case(
            actor=self.root, case_id=case.pk, user_id=self.member.pk, can_manage=False
        )
        self.assertEqual(policies.get_case(self.member, case.pk), case)
        with self.assertRaises(PermissionDenied):
            policies.get_case(self.member, other.pk)
        with self.assertRaises(PermissionDenied):
            patients.transition_case(
                actor=self.member,
                case_id=case.pk,
                target="suspended",
                expected_version=0,
            )
        patients.assign_case(
            actor=self.root, case_id=case.pk, user_id=self.member.pk, can_manage=True
        )
        patients.transition_case(
            actor=self.member, case_id=case.pk, target="suspended", expected_version=0
        )
        patients.assign_case(
            actor=self.root, case_id=case.pk, user_id=self.member.pk, active=False
        )
        self.assertFalse(policies.visible_cases(self.member).exists())

    def test_child_collections_obey_case_permissions_and_contact_validity(self):
        case, plan = self.plan()
        other = self.case()
        contact = patients.authorize_contact(
            actor=self.root,
            case_id=case.pk,
            name="FICTIF",
            phone="000",
            relationship="test",
            scope="organisation",
        )
        patients.authorize_contact(
            actor=self.root,
            case_id=other.pk,
            name="AUTRE FICTIF",
            phone="000",
            relationship="test",
            scope="organisation",
        )
        self.grant(
            self.member,
            "patients.view_patientcase",
            "patients.view_authorizedcontact",
            "patients.view_careplan",
        )
        patients.assign_case(actor=self.root, case_id=case.pk, user_id=self.member.pk)
        self.assertEqual(list(policies.visible_contacts(self.member)), [contact])
        self.assertEqual(list(policies.visible_plans(self.member)), [plan])
        self.assertEqual(list(policies.usable_contacts(self.member)), [contact])
        patients.revoke_contact(actor=self.root, contact_id=contact.pk)
        self.assertFalse(policies.usable_contacts(self.member).exists())
        self.assertEqual(policies.visible_contacts(self.member).count(), 1)
        expired = AuthorizedContact.objects.create(
            case=case,
            name="FICTIF",
            phone="000",
            relationship="test",
            scope="organisation",
            verified_by=self.root,
            verified_at=timezone.now() - timedelta(days=2),
            valid_until=timezone.now() - timedelta(days=1),
        )
        self.assertFalse(
            policies.usable_contacts(self.member).filter(pk=expired.pk).exists()
        )
        with self.assertRaises(PermissionDenied):
            policies.visible_audit_events(self.member)
        with self.assertRaises(PermissionDenied):
            policies.visible_interventions(self.member)

    def test_active_assignment_unique_and_self_grant_forbidden(self):
        case = self.case()
        self.grant(self.member, "patients.view_patientcase", "patients.assign_case")
        patients.assign_case(
            actor=self.root, case_id=case.pk, user_id=self.member.pk, can_manage=True
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            CaseAssignment.objects.create(case=case, user=self.member)
        with self.assertRaises(PermissionDenied):
            patients.assign_case(
                actor=self.member,
                case_id=case.pk,
                user_id=self.member.pk,
                can_manage=True,
            )

    def test_group_role_revocation_is_effective_on_next_call(self):
        from django.contrib.auth.models import Group
        case = self.case()
        group = Group.objects.create(name="Administrateur synthétique")
        group.permissions.add(Permission.objects.get(content_type__app_label="patients", codename="view_patientcase"))
        self.member.groups.add(group)
        self.assertFalse(policies.visible_cases(self.member).exists())
        patients.assign_case(actor=self.root, case_id=case.pk, user_id=self.member.pk)
        self.assertEqual(policies.get_case(self.member, case.pk), case)
        group.permissions.clear()
        with self.assertRaises(PermissionDenied):
            policies.get_case(self.member, case.pk)

    def test_disabled_user_rejected_despite_stale_python_object(self):
        case = self.case()
        get_user_model().objects.filter(pk=self.root.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            policies.get_case(self.root, case.pk)

    def test_public_reference_not_access_key_or_route(self):
        case = self.case()
        request = case.request
        for actor in [AnonymousUser(), self.member]:
            with self.assertRaises(PermissionDenied):
                policies.get_case(actor, request.reference)
        with self.assertRaises(PermissionDenied):
            policies.get_case(self.root, request.reference)
        for path in [
            f"/prise-en-charge/{request.reference}/",
            f"/administration/{case.pk}/",
            f"/admin/{case.pk}/",
        ]:
            self.assertEqual(self.client.get(path).status_code, 404)


class ConcurrencyTests(Fixtures, TransactionTestCase):
    def parallel(self, action):
        barrier = Barrier(2)

        def run(actor_id):
            connections.close_all()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SET lock_timeout = '5s'")
                    cursor.execute("SET statement_timeout = '10s'")
                actor = get_user_model().objects.get(pk=actor_id)
                barrier.wait(timeout=5)
                return action(actor)
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(run, actor.pk) for actor in [self.root, self.other_root]
            ]
            return [f.result(timeout=15) for f in futures]

    def test_simultaneous_acceptance_one_case_and_history(self):
        obj = self.reviewing()
        results = self.parallel(
            lambda actor: (
                intake.accept_request(
                    actor=actor, request_id=obj.pk, expected_version=1
                ).pk
            )
        )
        self.assertEqual(results[0], results[1])
        self.assertEqual(PatientCase.objects.count(), 1)
        self.assertEqual(RequestReview.objects.filter(to_status="accepted").count(), 1)
        self.assertEqual(
            NotificationOutbox.objects.filter(event_type="request.accepted").count(), 2
        )

    def test_concurrent_status_change_rejects_stale_writer(self):
        obj = self.reviewing()

        def action(actor):
            try:
                intake.transition_request(
                    actor=actor, request_id=obj.pk, target="refused", expected_version=1
                )
                return "updated"
            except Conflict:
                return "conflict"

        self.assertCountEqual(self.parallel(action), ["updated", "conflict"])
        self.assertEqual(RequestReview.objects.filter(to_status="refused").count(), 1)

    def test_simultaneous_staff_booking_across_cases(self):
        case, plan = self.plan()
        other, second = self.plan()
        staff = StaffMember.objects.create(display_name="FICTIF")
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=1)

        def action(actor):
            try:
                interventions.schedule(
                    actor=actor,
                    plan_id=plan.pk if actor.pk == self.root.pk else second.pk,
                    staff_id=staff.pk,
                    service_id=self.service.pk,
                    start=start,
                    end=end,
                )
                return "scheduled"
            except Conflict:
                return "conflict"

        self.assertCountEqual(self.parallel(action), ["scheduled", "conflict"])
        self.assertEqual(Intervention.objects.count(), 1)


class MigrationTests(TransactionTestCase):
    def test_lot1_upgrade_and_reverse_on_postgresql(self):
        self.assertEqual(connection.vendor, "postgresql")
        executor = MigrationExecutor(connection)
        latest = executor.loader.graph.leaf_nodes()
        try:
            executor.migrate(
                [
                    (app, None)
                    for app in [
                        "audit",
                        "interventions",
                        "notifications",
                        "patients",
                        "intake",
                    ]
                ]
            )
            self.assertNotIn(
                "intake_carerequest", connection.introspection.table_names()
            )
        finally:
            MigrationExecutor(connection).migrate(latest)
        self.assertIn("patients_patientcase", connection.introspection.table_names())
        self.assertEqual(
            set(ServiceType.objects.values_list("code", flat=True)),
            {"domicile", "hospitalier", "deplacements"},
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM pg_trigger WHERE tgname IN ('nakre_immutable', 'nakre_request_case_consistency', 'nakre_case_request_consistency')"
            )
            self.assertEqual(cursor.fetchone()[0], 7)
