import json
from typing import cast
from uuid import UUID

from django.contrib import messages
from django.forms.models import model_to_dict
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import (
    HttpResponseBadRequest,
    HttpResponse,
    HttpRequest,
    JsonResponse,
)

from customers.forms import SSHKeyForm, BotForm, RouteForm
from customers.models import Bot, SSHKey, Customer, FindingRoute
from customers.system.git import create_new_repo, remove_repo
from customers.system.ssh import (
    add_ssh_key_to_authorized_keys,
    remove_ssh_key_from_authorized_keys,
)


@login_required
@require_http_methods(["GET"])
def index(request: HttpRequest) -> HttpResponse:
    return redirect("bots_manager")


@login_required
@require_http_methods(["GET", "POST"])
def keys_manager(request: HttpRequest) -> HttpResponse:
    customer = cast(Customer, request.user)
    if request.method == "POST":
        form = SSHKeyForm(request.POST)
        if form.is_valid():
            ssh_key = form.save(commit=False)
            ssh_key.owner = request.user
            add_ssh_key_to_authorized_keys(customer.system_user_name, ssh_key.key)
            ssh_key.save()
            messages.success(request, "SSH Key added successfully.")
            return redirect("keys_manager")
    else:
        form = SSHKeyForm()

    return render(request, "customers/keys.html", {"customer": customer, "form": form})


@login_required
@require_http_methods(["POST"])
def delete_ssh_key(request: HttpRequest, key_uid: UUID) -> HttpResponse:
    ssh_key = get_object_or_404(SSHKey, uid=key_uid, owner=request.user)

    result = remove_ssh_key_from_authorized_keys(
        ssh_key.key, ssh_key.owner.system_user_name
    )

    if result is True:
        ssh_key.delete()
        messages.success(request, "SSH Key deleted successfully.")
    else:
        messages.error(request, "SSH Key not found in authorized_keys.")

    return redirect("keys_manager")


@login_required
@require_http_methods(["POST"])
def delete_bot(request: HttpRequest, bot_uid: UUID) -> HttpResponse:
    bot = get_object_or_404(Bot, uid=bot_uid, owner=request.user)

    remove_repo(bot.owner.system_user_name, bot.name)
    bot.delete()

    messages.success(request, f"Bot {bot.name} deleted successfully.")
    return redirect("bots_manager")


@login_required
@require_http_methods(["GET", "POST"])
def bots_manager(request):
    customer = cast(Customer, request.user)
    if request.method == "POST":
        form = BotForm(request.POST)
        if form.is_valid():
            bot = form.save(commit=False)
            bot.owner = request.user
            create_new_repo(customer.system_user_name, bot.name)
            bot.save()
            messages.success(request, "Bot added successfully.")
            return redirect("bots_manager")
    else:
        form = BotForm()
    return render(request, "customers/bots.html", {"customer": customer, "form": form})


@login_required
@require_http_methods(["GET", "POST"])
def routes_manager(request: HttpRequest) -> HttpResponse:
    customer = cast(Customer, request.user)
    if request.method == "POST":
        bot = get_object_or_404(Bot, owner=customer, uid=request.POST["bot"])
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.customer = customer
            route.bot = bot
            route.save()
            messages.success(request, "Route added successfully.")
            return redirect("routes_manager")
    else:
        form = RouteForm()
    return render(
        request,
        "customers/routes.html",
        {"routes": customer.routes.all(), "form": form},
    )


@login_required
@require_http_methods(["GET", "POST"])
def edit_route(request: HttpRequest, route_uid: UUID) -> HttpResponse:
    route = get_object_or_404(FindingRoute, uid=route_uid, customer=request.user)
    if request.method == "POST":
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, "Route updated successfully.")
            return redirect("routes_manager")
    else:
        form = RouteForm(instance=route)
    return render(request, "customers/route_edit.html", {"route": route, "form": form})


@login_required
@require_http_methods(["POST"])
def delete_route(request: HttpRequest, route_uid: UUID) -> HttpResponse:
    route = get_object_or_404(FindingRoute, uid=route_uid, customer=request.user)
    route.delete()
    messages.success(request, "Route deleted successfully.")
    return redirect("routes_manager")


@csrf_exempt
@require_http_methods(["POST"])
def set_bot_container_id(request):
    print("=== set_bot_container_id ===")
    print(request.body)
    print("=== set_bot_container_id ===")
    try:
        data = json.loads(request.body)
        system_user_name = data.get("system_user_name")
        bot_name = data.get("bot_name")
        container_id = data.get("container_id")

        print(system_user_name, bot_name, container_id)
        if not all([system_user_name, bot_name, container_id]):
            return HttpResponseBadRequest("Missing required fields")

        watchman = get_object_or_404(
            Bot, owner__system_user_name=system_user_name, name=bot_name
        )
        print(watchman)
        watchman.container_id = container_id
        watchman.save()

        return HttpResponse("OK")

    except json.JSONDecodeError as e:
        print(e)
        return HttpResponseBadRequest("Invalid JSON")


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
