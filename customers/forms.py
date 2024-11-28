from django import forms
from django.forms import ModelForm

from customers.models import SSHKey, Bot


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
