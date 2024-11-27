from django.urls import path

from customers.views import (
    set_bot_container_id,
    keys_manager,
    bots_manager,
    delete_ssh_key,
)

urlpatterns = [
    path("", bots_manager, name="bots_manager"),
    path("keys/", keys_manager, name="keys_manager"),
    path("keys/<uuid:key_uid>/delete/", delete_ssh_key, name="delete_ssh_key"),
    path("set-bot-container-id/", set_bot_container_id, name="set_bot_container_id"),
]
