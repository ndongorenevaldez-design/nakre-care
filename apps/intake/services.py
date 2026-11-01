from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.utils import timezone
from apps.accounts import policies
from apps.common.services import (
    Conflict,
    check_version,
    save_validated,
    record,
    queue_blocked,
    locked,
)
from apps.intake.models import (
    CareRequest,
    ConsentRecord,
    RequestAssignment,
    RequestReview,
    ServiceType,
    RequestedService,
)
from apps.patients.models import PatientCase, CaseAssignment

PUBLIC_FIELDS = frozenset(
    {
        "requester_name",
        "requester_phone",
        "requester_email",
        "relationship",
        "beneficiary_name",
        "beneficiary_age",
        "city",
        "intervention_address",
        "context",
        "desired_start",
        "availability",
        "latitude",
        "longitude",
        "proposed_contact_name",
        "proposed_contact_phone",
    }
)
CONSENT_FIELDS = frozenset(
    {"purpose", "notice_version", "legal_basis", "declarant_capacity", "agreed"}
)


@transaction.atomic
def create_request(*, actor, data, consent, service_ids):
    """Internal ingestion for authorized staff/tests only; no anonymous HTTP route."""
    actor = policies.current_actor(actor, lock=True)
    policies.require_capability(actor, "intake.add_carerequest")
    if set(data) - PUBLIC_FIELDS or set(consent) - CONSENT_FIELDS:
        raise ValidationError("Champ inattendu.")
    ids = set(service_ids)
    services = list(ServiceType.objects.filter(pk__in=ids, active=True))
    if not ids or len(services) != len(ids):
        raise ValidationError("Prestations actives requises.")
    obj = save_validated(CareRequest(**data))
    for service in services:
        RequestedService.objects.create(request=obj, service=service)
    save_validated(ConsentRecord(request=obj, **consent))
    record(actor, "request.created", obj)
    queue_blocked("request.created", obj)
    return obj


@transaction.atomic
def assign_request(*, actor, request_id, user_id, can_process=False, active=True):
    actor = policies.current_actor(actor, lock=True)
    obj = locked(CareRequest.objects, request_id)
    policies.require_request(actor, obj, "intake.assign_request")
    user = (
        get_user_model()
        .objects.filter(pk=user_id, is_active=True, is_staff=True)
        .first()
    )
    if user is None:
        raise ValidationError("Administrateur actif requis.")
    # No self-escalation, even for coordinators with assignment capabilities.
    if actor.pk == user.pk and not actor.is_superuser:
        raise PermissionDenied
    assignment, _ = RequestAssignment.objects.update_or_create(
        request=obj,
        user=user,
        defaults={
            "active": active,
            "can_process": can_process,
            "revoked_at": None if active else timezone.now(),
        },
    )
    record(actor, "request.assignment_changed", assignment)
    return assignment


@transaction.atomic
def transition_request(*, actor, request_id, target, expected_version, orientation=""):
    actor = policies.current_actor(actor, lock=True)
    obj = locked(CareRequest.objects, request_id)
    policies.require_request(actor, obj, "intake.change_carerequest")
    check_version(obj, expected_version)
    allowed = {"new": {"review", "cancelled"}, "review": {"refused", "cancelled"}}
    if target not in allowed.get(obj.status, set()):
        raise Conflict(
            "Transition interdite ; l’acceptation utilise la conversion dédiée."
        )
    previous = obj.status
    obj.status = target
    obj.version += 1
    save_validated(obj)
    save_validated(
        RequestReview(
            request=obj,
            actor=actor,
            from_status=previous,
            to_status=target,
            orientation=orientation,
        )
    )
    record(actor, "request.status_changed", obj)
    return obj


@transaction.atomic
def accept_request(*, actor, request_id, expected_version, orientation=""):
    actor = policies.current_actor(actor, lock=True)
    obj = locked(CareRequest.objects, request_id)
    policies.require_request(actor, obj, "intake.change_carerequest")
    policies.require_capability(actor, "patients.add_patientcase")
    policies.require_capability(actor, "patients.view_patientcase")
    if obj.status == CareRequest.Status.ACCEPTED:
        case = PatientCase.objects.get(request=obj)
        policies.require_case(actor, case, "patients.view_patientcase", write=False)
        return case  # idempotent retry; never create a second dossier
    check_version(obj, expected_version)
    if obj.status != CareRequest.Status.REVIEW:
        raise Conflict("La demande doit être en évaluation.")
    obj.status = CareRequest.Status.ACCEPTED
    obj.version += 1
    save_validated(obj)
    case = save_validated(PatientCase(request=obj))
    # Accepting actor gets an explicit dossier assignment, not access to all dossiers.
    CaseAssignment.objects.create(case=case, user=actor, can_manage=True)
    save_validated(
        RequestReview(
            request=obj,
            actor=actor,
            from_status="review",
            to_status="accepted",
            orientation=orientation,
        )
    )
    record(actor, "request.accepted", obj)
    record(actor, "case.created", case)
    queue_blocked("request.accepted", obj)
    return case
