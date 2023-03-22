from django import template

register = template.Library()

@register.filter
def addspaces(value):
    value=str(value)
    return value.replace(" ","_")