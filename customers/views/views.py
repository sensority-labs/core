from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import (
    HttpResponse,
    HttpRequest,
)


@login_required
@require_http_methods(["GET"])
def index(request: HttpRequest) -> HttpResponse:
    return redirect("bots_manager")
