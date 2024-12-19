from django import forms
from django.forms import ModelForm

from customers.models import SSHKey, Bot, FindingRoute


class SSHKeyForm(ModelForm):
    class Meta:
        model = SSHKey
        fields = ["name", "key"]
        labels = {"name": "Имя", "key": "Ключ"}
        help_texts = {"key": "Ключ должен начинаться с 'ssh-rsa'"}
        error_messages = {
            "key": {"invalid": "Invalid SSH public key"},
        }

    def clean_key(self):
        data = self.cleaned_data["key"]
        if not data.startswith("ssh-rsa "):
            raise forms.ValidationError(f"Invalid SSH public key: {data}")
        return data


class BotForm(ModelForm):
    class Meta:
        model = Bot
        fields = ["name"]
        labels = {"name": "Имя"}
        help_texts = {"name": "Имя бота"}


class BotEnvVarsForm(ModelForm):
    class Meta:
        model = Bot
        fields = ["env_vars"]
        labels = {"env_vars": "Переменные окружения"}
        help_texts = {"env_vars": "Переменные окружения бота"}


class RouteForm(ModelForm):
    class Meta:
        model = FindingRoute
        fields = [
            "bot",
            "alert_id",
            "channel_type",
            "telegram_bot_token",
            "telegram_chat_id",
            "webhook_url",
        ]
        labels = {
            "bot": "Бот",
            "alert_id": "ID Алерта",
            "channel_type": "Тип канала",
            "telegram_bot_token": "Токен бота",
            "telegram_chat_id": "ID чата",
            "webhook_url": "URL вебхука",
        }

    def __init__(self, *args, **kwargs):
        customer = kwargs.pop("customer", None)
        super(RouteForm, self).__init__(*args, **kwargs)
        if customer:
            self.fields["bot"].queryset = Bot.objects.filter(owner=customer)
