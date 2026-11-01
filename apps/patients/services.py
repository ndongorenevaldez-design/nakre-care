from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from apps.accounts import policies
from apps.common.services import Conflict, locked, check_version, save_validated, record
from apps.patients.models import (
    PatientCase,
    CaseAssignment,
    AuthorizedContact,
    CarePlan,
    PlanService,
)
from apps.intake.models import ServiceType


@transaction.atomic
def assign_case(*, actor, case_id, user_id, can_manage=False, active=True):
    actor = policies.current_actor(actor, lock=True)
    case = locked(PatientCase.objects, case_id)
    policies.require_case(actor, case, "patients.assign_case")
    user = (
        get_user_model()
        .objects.filter(pk=user_id, is_active=True, is_staff=True)
        .first()
    )
    if not user:
        raise ValidationError("Administrateur actif requis.")
    if user.pk == actor.pk and not actor.is_superuser:
        raise PermissionDenied
    current = CaseAssignment.objects.filter(case=case, user=user, active=True).first()
    if current:
        current.active = False
        current.revoked_at = timezone.now()
        current.save(update_fields=["active", "revoked_at"])
    assignment = CaseAssignment.objects.create(
        case=case,
        user=user,
        active=active,
        can_manage=can_manage,
        revoked_at=None if active else timezone.now(),
    )
    record(actor, "case.assignment_changed", assignment)
    return assignment


@transaction.atomic
def transition_case(*, actor, case_id, target, expected_version):
    actor = policies.current_actor(actor, lock=True)
    case = locked(PatientCase.objects, case_id)
    policies.require_case(actor, case, "patients.change_patientcase")
    check_version(case, expected_version)
    allowed = {"active": {"suspended", "closed"}, "suspended": {"active", "closed"}}
    if target not in allowed.get(case.status, set()):
        raise Conflict("Transition de dossier interdite.")
    from apps.interventions.models import Intervention

    if (
        target in {"suspended", "closed"}
        and Intervention.objects.filter(plan__case=case, status="planned").exists()
    ):
        raise Conflict(
            "Annulez ou terminez les interventions prévues avant cette transition."
        )
    case.status = target
    case.closed_at = timezone.now() if target == "closed" else None
    case.version += 1
    save_validated(case)
    if target == "closed":
        CarePlan.objects.filter(case=case, active=True).update(active=False)
    record(actor, f"case.{target}", case)
    return case


@transaction.atomic
def authorize_contact(
    *, actor, case_id, name, phone, relationship, scope, valid_until=None
):
    actor = policies.current_actor(actor, lock=True)
    case = locked(PatientCase.objects, case_id)
    policies.require_case(actor, case, "patients.add_authorizedcontact")
    if case.status == "closed":
        raise Conflict("Dossier clos.")
    contact = save_validated(
        AuthorizedContact(
            case=case,
            name=name,
            phone=phone,
            relationship=relationship,
            scope=scope,
            verified_by=actor,
            verified_at=timezone.now(),
            valid_until=valid_until,
        )
    )
    record(actor, "contact.authorized", contact)
    return contact


@transaction.atomic
def revoke_contact(*, actor, contact_id):
    actor = policies.current_actor(actor, lock=True)
    # Parent is always locked before child, matching other dossier operations.
    contact = AuthorizedContact.objects.filter(pk=contact_id).first()
    if not contact:
        raise PermissionDenied
    case = locked(PatientCase.objects, contact.case_id)
    policies.require_case(actor, case, "patients.change_authorizedcontact")
    contact = locked(AuthorizedContact.objects, contact_id)
    if contact.revoked_at is None:
        contact.revoked_at = timezone.now()
        contact.save(update_fields=["revoked_at"])
        record(actor, "contact.revoked", contact)
    return contact


@transaction.atomic
def replace_plan(
    *, actor, case_id, expected_version, starts_on, frequency, service_ids, ends_on=None
):
    actor = policies.current_actor(actor, lock=True)
    case = locked(PatientCase.objects, case_id)
    policies.require_case(actor, case, "patients.add_careplan")
    check_version(case, expected_version)
    if case.status != "active":
        raise Conflict("Dossier actif requis.")
    ids = set(service_ids)
    services = list(ServiceType.objects.filter(pk__in=ids, active=True))
    if not ids or len(services) != len(ids):
        raise ValidationError("Prestations actives requises.")
    version = (case.plans.aggregate(latest=Max("version"))["latest"] or 0) + 1
    case.plans.filter(active=True).update(active=False)
    plan = save_validated(
        CarePlan(
            case=case,
            version=version,
            starts_on=starts_on,
            ends_on=ends_on,
            frequency=frequency,
        )
    )
    for service in services:
        PlanService.objects.create(plan=plan, service=service)
    case.version += 1
    case.save(update_fields=["version"])
    record(actor, "plan.created", plan)
    return plan
