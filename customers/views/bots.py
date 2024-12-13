import json

from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from customers.decorators import require_token
from customers.forms import BotForm
from customers.models import Bot
from customers.system.git import create_new_repo, remove_repo


class ListBots(ListView):
    model = Bot
    template_name = "customers/bots.html"

    def get_queryset(self):
        return Bot.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.request.user
        context["form"] = BotForm()
        return context


class CreateBot(CreateView):
    model = Bot
    fields = ["name"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        create_new_repo(self.request.user.system_user_name, form.instance.name)
        return super().form_valid(form)

    def get_success_url(self):
        return redirect("bots_manager").url


class EditBot(UpdateView):
    model = Bot
    fields = ["name"]
    template_name = "customers/bot.html"

    def get_queryset(self):
        return Bot.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.request.user
        return context

    def get_success_url(self):
        return redirect("bots_manager").url


class DeleteBot(DeleteView):
    model = Bot

    def form_valid(self, form):
        bot = self.get_object()
        remove_repo(self.request.user.system_user_name, bot.name)
        return super().form_valid(form)

    def get_success_url(self):
        return redirect("bots_manager").url


@csrf_exempt
@require_token
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
            Bot, owner__system_user_name=system_user_name, name=bot_name
        )
        print(watchman)
        watchman.container_id = container_id
        watchman.save()

        return HttpResponse("OK")

    except json.JSONDecodeError as e:
        print(e)
        return HttpResponseBadRequest("Invalid JSON")
