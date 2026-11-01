from django.db import models
from apps.common.models import Entity, ImmutableRecord


class NotificationOutbox(Entity):
    deduplication_key = models.CharField(max_length=150, unique=True)
    event_type = models.CharField(max_length=64)
    target_id = models.UUIDField()
    channel = models.CharField(
        max_length=12, choices=[("email", "E-mail"), ("whatsapp", "WhatsApp")]
    )
    # No real destination or message body until the notification lot is authorized.
    destination_alias = models.CharField(max_length=40, default="administration")
    status = models.CharField(
        max_length=24,
        default="blocked",
        choices=[
            ("blocked", "Non configuré"),
            ("queued", "En attente"),
            ("processing", "En cours"),
            ("provider_accepted", "Accepté fournisseur"),
            ("delivered", "Livré"),
            ("failed", "Échec"),
            ("dead_letter", "Abandonné"),
            ("delivery_unknown", "Inconnu"),
        ],
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    lease_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["status", "scheduled_at"])]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "blocked",
                        "queued",
                        "processing",
                        "provider_accepted",
                        "delivered",
                        "failed",
                        "dead_letter",
                        "delivery_unknown",
                    ]
                ),
                name="outbox_valid_status",
            )
        ]


class NotificationAttempt(ImmutableRecord):
    outbox = models.ForeignKey(
        NotificationOutbox, on_delete=models.PROTECT, related_name="attempts"
    )
    number = models.PositiveIntegerField()
    status = models.CharField(
        max_length=24,
        choices=[
            ("failed", "Échec"),
            ("provider_accepted", "Accepté"),
            ("delivery_unknown", "Inconnu"),
        ],
    )
    error_code = models.CharField(max_length=64, blank=True)
    provider_id = models.CharField(max_length=120, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["outbox", "number"], name="notification_attempt_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(number__gte=1), name="notification_attempt_positive"
            ),
        ]
