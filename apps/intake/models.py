import secrets
from django.conf import settings
from django.db import models
from django.db.models import Q
from apps.common.models import Entity, ImmutableRecord


def new_reference():
    return secrets.token_hex(16)


class ServiceType(Entity):
    code = models.SlugField(max_length=40, unique=True)
    label = models.CharField(max_length=120)
    active = models.BooleanField(default=True)


class CareRequest(Entity):
    class Status(models.TextChoices):
        NEW = "new", "Nouvelle"
        REVIEW = "review", "En évaluation"
        ACCEPTED = "accepted", "Acceptée"
        REFUSED = "refused", "Refusée"
        CANCELLED = "cancelled", "Annulée"

    reference = models.CharField(
        max_length=32, default=new_reference, unique=True, editable=False
    )
    status = models.CharField(max_length=12, choices=Status, default=Status.NEW)
    version = models.PositiveIntegerField(default=0)
    requester_name = models.CharField(max_length=120)
    requester_phone = models.CharField(max_length=32)
    requester_email = models.EmailField(blank=True)
    relationship = models.CharField(max_length=80)
    beneficiary_name = models.CharField(max_length=120)
    beneficiary_age = models.PositiveSmallIntegerField(null=True, blank=True)
    city = models.CharField(max_length=80)
    intervention_address = models.CharField(max_length=250, blank=True)
    context = models.CharField(max_length=1000, blank=True)
    desired_start = models.DateField(null=True, blank=True)
    availability = models.CharField(max_length=250, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    # Declared contact stays unverified; never automatically copied as authorized.
    proposed_contact_name = models.CharField(max_length=120, blank=True)
    proposed_contact_phone = models.CharField(max_length=32, blank=True)
    services = models.ManyToManyField(ServiceType, through="RequestedService")

    class Meta:
        permissions = [
            ("triage_unassigned", "Traiter la file non affectée"),
            ("assign_request", "Affecter une demande"),
        ]
        indexes = [models.Index(fields=["status", "created_at"])]
        constraints = [
            models.CheckConstraint(
                condition=Q(
                    status__in=["new", "review", "accepted", "refused", "cancelled"]
                ),
                name="request_valid_status",
            ),
            models.CheckConstraint(
                condition=Q(beneficiary_age__isnull=True) | Q(beneficiary_age__lte=120),
                name="request_age_range",
            ),
            models.CheckConstraint(
                condition=Q(latitude__isnull=True, longitude__isnull=True)
                | Q(
                    latitude__isnull=False,
                    longitude__isnull=False,
                    latitude__gte=-90,
                    latitude__lte=90,
                    longitude__gte=-180,
                    longitude__lte=180,
                ),
                name="request_coordinates_pair",
            ),
        ]


class RequestedService(Entity):
    request = models.ForeignKey(CareRequest, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceType, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["request", "service"], name="request_service_unique"
            )
        ]


class ConsentRecord(ImmutableRecord):
    request = models.ForeignKey(
        CareRequest, on_delete=models.PROTECT, related_name="consents"
    )
    purpose = models.CharField(max_length=80)
    notice_version = models.CharField(max_length=40)
    legal_basis = models.CharField(max_length=120)
    declarant_capacity = models.CharField(max_length=120)
    agreed = models.BooleanField(null=True, blank=True)
    # No preselected legal basis: callers must provide a reviewed declaration.


class RequestAssignment(Entity):
    request = models.ForeignKey(
        CareRequest, on_delete=models.PROTECT, related_name="assignments"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
    can_process = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["request", "user"], name="request_assignee_unique"
            )
        ]
        indexes = [models.Index(fields=["user", "active"])]


class RequestReview(ImmutableRecord):
    request = models.ForeignKey(
        CareRequest, on_delete=models.PROTECT, related_name="reviews"
    )
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    from_status = models.CharField(max_length=12, choices=CareRequest.Status)
    to_status = models.CharField(max_length=12, choices=CareRequest.Status)
    orientation = models.CharField(max_length=500, blank=True)
    # A minimal internal evaluation, separate from the audit log.
