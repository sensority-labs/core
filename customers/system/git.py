import subprocess

from customers.system.utils import is_docker

OBSERVERS_GROUP = "observers"


def add_git_user(username: str):
    if not is_docker():
        print(f"Add {username}")
        return

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


def create_new_repo(username: str, repo_name: str):
    if not is_docker():
        print(f"Create {username}/{repo_name}")
        return

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


def remove_repo(username: str, repo_name: str):
    if not is_docker():
        print(f"Remove {username}/{repo_name}")
        return

    # Remove the directory
    subprocess.run(["rm", "-rf", f"/home/{username}/repos/{repo_name}.git"], check=True)
    return
