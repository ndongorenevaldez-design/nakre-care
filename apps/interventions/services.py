from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from apps.accounts import policies
from apps.common.services import Conflict, locked, check_version, save_validated, record
from apps.patients.models import CarePlan, PatientCase
from apps.interventions.models import Intervention, InterventionEvent, StaffMember


@transaction.atomic
def schedule(*, actor, plan_id, staff_id, service_id, start, end):
    actor = policies.current_actor(actor, lock=True)
    plan = CarePlan.objects.filter(pk=plan_id).first()
    if not plan:
        raise PermissionDenied
    case = locked(PatientCase.objects, plan.case_id)
    policies.require_case(actor, case, "interventions.add_intervention")
    plan.refresh_from_db()
    if case.status != "active" or not plan.active:
        raise Conflict("Plan et dossier actifs requis.")
    if timezone.is_naive(start) or timezone.is_naive(end) or end <= start:
        raise ValidationError("Horaires avec fuseau et fin après début requis.")
    if timezone.localtime(start).date() < plan.starts_on or (
        plan.ends_on and timezone.localtime(end).date() > plan.ends_on
    ):
        raise ValidationError("Intervention hors période du plan.")
    if not plan.services.filter(pk=service_id, active=True).exists():
        raise ValidationError("Prestation absente du plan ou inactive.")
    staff = locked(StaffMember.objects, staff_id)
    if not staff.active:
        raise ValidationError("Intervenant inactif.")
    if Intervention.objects.filter(
        staff=staff,
        status__in=["planned", "done"],
        scheduled_start__lt=end,
        scheduled_end__gt=start,
    ).exists():
        raise Conflict("Intervenant déjà affecté sur cette période.")
    obj = save_validated(
        Intervention(
            plan=plan,
            staff=staff,
            service_id=service_id,
            scheduled_start=start,
            scheduled_end=end,
        )
    )
    save_validated(
        InterventionEvent(
            intervention=obj,
            actor=actor,
            effective_at=timezone.now(),
            kind="scheduled",
            to_status="planned",
        )
    )
    record(actor, "intervention.scheduled", obj)
    return obj


@transaction.atomic
def transition(
    *,
    actor,
    intervention_id,
    target,
    expected_version,
    actual_start=None,
    actual_end=None,
    note="",
):
    actor = policies.current_actor(actor, lock=True)
    obj = Intervention.objects.filter(pk=intervention_id).select_related("plan").first()
    if not obj:
        raise PermissionDenied
    case = locked(PatientCase.objects, obj.plan.case_id)
    policies.require_case(actor, case, "interventions.change_intervention")
    locked(StaffMember.objects, obj.staff_id)
    obj = locked(Intervention.objects, intervention_id)
    check_version(obj, expected_version)
    if obj.status != "planned" or target not in {"done", "cancelled"}:
        raise Conflict("Transition d’intervention interdite.")
    if target == "done":
        if (
            not actual_start
            or not actual_end
            or timezone.is_naive(actual_start)
            or timezone.is_naive(actual_end)
        ):
            raise ValidationError("Dates réelles avec fuseau requises.")
        obj.actual_start, obj.actual_end = actual_start, actual_end
    elif actual_start or actual_end:
        raise ValidationError("Une annulation ne renseigne pas de dates réelles.")
    obj.status = target
    obj.version += 1
    save_validated(obj)
    save_validated(
        InterventionEvent(
            intervention=obj,
            actor=actor,
            effective_at=timezone.now(),
            kind="transition",
            from_status="planned",
            to_status=target,
            note=note,
        )
    )
    record(actor, "intervention.status_changed", obj)
    return obj


@transaction.atomic
def correct_note(*, actor, intervention_id, expected_version, note, effective_at):
    actor = policies.current_actor(actor, lock=True)
    obj = Intervention.objects.filter(pk=intervention_id).select_related("plan").first()
    if not obj:
        raise PermissionDenied
    case = locked(PatientCase.objects, obj.plan.case_id)
    policies.require_case(actor, case, "interventions.change_intervention")
    obj = locked(Intervention.objects, intervention_id)
    check_version(obj, expected_version)
    event = save_validated(
        InterventionEvent(
            intervention=obj,
            actor=actor,
            effective_at=effective_at,
            kind="correction",
            from_status=obj.status,
            to_status=obj.status,
            note=note,
        )
    )
    obj.version += 1
    obj.save(update_fields=["version"])
    record(actor, "intervention.note_corrected", obj)
    return event
