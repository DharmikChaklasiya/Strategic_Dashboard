from django import template

register = template.Library()

@register.filter
def addspaces(value):
    value=str(value)
    if '/' in value:
        value=value.replace("/",'')
    if '\\' in value:
        value=value.replace('\\','')
    if '.' in value:
        value=value.replace('.','')
    return value.replace(" ","_")