
import re

from django import template
register = template.Library()

# Adapted from http://gnuvince.wordpress.com/2007/09/14/a-django-template-for-the-current-active-page/
@register.simple_tag
def active(request, pattern):
  if re.search(pattern, request.path):
    return 'active'
  return ''
