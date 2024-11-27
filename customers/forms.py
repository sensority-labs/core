from django import forms
from django.forms import ModelForm

from customers.models import SSHKey


# class SSHKeyForm(forms.Form):
#     ssh_public_key = forms.CharField(
#         widget=forms.Textarea, required=False, label="SSH Public Key"
#     )
#
#     def clean_ssh_public_key(self):
#         data = self.cleaned_data["ssh_public_key"]
#         if not data.startswith("ssh-rsa "):
#             raise forms.ValidationError("Invalid SSH public key")
#         return data


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
            raise forms.ValidationError("Invalid SSH public key")
        return data
