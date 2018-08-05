from django.contrib import admin
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django.template.defaultfilters import escape

from solo.admin import SingletonModelAdmin
from sorl.thumbnail.admin import AdminImageMixin

from . import models
from . import views, staff_views
from .fields import PnrField

from .admin_actions import *
from .admin_inlines import *
from .admin_filters import *

class AdminSite(admin.AdminSite):
    site_header = 'Curls & Beard'
    site_title = 'Curls & Beard'


site = AdminSite(name='admin')


@admin.register(models.Event, site=site)
class EventAdmin(admin.ModelAdmin):
    model = models.Event
    list_display = ('name', 'invited', 'attending', 'declined', 'no_response')
    
    inlines = [
        GroupInline,
    ]



@admin.register(models.NeedToSend, site=site)
class NeedToSendAdmin(admin.ModelAdmin):
    model = models.NeedToSend
    list_display = ('why', 'who_link', 'what', 'added', 'sent')
    list_display_links = ('why', 'what', 'added', 'sent')
    list_filter = ('what', 'sent', 'added', AddedBeforeListFilter)
    list_per_page = 200
    search_fields = ('why', 'who__person__name', 'who__display_name', 'who__pnr')
    empty_value_display = '(Not yet)'
    autocomplete_fields = ('who',)
    actions = [mark_as_sent_today]

    def who_link(self, obj):
        return mark_safe(
            '<a href="{url}">{display_name}</a>'.format(
                url=reverse("admin:wedding_group_change", args=(obj.who.pk,)),
                display_name=escape(obj.who.display_name)))
    who_link.short_description = "Who"



@admin.register(models.Person, site=site)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_link', 'rsvp_status')
    list_display_links = ('name', )
    list_filter = ('rsvp_status', WasSent, Opened, HasNotOpened)
    list_per_page = 200
    search_fields = ('name', 'group__display_name', 'group__pnr')
    autocomplete_fields = ('group',)

    inlines = [
        MailSentInline,
    ]

    def group_link(self, obj):
        return mark_safe(
            '<a href="{url}">{display_name}</a>'.format(
                url=reverse("admin:wedding_group_change", args=(obj.group.pk,)),
                display_name=escape(obj.group.display_name)))
    group_link.short_description = "Group"


@admin.register(models.Group, site=site)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'invited', 'attending', 'declined', 'no_response')
    list_filter = (RSVPFilter, 'events')
    search_fields = ('display_name', 'pnr', 'person__name')
    actions = [
        need_to_send_save_the_date,
        need_to_send_invitation,
        need_to_send_thankyou_card,
    ]

    formfield_overrides = {
        PnrField: {'initial': PnrField.make_generator(6)},
    }

    inlines = [
        PersonInline,
        NeedToSendInline,
        NoteInline,
    ]


@admin.register(models.Mailout, site=site)
class MailoutAdmin(admin.ModelAdmin):
    fields = ('name', 'event', 'subject', 'plain_body', 'html_body')
    list_display = ('name', 'event_link', 'subject', 'sent_to', 'opened_by')
    list_display_links = ('name', 'subject')
    list_filter = ('event', 'subject')
    search_fields = ('name', 'event__short_name', 'event__name', 'subject', 'plain_body')

    inlines = [
        MailoutImageInline,
        MailSentInline,
    ]

    def view_on_site(self, obj):
        return reverse(staff_views.mailout, args=(obj.id,))

    def get_readonly_fields(self, request, obj):
        if obj is not None and obj.mailsent_set.count() > 0:
            return ('subject', 'plain_body', 'html_body')
        else:
            return ()

    def event_link(self, obj):
        return mark_safe(
            '<a href="{url}">{display_name}</a>'.format(
                url=reverse("admin:wedding_event_change", args=(obj.event.pk,)),
                display_name=escape(obj.event.name)))
    event_link.short_description = "Event"


from admin_ordering.admin import OrderableAdmin

@admin.register(models.Photo, site=site)
class PhotoAdmin(AdminImageMixin, OrderableAdmin, admin.ModelAdmin):
    list_display = ('__str__', 'description', 'order',)
    list_editable = ('order',)
    list_display_links = ('__str__', 'description',)
    search_fields = ('name', 'description',)
    ordering_field = 'order'


site.register(models.SiteConfiguration, SingletonModelAdmin)
