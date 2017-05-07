from django import template

register = template.Library()

@register.filter(name='keyColor')


def keyColor(value):
    if value[:2] == 'no':
        return True
    else:
        return False

