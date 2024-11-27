from django.urls import path

from customers.views import (
    customer_info,
    set_bot_container_id,
    keys_manager,
    bots_manager,
    delete_ssh_key,
)

urlpatterns = [
    path("", customer_info, name="customer_info"),
    path("keys/", keys_manager, name="keys_manager"),
    path("keys/<uuid:key_uid>/delete/", delete_ssh_key, name="delete_ssh_key"),
    path("bots/", bots_manager, name="bots_manager"),
    path("set-bot-container-id/", set_bot_container_id, name="set_bot_container_id"),
]
