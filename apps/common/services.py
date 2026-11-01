from django.core.exceptions import ValidationError, PermissionDenied
from apps.audit.models import AuditEvent
from apps.notifications.models import NotificationOutbox


class Conflict(ValidationError):
    """Stale version or incompatible state: callers must reload, not overwrite."""


def check_version(obj, expected):
    if obj.version != expected:
        raise Conflict("La version a changé ; rechargez les données.")


def save_validated(obj):
    obj.full_clean()
    obj.save()
    return obj


def record(actor, action, obj):
    return AuditEvent.objects.create(
        actor=actor, action=action, target_type=obj._meta.model_name, target_id=obj.pk
    )


def queue_blocked(event, obj):
    for channel in ("email", "whatsapp"):
        NotificationOutbox.objects.get_or_create(
            deduplication_key=f"{event}:{obj.pk}:{channel}",
            defaults={"event_type": event, "target_id": obj.pk, "channel": channel},
        )


def locked(query, pk):
    # Same denial for missing IDs and invalid object access. No public lookup by reference.
    try:
        obj = query.select_for_update().filter(pk=pk).first()
    except (ValidationError, ValueError):
        obj = None
    if obj is None:
        raise PermissionDenied
    return obj
