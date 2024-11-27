from django import template

register = template.Library()


@register.filter(name="shorten_ssh_key")
def shorten_ssh_key(value):
    parts = value.split(" ")
    if len(parts) >= 3:
        key_part_1 = parts[0]  # Берём первую часть ключа
        key_part_2 = parts[1]  # Берём вторую часть ключа
        return f"{key_part_1} {key_part_2[:20]}...{key_part_2[-20:]}"
    return value
