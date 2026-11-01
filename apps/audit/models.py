from django.conf import settings
from django.db import models
from apps.common.models import ImmutableRecord


class AuditEvent(ImmutableRecord):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT
    )
    action = models.CharField(max_length=64)
    target_type = models.CharField(max_length=40)
    target_id = models.UUIDField()
    result = models.CharField(max_length=16, default="success")

    class Meta:
        indexes = [models.Index(fields=["target_id", "created_at"])]
