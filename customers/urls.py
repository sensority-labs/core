from django.urls import path

from customers.views.profile import ProfileView
from customers.views.ssh_keys import CreateSSHKeyView, DeleteSSHKeyView
from customers.views.views import (
    index,
)
from customers.views.routes import (
    get_route,
    RoutesList,
    CreateRoute,
    EditRoute,
    DeleteRoute,
)
from customers.views.bots import (
    ListBots,
    CreateBot,
    EditBot,
    DeleteBot,
    set_bot_container_id,
    start_bot,
    stop_bot,
    rebuild_bot,
)


urlpatterns = [
    path("", index, name="customers_index"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("keys/new", CreateSSHKeyView.as_view(), name="create_ssh_key"),
    path("keys/<uuid:pk>/delete/", DeleteSSHKeyView.as_view(), name="delete_ssh_key"),
    path("bots/", ListBots.as_view(), name="bots_manager"),
    path("bots/new", CreateBot.as_view(), name="new_bot"),
    path("bots/<uuid:pk>/", EditBot.as_view(), name="edit_bot"),
    path("bots/<uuid:pk>/delete/", DeleteBot.as_view(), name="delete_bot"),
    path("bots/<uuid:pk>/start/", start_bot, name="start_bot"),
    path("bots/<uuid:pk>/stop/", stop_bot, name="stop_bot"),
    path("bots/<uuid:pk>/rebuild/", rebuild_bot, name="rebuild_bot"),
    path("routes/", RoutesList.as_view(), name="routes_manager"),
    path("routes/new", CreateRoute.as_view(), name="new_route"),
    path("routes/<uuid:pk>/", EditRoute.as_view(), name="edit_route"),
    path("routes/<uuid:pk>/delete/", DeleteRoute.as_view(), name="delete_route"),
    # Internal routes
    path(
        "get-route/<str:system_user_name>/<str:bot_name>/<str:alert_id>/",
        get_route,
        name="get_route",
    ),
    path("set-bot-container-id/", set_bot_container_id, name="set_bot_container_id"),
]
