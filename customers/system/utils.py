import enum
import logging
import os
from dataclasses import dataclass
from http import HTTPStatus
from urllib.parse import urljoin

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


def is_docker():
    return os.getenv("IS_DOCKER") == "true"


def clean_username(username: str):
    return username.replace("@", "_").replace(".", "_")


class BotmanAction(enum.Enum):
    START = "start"
    STOP = "stop"
    REMOVE = "remove"
    REBUILD = "rebuild"
    GET_STATUS = "status"


class BotStatus(enum.Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    EXITED = "exited"
    DEAD = "dead"
    UNKNOWN = "unknown"


class BotmanError(Exception):
    pass


@dataclass
class BotMan:
    """
    Manages interactions with the Botman service to control bot instances.

    Provides a high-level interface for starting, stopping, removing, rebuilding,
    and retrieving the status of bot containers managed by the Botman service.

    :ivar container_id: Identifier of the container managed by the Botman service.
    :type container_id: str
    :ivar botman_url: Base URL of the Botman service. Defaults to the value in settings.BOTMAN_URL.
    :type botman_url: str
    """

    container_id: str
    botman_url: str = settings.BOTMAN_URL

    def _request(self, action: BotmanAction) -> bool | dict:
        url = urljoin(self.botman_url, f"/{self.container_id}/{action.value}")
        logger.info(f"Botman request: {url}")
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            logger.error(f"Botman request error: {str(e)}")
            raise BotmanError(str(e))

        if response.status_code != HTTPStatus.OK:
            msg = f"Botman error: {response.text}"
            logger.error(f"Botman non 200 response: {msg}")
            raise BotmanError(msg)

        try:
            return response.json()
        except ValueError:
            return True

    def start(self):
        return self._request(BotmanAction.START)

    def stop(self):
        return self._request(BotmanAction.STOP)

    def remove(self):
        return self._request(BotmanAction.REMOVE)

    def rebuild(self):
        return self._request(BotmanAction.REBUILD)

    def status(self):
        try:
            bot_status_response = self._request(BotmanAction.GET_STATUS)
            bot_status = bot_status_response.get("status", BotStatus.UNKNOWN)
            return BotStatus(bot_status).value
        except BotmanError:
            return BotStatus.UNKNOWN.value
