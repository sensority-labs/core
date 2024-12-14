import enum

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from customers.managers import CustomUserManager
from customers.system.utils import (
    clean_username,
)
from customers.system.git import add_git_user, create_new_repo
from shared.models import Dated, UUIDed


class Customer(Dated, UUIDed, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("Email"), unique=True, db_index=True)
    system_user_name = models.CharField(
        _("Имя пользователя GIT"), max_length=255, blank=True
    )
    is_staff = models.BooleanField(_("Staff"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    date_joined = models.DateTimeField(_("Joined at"), default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.system_user_name:
            self.system_user_name = clean_username(self.email)
        if self._state.adding and not self.is_staff:
            # Create git user
            add_git_user(self.system_user_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class SSHKey(Dated, UUIDed):
    name = models.CharField(_("Key name"), max_length=255, blank=True)
    key = models.CharField(_("Key content"), max_length=4096)
    owner = models.ForeignKey(
        Customer,
        verbose_name=_("Owner"),
        related_name="ssh_keys",
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        if not self.name:
            # Try to cut the key by spaces to get the name. If it fails, left it empty
            try:
                self.name = self.key.split(" ")[2]
            except IndexError:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.owner.email}/{self.key[:20]}"


class Bot(Dated, UUIDed):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"], name="unique_owner_bot_name"
            ),
        ]

    name = models.CharField(_("Name"), max_length=255)
    owner = models.ForeignKey(
        Customer,
        verbose_name=_("Customer"),
        related_name="bots",
        on_delete=models.CASCADE,
    )
    container_id = models.CharField(_("Container ID"), max_length=255, blank=True)

    @property
    def repo_url(self):
        return f"ssh://{self.owner.system_user_name}@{settings.GIT_SERVER_ADDRESS}/home/{self.owner.system_user_name}/repos/{self.name}.git"

    def __str__(self):
        return f"{self.owner.email}/{self.name}"


class ChannelType(enum.IntEnum):
    Telegram = 0
    Webhook = 1


class FindingRoute(Dated, UUIDed):
    customer = models.ForeignKey(
        Customer,
        verbose_name=_("Customer"),
        related_name="routes",
        on_delete=models.CASCADE,
    )
    bot = models.ForeignKey(
        Bot, verbose_name=_("Bot"), related_name="routes", on_delete=models.CASCADE
    )
    alert_id = models.CharField(_("Alert ID"), max_length=255)

    channel_type = models.IntegerField(
        verbose_name=_("Feedback channel type"),
        choices=[(tag, tag.name) for tag in ChannelType],
    )
    telegram_bot_token = models.CharField(
        _("Telegram bot token"), max_length=255, blank=True
    )
    telegram_chat_id = models.CharField(
        _("Telegram chat ID"), max_length=255, blank=True
    )
    webhook_url = models.URLField(_("Webhook URL"), blank=True)
