import json

import pytest
from django.http import JsonResponse
from django.test import RequestFactory
from customers.decorators import require_token


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def view():
    return require_token(lambda request: JsonResponse({"success": True}))


def test_require_token_allows_access_with_valid_token(factory, view, settings):
    settings.API_ACCESS_TOKEN = "valid_token"
    request = factory.get("/some-url", {"token": "valid_token"})

    response = view(request)
    response_content = response.content
    response_dict = json.loads(response_content.decode("utf-8"))

    assert response.status_code == 200
    assert response_dict == {"success": True}


def test_require_token_denies_access_with_invalid_token(factory, view, settings):
    settings.API_ACCESS_TOKEN = "valid_token"
    request = factory.get("/some-url", {"token": "invalid_token"})

    response = view(request)
    response_content = response.content
    response_dict = json.loads(response_content.decode("utf-8"))

    assert response.status_code == 401
    assert response_dict == {"error": "Unauthorized access"}


def test_require_token_allows_access_in_debug_mode(factory, view, settings):
    settings.DEBUG = True
    request = factory.get("/some-url")

    response = view(request)
    response_content = response.content
    response_dict = json.loads(response_content.decode("utf-8"))

    assert response.status_code == 200
    assert response_dict == {"success": True}


def test_require_token_denies_access_without_token(factory, view, settings):
    settings.DEBUG = False
    settings.API_ACCESS_TOKEN = "valid_token"
    request = factory.get("/some-url")

    response = view(request)
    response_content = response.content
    response_dict = json.loads(response_content.decode("utf-8"))

    assert response.status_code == 401
    assert response_dict == {"error": "Unauthorized access"}
