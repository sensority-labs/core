import os
import subprocess

OBSERVERS_GROUP = "observers"


def is_docker():
    return os.getenv("IS_DOCKER") == "true"


def clean_username(username: str):
    return username.replace("@", "_").replace(".", "_")


def add_git_user(username: str):
    if is_docker():
        subprocess.run(
            ["useradd", "-ms", "/usr/bin/git-shell", "-G", OBSERVERS_GROUP, username],
            check=True,
        )
        subprocess.run(["mkdir", "-p", f"/home/{username}/.ssh"], check=True)
        subprocess.run(["touch", f"/home/{username}/.ssh/authorized_keys"], check=True)
        subprocess.run(
            ["chown", "-R", f"{username}:{OBSERVERS_GROUP}", f"/home/{username}/.ssh"],
            check=True,
        )
        subprocess.run(["chmod", "700", f"/home/{username}/.ssh"], check=True)
        subprocess.run(
            ["chmod", "600", f"/home/{username}/.ssh/authorized_keys"], check=True
        )
        return
    print(f"Add {username}")


def add_ssh_key(username: str, key: str):
    if is_docker():
        with open(f"/home/{username}/.ssh/authorized_keys", "w") as f:
            f.write(key)
        return
    print(f"Add {key} to {username}")


def create_new_repo(username: str, repo_name: str):
    if is_docker():
        print(f"Create {username}/{repo_name}")
        # Make a directory
        subprocess.run(["mkdir", "-p", f"/home/{username}/repos"], check=True)
        # Initialize a git repository
        subprocess.run(
            ["git", "init", "--bare", f"/home/{username}/repos/{repo_name}.git"],
            check=True,
        )
        # Copy git hooks
        subprocess.run(
            [
                "cp",
                "-r",
                "/srv/git/hooks/.",
                f"/home/{username}/repos/{repo_name}.git/hooks",
            ],
            check=True,
        )
        # Change the owner of all files
        subprocess.run(
            ["chown", "-R", f"{username}:{OBSERVERS_GROUP}", f"/home/{username}/repos"],
            check=True,
        )
        return
    print(f"Create {username}/{repo_name}")
