from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from customers.decorators import require_token
from customers.forms import RouteForm
from customers.models import FindingRoute


class RoutesList(LoginRequiredMixin, ListView):
    model = FindingRoute
    template_name = "customers/routes.html"

    def get_queryset(self):
        return FindingRoute.objects.filter(customer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = RouteForm(customer=self.request.user)
        return context


class CreateRoute(LoginRequiredMixin, CreateView):
    model = FindingRoute
    fields = [
        "bot",
        "alert_id",
        "channel_type",
        "telegram_bot_token",
        "telegram_chat_id",
        "webhook_url",
    ]

    def form_valid(self, form):
        form.instance.customer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return redirect("routes_manager").url


class EditRoute(LoginRequiredMixin, UpdateView):
    model = FindingRoute
    fields = [
        "bot",
        "alert_id",
        "channel_type",
        "telegram_bot_token",
        "telegram_chat_id",
        "webhook_url",
    ]
    template_name = "customers/route_edit.html"

    def get_queryset(self):
        return FindingRoute.objects.filter(customer=self.request.user)

    def get_success_url(self):
        return redirect("routes_manager").url


class DeleteRoute(LoginRequiredMixin, DeleteView):
    model = FindingRoute

    def get_queryset(self):
        return FindingRoute.objects.filter(customer=self.request.user)

    def get_success_url(self):
        return redirect("routes_manager").url


@require_token
@require_http_methods(["GET"])
def get_route(
    request: HttpRequest, system_user_name: str, bot_name: str, alert_id: str
) -> JsonResponse:
    route = get_object_or_404(
        FindingRoute,
        customer__system_user_name=system_user_name,
        bot__name=bot_name,
        alert_id=alert_id,
    )
    return JsonResponse({"route": model_to_dict(route)})
