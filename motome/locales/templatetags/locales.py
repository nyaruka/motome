from django import template
from datetime import datetime
from django.utils import simplejson
from ..models import comma_formatted
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
import pytz

register = template.Library()

@register.filter
def local_timezone(value, format="%b %e %Y, %H:%M"):
    local = pytz.timezone(settings.USER_TIME_ZONE)
    value = value.replace(tzinfo=pytz.utc)
    return value.astimezone(local).strftime(format)

@register.filter
def format_int(value):
    try:
        value = int(value)
        return intcomma(value)
    except:
        return intcomma(value)

@register.filter
def format_currency(price, currency):
    if price is None or price == '':
        return "-"
    else:
        try:
            return currency.format(price)
        except:
            return price

@register.filter
def format_id(national_id, country):
    return country.format_id(national_id)

@register.filter
def format_phone(phone, country):
    return country.format_phone(phone)

    

