import uuid
from django.db import models
from django.core.exceptions import ValidationError


class Entity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        # Safe in admin/log labels: never interpolate personal fields.
        return f"{self._meta.model_name}:{self.pk}"


class ImmutableRecord(Entity):
    """PostgreSQL triggers also protect updates/deletes, including QuerySet methods."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("Les événements historiques ne sont pas modifiables.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("La purge des historiques exige une procédure dédiée.")
