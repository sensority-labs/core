import json
from typing import cast
from uuid import UUID

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import (
    HttpResponseBadRequest,
    HttpResponse,
    HttpRequest,
)

from customers.forms import SSHKeyForm
from customers.models import Watchman, SSHKey, Customer
from customers.system.ssh import (
    add_ssh_key_to_authorized_keys,
    remove_ssh_key_from_authorized_keys,
)


@login_required
@require_http_methods(["GET"])
def customer_info(request):
    return render(request, "customers/index.html", {"customer": request.user})


@login_required
@require_http_methods(["GET", "POST"])
def keys_manager(request: HttpRequest) -> HttpResponse:
    customer = cast(Customer, request.user)
    if request.method == "POST":
        form = SSHKeyForm(request.POST)
        if form.is_valid():
            add_ssh_key_to_authorized_keys(customer.system_user_name, form.instance.key)
            form.instance.owner = customer
            form.save()
            return redirect("keys_manager")
    else:
        form = SSHKeyForm(initial={"ssh_public_key": ""})

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
@require_http_methods(["GET", "POST"])
def bots_manager(request):
    customer = request.user
    return render(request, "customers/bots.html", {"customer": customer})


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
            Watchman, owner__system_user_name=system_user_name, name=bot_name
        )
        print(watchman)
        watchman.container_id = container_id
        watchman.save()

        return HttpResponse("OK")

    except json.JSONDecodeError as e:
        print(e)
        return HttpResponseBadRequest("Invalid JSON")
