from django.contrib import admin
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django.template.defaultfilters import escape
from django.db import models as django_models
from django import forms

from . import models

class MailSentInline(admin.TabularInline):
    model = models.MailSent
    fields = ('recipient_link', 'datestamp', 'last_opened')
    readonly_fields = ('recipient_link', 'datestamp', 'last_opened')
    empty_value_display = '(Not yet)'
    extra = 0
    max_num = 0
    can_delete = False

    def recipient_link(self, obj):
        return mark_safe(
            '<a href="{url}">{display_name}</a>'.format(
                url=reverse("admin:wedding_person_change", args=(obj.recipient.pk,)),
                display_name=escape(obj.recipient.name)))
    recipient_link.short_description = "Who"


class NeedToSendInline(admin.TabularInline):
    model = models.NeedToSend
    extra = 0
    show_change_link = True
    formfield_overrides = {
        django_models.TextField: {'widget': forms.TextInput},
    }


class NoteInline(admin.TabularInline):
    model = models.Note
    extra = 0
    fields = ('content', 'created')
    readonly_fields = ('created',)
    formfield_overrides = {
        django_models.TextField: {'widget': forms.Textarea(attrs={'rows': 2, 'cols': 80})},
    }


class MailoutImageInline(admin.TabularInline):
    model = models.MailoutImage
    extra = 1


class PersonInline(admin.TabularInline):
    model = models.Person
    extra = 0
    show_change_link = True

    formfield_overrides = {
        django_models.TextField: {'widget': forms.TextInput},
    }


class GroupInline(admin.TabularInline):
    model = models.Event.groups.through
    fields = ('group_link', )
    readonly_fields = ('group_link',)
    extra = 0
    verbose_name = 'invited group'

    def group_link(self, obj):
        return mark_safe(
            '<a href="{url}">{display_name}</a>'.format(
                url=reverse("admin:wedding_group_change", args=(obj.group.pk,)),
                display_name=escape(obj.group.display_name)))
    group_link.short_description = "Group"
