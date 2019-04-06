from .models import NeedToSend

from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse

__all__ = ['mark_as_sent_today', 'need_to_send_invitation',
           'need_to_send_thankyou_card', 'need_to_send_save_the_date',
           'need_to_send_reminder', 'add_details_section']


def mark_as_sent_today(modeladmin, request, queryset):
    queryset.update(sent=timezone.now())


mark_as_sent_today.short_description = 'Mark as sent today'


def build_need_to_send(what):
    def need_to_send(modeladmin, request, queryset):
        need_to_sends = []
        for group in queryset:
            need_to_sends.append(NeedToSend(
                who=group,
                what=what,
                why='Added by {}'.format(request.user)
            ))
        NeedToSend.objects.bulk_create(need_to_sends)
    need_to_send.__name__ = 'need_to_send_{}'.format(what)
    need_to_send.short_description = 'Add need to send {}'.format(
        NeedToSend.thing_to_send_name(what).lower())
    return need_to_send


need_to_send_invitation = build_need_to_send(NeedToSend.INVITATION)
need_to_send_thankyou_card = build_need_to_send(NeedToSend.THANKYOU_CARD)
need_to_send_save_the_date = build_need_to_send(NeedToSend.SAVE_THE_DATE)
need_to_send_reminder = build_need_to_send(NeedToSend.REMINDER)


def add_details_section(modeladmin, request, queryset):
    return redirect(
        reverse('add_details_section') + '?' +
        '&'.join(['groups={}'.format(x)
                  for x in queryset.values_list('pk', flat=True)])
    )


add_details_section.short_description = 'Add details section'
