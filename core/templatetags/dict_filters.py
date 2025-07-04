from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    return d.get(key)

@register.filter
def get_status_code(status_list, status_name):
    for code, name in status_list:
        if name == status_name:
            return code
    return ''