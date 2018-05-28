from django import template
from wedding import models

register = template.Library()


@register.simple_tag(takes_context=True)
def return_event_from_group(context, event_short_name):
    try:
        group_id = context.request.session["group_id"]
        group = models.Group.objects.get(id=group_id)
    except (KeyError, models.Group.DoesNotExist):
        return None

    try:
        return group.events.get(short_name=event_short_name)
    except models.Event.DoesNotExist:
        return None

def outstanding_need_to_sends(what):
    return models.NeedToSend.objects.filter(what=what, sent__isnull=True).count()

@register.simple_tag
def outstanding_invitations():
    return outstanding_need_to_sends(models.NeedToSend.INVITATION)

@register.simple_tag
def outstanding_thankyou_cards():
    return outstanding_need_to_sends(models.NeedToSend.THANKYOU_CARD)
    
@register.simple_tag
def outstanding_save_the_dates():
    return outstanding_need_to_sends(models.NeedToSend.SAVE_THE_DATE)
