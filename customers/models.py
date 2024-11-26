from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from customers.managers import CustomUserManager
from customers.system.utils import (
    add_git_user,
    add_ssh_key,
    create_new_repo,
    clean_username,
)
from shared.models import Dated, UUIDed


class Customer(Dated, UUIDed, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("Адрес email"), unique=True, db_index=True)
    system_user_name = models.CharField(
        _("Имя пользователя GIT"), max_length=255, blank=True
    )
    is_staff = models.BooleanField(_("Сотрудник"), default=False)
    is_active = models.BooleanField(_("Активен"), default=True)
    date_joined = models.DateTimeField(_("Дата регистрации"), default=timezone.now)

    ssh_public_key = models.CharField(
        _("Ключ SSH"), max_length=4096, blank=True, null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.system_user_name:
            self.system_user_name = clean_username(self.email)
        if self._state.adding and not self.is_staff:
            # Create git user
            add_git_user(self.system_user_name)

        if self.ssh_public_key:
            add_ssh_key(self.system_user_name, self.ssh_public_key)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class Watchman(Dated, UUIDed):
    name = models.CharField(_("Имя"), max_length=255)
    owner = models.ForeignKey(
        Customer, verbose_name=_("Клиент"), on_delete=models.CASCADE
    )
    container_id = models.CharField(_("ID контейнера"), max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            # Create a new repo
            create_new_repo(self.owner.system_user_name, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.owner.email}/{self.name}"
