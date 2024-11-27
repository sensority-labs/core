import os

from customers.system.utils import is_docker


def add_ssh_key_to_authorized_keys(sys_user: str, key: str):
    if not is_docker():
        print(f"Add {key} to {sys_user}")
        return

    with open(f"/home/{sys_user}/.ssh/authorized_keys", "w") as f:
        f.write(key)
    return


def remove_ssh_key_from_authorized_keys(key_value: str, system_user_name: str) -> bool:
    if not is_docker():
        print(f"Remove {key_value} from {system_user_name}")
        return True

    user_home = os.path.join("/home", system_user_name)
    authorized_keys_path = os.path.join(user_home, ".ssh", "authorized_keys")

    if not os.path.exists(authorized_keys_path):
        return False

    with open(authorized_keys_path, "r") as auth_keys_file:
        lines = auth_keys_file.readlines()

    new_lines = []
    key_found = False
    for line in lines:
        if key_value.strip() not in line.strip():
            new_lines.append(line)
        else:
            key_found = True

    if key_found:
        with open(authorized_keys_path, "w") as auth_keys_file:
            auth_keys_file.writelines(new_lines)
        return True
    return False
