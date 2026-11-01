from django.conf import settings
from django.db import models
from django.db.models import Q, F
from apps.common.models import Entity


class PatientCase(Entity):
    class Status(models.TextChoices):
        ACTIVE = "active", "Actif"
        SUSPENDED = "suspended", "Suspendu"
        CLOSED = "closed", "Clos"

    request = models.OneToOneField(
        "intake.CareRequest", on_delete=models.PROTECT, related_name="patient_case"
    )
    status = models.CharField(max_length=12, choices=Status, default=Status.ACTIVE)
    version = models.PositiveIntegerField(default=0)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = [("assign_case", "Affecter un dossier")]
        indexes = [models.Index(fields=["status", "created_at"])]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=["active", "suspended", "closed"]),
                name="case_valid_status",
            ),
            models.CheckConstraint(
                condition=Q(status="closed", closed_at__isnull=False)
                | (~Q(status="closed") & Q(closed_at__isnull=True)),
                name="case_closed_timestamp",
            ),
        ]


class CaseAssignment(Entity):
    case = models.ForeignKey(
        PatientCase, on_delete=models.PROTECT, related_name="assignments"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
    can_manage = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["case", "user"],
                condition=Q(active=True),
                name="case_active_assignee_unique",
            )
        ]
        indexes = [models.Index(fields=["user", "active"])]


class AuthorizedContact(Entity):
    case = models.ForeignKey(
        PatientCase, on_delete=models.PROTECT, related_name="authorized_contacts"
    )
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=32)
    relationship = models.CharField(max_length=80)
    scope = models.CharField(max_length=250)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    verified_at = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(valid_until__isnull=True)
                | Q(valid_until__gte=F("verified_at")),
                name="contact_valid_period",
            )
        ]


class CarePlan(Entity):
    case = models.ForeignKey(
        PatientCase, on_delete=models.PROTECT, related_name="plans"
    )
    version = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    starts_on = models.DateField()
    ends_on = models.DateField(null=True, blank=True)
    frequency = models.CharField(max_length=250)
    services = models.ManyToManyField("intake.ServiceType", through="PlanService")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["case", "version"], name="plan_case_version_unique"
            ),
            models.UniqueConstraint(
                fields=["case"],
                condition=Q(active=True),
                name="plan_one_active_per_case",
            ),
            models.CheckConstraint(
                condition=Q(version__gte=1), name="plan_positive_version"
            ),
            models.CheckConstraint(
                condition=Q(ends_on__isnull=True) | Q(ends_on__gte=F("starts_on")),
                name="plan_dates_order",
            ),
        ]


class PlanService(Entity):
    plan = models.ForeignKey(CarePlan, on_delete=models.CASCADE)
    service = models.ForeignKey("intake.ServiceType", on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["plan", "service"], name="plan_service_unique"
            )
        ]
