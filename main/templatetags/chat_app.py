from datetime import timedelta

from django import template
from django.utils import timezone
from django.utils.translation import gettext, ngettext
from django.templatetags.static import static
from django.db.models import Q

from  ..models import Talk

register = template.Library()


@register.filter
@register.simple_tag
def elapsed_time(dt):
    if not dt:
        return None

    delta = timezone.now() - dt

    zero = timedelta()
    one_hour = timedelta(hours=1)
    one_day = timedelta(days=1)
    one_week = timedelta(days=7)

    if delta < one_hour:  # 経過時間が 1 時間以内のとき
        minutes = delta.seconds // 60
        return ngettext("%d minute ago", "%d minutes ago", minutes) % minutes
    elif delta < one_day:  # 経過時間が 1 日以内のとき
        hours = delta.seconds // 3600
        return ngettext("%d hour ago", "%d hours ago", hours) % hours
    elif delta < one_week:  # 経過時間が 1 週間以内のとき
        return ngettext("%d day ago", "%d days ago", delta.days) % delta.days
    else:
        return gettext("more than 1 week")
    
@register.simple_tag
def user_icon_url(user_obj):
    if user_obj and user_obj.icon:
        return user_obj.icon.url
    return static('main/img/default-icon.png')

@register.simple_tag
def get_last_message(user1, user2):
    last_talk = Talk.objects.filter(
        (Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1))
    ).order_by('-time').first()
    return last_talk