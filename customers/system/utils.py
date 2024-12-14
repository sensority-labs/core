import os
from http import HTTPStatus
from urllib.parse import urljoin

import requests
from django.conf import settings


def is_docker():
    return os.getenv("IS_DOCKER") == "true"


def clean_username(username: str):
    return username.replace("@", "_").replace(".", "_")


def get_bot_status(container_id: str):
    botStatusUrl = urljoin(settings.BOTMAN_URL, f"/{container_id}/status")
    response = requests.get(botStatusUrl)
    if response.status_code > HTTPStatus.OK:
        return "unknown"

    return response.json().get("status", "unknown")
