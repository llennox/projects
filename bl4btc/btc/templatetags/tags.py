from decimal import *
from django import template

register = template.Library()

@register.filter(name='div')
def div(numerator, denominator):
    x = float(numerator)/float(denominator)
    x = x * 1000
    x = round(x,6)
    return x

@register.filter(name='mul')
def mul(numerator, denominator):
    x = float(numerator) * float(denominator)
    x = round(x,6)
    return x
