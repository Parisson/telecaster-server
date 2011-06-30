from django import template
from django.utils.http import urlquote
from telecaster import models
from django.core.urlresolvers import reverse
from django.utils import html
from django import template
from django.utils.text import capfirst
from django.utils.translation import ungettext
#from docutils.core import publish_parts
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe
from django import db
from django.conf import settings

import re
import datetime

register = template.Library()

@register.filter
def len(list):
    return len(list)
