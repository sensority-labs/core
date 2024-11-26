import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# Create your models here.
class UUIDed(models.Model):
    class Meta:
        abstract = True

    uid = models.UUIDField(
        _("UID"), primary_key=True, default=uuid.uuid4, editable=False
    )


class Dated(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        _("Создано"), default=timezone.now, editable=False
    )
    updated_at = models.DateTimeField(_("Обновлено"), default=timezone.now)


class CreatedBy(models.Model):
    class Meta:
        abstract = True

    created_by = models.ForeignKey(
        "customers.Customer",
        verbose_name=_("Кем создано"),
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
    )
