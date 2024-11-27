import os


def is_docker():
    return os.getenv("IS_DOCKER") == "true"


def clean_username(username: str):
    return username.replace("@", "_").replace(".", "_")
