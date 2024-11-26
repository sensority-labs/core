from django import forms


class SSHKeyForm(forms.Form):
    ssh_public_key = forms.CharField(
        widget=forms.Textarea, required=False, label="SSH Public Key"
    )

    def clean_ssh_public_key(self):
        data = self.cleaned_data["ssh_public_key"]
        if not data.startswith("ssh-rsa "):
            raise forms.ValidationError("Invalid SSH public key")
        return data
