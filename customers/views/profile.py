from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
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


@login_required
@require_http_methods(["POST"])
def set_env_vars(request):
    if env_names := request.POST.getlist("env_name"):
        env_vars = dict()
        for name, value in zip(env_names, request.POST.getlist("env_value")):
            if name and value:
                env_vars[name] = value
        request.user.env_vars = env_vars
        request.user.save()
    return redirect("profile")
