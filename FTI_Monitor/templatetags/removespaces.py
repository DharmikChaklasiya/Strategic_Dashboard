from django import template

register = template.Library()

@register.filter
def removespaces(value):
    value=str(value)
    return value.replace("_"," ")
