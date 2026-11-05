from django import template
register = template.Library()
@register.filter
def get(d, k): return d.get(k, 0)
