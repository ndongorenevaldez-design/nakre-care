"""Business authorization only. Lot 3 must additionally require a verified MFA session.

Never expose a default ModelAdmin: queryset, FK choices and each action must use
these policies. Django ORM/DB credentials remain trusted backend capabilities.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from apps.intake.models import CareRequest, RequestAssignment
from apps.patients.models import PatientCase, CaseAssignment


def current_actor(actor, *, lock=False):
    if not getattr(actor, "is_authenticated", False) or not actor.pk:
        raise PermissionDenied
    query = get_user_model().objects
    if lock:
        query = query.select_for_update()
    fresh = query.filter(pk=actor.pk, is_active=True, is_staff=True).first()
    if fresh is None:
        raise PermissionDenied
    return fresh


def require_capability(actor, capability):
    if not actor.has_perm(capability):
        raise PermissionDenied


def _requests(actor, *, write=False):
    query = CareRequest.objects.all()
    if not actor.has_perm("intake.view_carerequest"):
        return query.none()
    if actor.is_superuser:
        return query
    own = RequestAssignment.objects.filter(user=actor, active=True)
    if write:
        own = own.filter(can_process=True)
    scope = Q(pk__in=own.values("request_id"))
    if actor.has_perm("intake.triage_unassigned"):
        scope |= ~Q(
            pk__in=RequestAssignment.objects.filter(active=True).values("request_id")
        )
    return query.filter(scope)


def _cases(actor, *, write=False):
    query = PatientCase.objects.all()
    if not actor.has_perm("patients.view_patientcase"):
        return query.none()
    if actor.is_superuser:
        return query
    assignments = CaseAssignment.objects.filter(user=actor, active=True)
    if write:
        assignments = assignments.filter(can_manage=True)
    return query.filter(pk__in=assignments.values("case_id"))


def visible_requests(actor):
    return _requests(current_actor(actor))


def visible_cases(actor):
    return _cases(current_actor(actor))


def get_request(actor, request_id):
    try:
        obj = visible_requests(actor).filter(pk=request_id).first()
    except (ValidationError, ValueError):
        obj = None
    if obj is None:
        raise PermissionDenied
    return obj


def get_case(actor, case_id):
    try:
        obj = visible_cases(actor).filter(pk=case_id).first()
    except (ValidationError, ValueError):
        obj = None
    if obj is None:
        raise PermissionDenied
    return obj


def require_request(actor, obj, capability, *, write=True):
    require_capability(actor, capability)
    if not _requests(actor, write=write).filter(pk=obj.pk).exists():
        raise PermissionDenied


def require_case(actor, obj, capability, *, write=True):
    require_capability(actor, capability)
    if not _cases(actor, write=write).filter(pk=obj.pk).exists():
        raise PermissionDenied


def visible_reviews(actor):
    from apps.intake.models import RequestReview

    actor = current_actor(actor)
    require_capability(actor, "intake.view_requestreview")
    return RequestReview.objects.filter(request__in=_requests(actor))


def visible_contacts(actor):
    from apps.patients.models import AuthorizedContact

    actor = current_actor(actor)
    require_capability(actor, "patients.view_authorizedcontact")
    return AuthorizedContact.objects.filter(case__in=_cases(actor))


def usable_contacts(actor):
    """Current authorizations only; caller must additionally respect each scope."""
    from django.utils import timezone

    return (
        visible_contacts(actor)
        .filter(revoked_at__isnull=True)
        .filter(Q(valid_until__isnull=True) | Q(valid_until__gt=timezone.now()))
    )


def visible_plans(actor):
    from apps.patients.models import CarePlan

    actor = current_actor(actor)
    require_capability(actor, "patients.view_careplan")
    return CarePlan.objects.filter(case__in=_cases(actor))


def visible_interventions(actor):
    from apps.interventions.models import Intervention

    actor = current_actor(actor)
    require_capability(actor, "interventions.view_intervention")
    return Intervention.objects.filter(plan__case__in=_cases(actor))


def visible_intervention_events(actor):
    from apps.interventions.models import InterventionEvent

    actor = current_actor(actor)
    require_capability(actor, "interventions.view_interventionevent")
    return InterventionEvent.objects.filter(
        intervention__in=visible_interventions(actor)
    )


def visible_audit_events(actor):
    from apps.audit.models import AuditEvent

    actor = current_actor(actor)
    # Global audit access is intentionally restricted to superadministrators.
    if not actor.is_superuser:
        raise PermissionDenied
    return AuditEvent.objects.all()


def visible_notifications(actor):
    from apps.notifications.models import NotificationOutbox

    actor = current_actor(actor)
    require_capability(actor, "notifications.view_notificationoutbox")
    # All events emitted in Lot 2 concern a request; future event types need scopes.
    return NotificationOutbox.objects.filter(
        target_id__in=_requests(actor).values("pk"),
        event_type__in=["request.created", "request.accepted"],
    )
