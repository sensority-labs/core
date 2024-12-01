from functools import wraps

from django.conf import settings
from django.http import JsonResponse


def require_token(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        api_key = request.GET.get("token") or request.headers.get("X-Token")
        if not settings.DEBUG and api_key != settings.API_ACCESS_TOKEN:
            return JsonResponse({"error": "Unauthorized access"}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapped_view
