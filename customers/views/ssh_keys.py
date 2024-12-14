from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.generic import CreateView, DeleteView

from customers.forms import SSHKeyForm
from customers.models import SSHKey


class CreateSSHKeyView(LoginRequiredMixin, CreateView):
    model = SSHKey
    form_class = SSHKeyForm
    template_name = "customers/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.request.user
        return context

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        key = form.clean_key()
        if not key.startswith("ssh-rsa "):
            raise ValidationError(f"Invalid SSH public key: {key}")

        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return redirect("profile").url


class DeleteSSHKeyView(LoginRequiredMixin, DeleteView):
    model = SSHKey

    def get_queryset(self):
        return SSHKey.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return redirect("profile").url
