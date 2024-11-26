import json

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import (
    HttpResponseRedirect,
    HttpResponseBadRequest,
    HttpResponse,
)
from django.urls import reverse

from customers.forms import SSHKeyForm
from customers.models import Watchman


@login_required
@require_http_methods(["GET", "POST"])
def customer_info(request):
    customer = request.user
    if request.method == "POST":
        form = SSHKeyForm(request.POST)
        if form.is_valid():
            customer.ssh_public_key = form.cleaned_data["ssh_public_key"]
            customer.save()
            return HttpResponseRedirect(reverse("customer_info"))
    else:
        form = SSHKeyForm(initial={"ssh_public_key": ""})

    return render(
        request, "customers/customer_info.html", {"customer": customer, "form": form}
    )


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
