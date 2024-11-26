from django.urls import path

from customers.views import customer_info, set_bot_container_id

urlpatterns = [
    path("", customer_info, name="customer_info"),
    path("set-bot-container-id/", set_bot_container_id, name="set_bot_container_id"),
]
