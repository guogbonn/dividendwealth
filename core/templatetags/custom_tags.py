from django import template
from django.template.defaultfilters import stringfilter
import string
import re
import json
from core.models import (UserRelationship
)

register = template.Library()

@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)

@register.filter
@stringfilter
def upto(value, delimiter=None):
    return value.split(delimiter)[0]
# upto.is_safe = True

# https://stackoverflow.com/questions/2894365/use-variable-as-dictionary-key-in-django-template
@register.filter
def keyvalue(dict, key):
    return dict[key]

@register.filter
def price_convert(value):
    try:
        s ="{:.2f}".format(value / 100 )
    except:
        s= "None"
    return s


@register.filter
def cap_title(value):
    word =string.capwords(value)
    word=word.translate(str.maketrans({"'":r"\'"}))
    return word

@register.filter
def user_follow(value,arg):
    if UserRelationship.objects.filter(following__user__username=value,follower__user__username=arg).exists():
        return "Following"
    else:
        return "Follow"

@register.filter
def is_user_a_follower(value,arg):
    if UserRelationship.objects.filter(following__user__username=arg,follower__user__username=value).exists():
        return "true"
    else:
        return "false"
