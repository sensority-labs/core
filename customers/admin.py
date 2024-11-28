from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from gettext import gettext as _
from customers.models import Customer, Bot, SSHKey


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    fieldsets = [
        (None, {"fields": ["email", "system_user_name", "password"]}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    ]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "system_user_name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    list_display = ["email", "system_user_name", "is_staff"]

    search_fields = ["email"]
    ordering = ["email"]


@admin.register(SSHKey)
class SSHKeyAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "key"]
    fields = ["name", "owner", "key"]
    readonly_fields = ["key"]


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "repo_url", "container_id"]
    fields = ["name", "owner", "repo_url", "container_id"]
    readonly_fields = ["repo_url", "container_id"]

    def repo_url(self, obj: Bot):
        owner = obj.owner
        return f"ssh://{owner.system_user_name}@localhost:2222/home/{owner.system_user_name}/repos/{obj.name}.git"
