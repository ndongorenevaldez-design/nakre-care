from django.conf import settings
from django.db import models
from django.db.models import F, Q
from apps.common.models import Entity, ImmutableRecord


class StaffMember(Entity):
    display_name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT
    )


class Intervention(Entity):
    class Status(models.TextChoices):
        PLANNED = "planned", "Prévue"
        DONE = "done", "Effectuée"
        CANCELLED = "cancelled", "Annulée"

    plan = models.ForeignKey(
        "patients.CarePlan", on_delete=models.PROTECT, related_name="interventions"
    )
    staff = models.ForeignKey(StaffMember, on_delete=models.PROTECT)
    service = models.ForeignKey("intake.ServiceType", on_delete=models.PROTECT)
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status, default=Status.PLANNED)
    version = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["plan", "scheduled_start"]),
            models.Index(fields=["staff", "scheduled_start"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=["planned", "done", "cancelled"]),
                name="intervention_valid_status",
            ),
            models.CheckConstraint(
                condition=Q(scheduled_end__gt=F("scheduled_start")),
                name="intervention_schedule_order",
            ),
            models.CheckConstraint(
                condition=Q(actual_start__isnull=True, actual_end__isnull=True)
                | Q(
                    actual_start__isnull=False,
                    actual_end__isnull=False,
                    actual_end__gte=F("actual_start"),
                ),
                name="intervention_actual_pair",
            ),
            models.CheckConstraint(
                condition=~Q(status="done")
                | Q(actual_start__isnull=False, actual_end__isnull=False),
                name="intervention_done_dates",
            ),
        ]


class InterventionEvent(ImmutableRecord):
    intervention = models.ForeignKey(
        Intervention, on_delete=models.PROTECT, related_name="events"
    )
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    effective_at = models.DateTimeField()
    kind = models.CharField(
        max_length=24,
        choices=[
            ("scheduled", "Planification"),
            ("transition", "Transition"),
            ("correction", "Correction"),
        ],
    )
    from_status = models.CharField(max_length=12, blank=True)
    to_status = models.CharField(max_length=12)
    note = models.CharField(max_length=500, blank=True)
