import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponse, HttpRequest
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from customers.decorators import require_token
from customers.forms import BotForm, BotEnvVarsForm
from customers.models import Bot
from customers.system.git import create_new_repo, remove_repo
from customers.system.utils import BotMan

logger = logging.getLogger(__name__)


class ListBots(LoginRequiredMixin, ListView):
    model = Bot
    template_name = "customers/bots.html"

    def get_queryset(self):
        return Bot.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.request.user
        context["form"] = BotForm()
        return context


class CreateBot(LoginRequiredMixin, CreateView):
    model = Bot
    fields = ["name"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        create_new_repo(self.request.user.system_user_name, form.instance.name)
        return super().form_valid(form)

    def get_success_url(self):
        return redirect("bots_manager").url


class EditBot(LoginRequiredMixin, UpdateView):
    model = Bot
    fields = ["name"]
    template_name = "customers/bot.html"

    def post(self, request, *args, **kwargs):
        env_names = request.POST.getlist("env_name")
        if env_names:
            env_vars = dict()
            for name, value in zip(env_names, request.POST.getlist("env_value")):
                if name and value:
                    env_vars[name] = value
            bot = self.get_object()
            bot.env_vars = env_vars
            bot.save()
            return redirect("edit_bot", pk=self.get_object().pk)
        return redirect("edit_bot", pk=self.get_object().pk)

    def get_queryset(self):
        return Bot.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.request.user
        context["status"] = BotMan(self.object.container_id).status()
        return context

    def get_success_url(self):
        return redirect("bots_manager").url


class DeleteBot(LoginRequiredMixin, DeleteView):
    model = Bot

    def form_valid(self, form):
        bot = self.get_object()
        remove_repo(self.request.user.system_user_name, bot.name)
        if bot.container_id:
            BotMan(bot.container_id).remove()
        return super().form_valid(form)

    def get_success_url(self):
        return redirect("bots_manager").url


@login_required
def start_bot(request, pk):
    bot = get_object_or_404(Bot, owner=request.user, pk=pk)
    try:
        BotMan(container_id=bot.container_id).start()
    except Exception as e:
        logger.error(e)
        messages.error(request=request, message=f"Failed to start the bot: {e}")
    return redirect("edit_bot", pk=pk)


@login_required
def stop_bot(request, pk):
    bot = get_object_or_404(Bot, owner=request.user, pk=pk)
    try:
        BotMan(container_id=bot.container_id).stop()
    except Exception as e:
        logger.error(e)
        messages.error(request=request, message=f"Failed to stop the bot: {e}")
    return redirect("edit_bot", pk=pk)


@login_required
def recreate_bot(request, pk):
    bot = get_object_or_404(Bot, owner=request.user, pk=pk)
    try:
        new_container_id = BotMan(container_id=bot.container_id).recreate()
        bot.container_id = new_container_id
        bot.save()
    except Exception as e:
        logger.error(e)
        messages.error(request=request, message=f"Failed to recreate the bot: {e}")
    return redirect("edit_bot", pk=pk)


# Internal API
@csrf_exempt
@require_token
@require_http_methods(["GET"])
def get_bot_config(
    request: HttpRequest, system_user_name: str, bot_name: str
) -> HttpResponse:
    bot = get_object_or_404(
        Bot, owner__system_user_name=system_user_name, name=bot_name
    )
    envs: dict = bot.owner.env_vars
    envs.update(bot.env_vars)

    return HttpResponse(
        json.dumps(envs),
        content_type="application/json",
    )


@csrf_exempt
@require_token
@require_http_methods(["POST"])
def set_bot_container_id(request):
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
