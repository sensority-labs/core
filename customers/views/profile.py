from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView

from customers.forms import SSHKeyForm
from customers.models import Customer


class ProfileView(LoginRequiredMixin, UpdateView):
    model = Customer
    fields = ["email"]
    template_name = "customers/profile.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SSHKeyForm()
        return context
