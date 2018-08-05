from django.contrib import admin
from django.utils import timezone

from datetime import timedelta

from . import models


class AddedBeforeListFilter(admin.SimpleListFilter):
    title = 'added'
    parameter_name = 'added_before'
    
    def lookups(self, request, model_admin):
        return (
            ((timezone.now().replace(hour=0, minute=0, second=0) - timedelta(days=1)).date(), 'Before today'),
            ((timezone.now() - timedelta(days=3)).date(), 'Before 3 days ago'),
            ((timezone.now() - timedelta(days=7)).date(), 'Before 7 days ago'),
            ((timezone.now() - timedelta(days=14)).date(), 'Before two weeks ago'),
            ((timezone.now() - timedelta(days=21)).date(), 'Before three weeks ago'),
            ((timezone.now() - timedelta(days=28)).date(), 'Before four weeks ago'),
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(added__lte=self.value())


class WasSent(admin.SimpleListFilter):
    title = 'was sent'
    parameter_name = 'was_sent'
    
    def lookups(self, request, model_admin):
        return [
            (mailout.pk, mailout.name) for mailout in models.Mailout.objects.all()
        ]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(mailsent__mailout=self.value())


class Opened(admin.SimpleListFilter):
    title = 'has opened'
    parameter_name = 'has_opened'
    
    def lookups(self, request, model_admin):
        return [
            (mailout.pk, mailout.name) for mailout in models.Mailout.objects.all()
        ]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(mailsent__mailout=self.value(), mailsent__last_opened__isnull=False)


class HasNotOpened(admin.SimpleListFilter):
    title = 'has not opened'
    parameter_name = 'has_not_opened'

    def lookups(self, request, model_admin):
        return [
            (mailout.pk, mailout.name) for mailout in models.Mailout.objects.all()
        ]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(mailsent__mailout=self.value(), mailsent__last_opened__isnull=True)


class RSVPFilter(admin.SimpleListFilter):
    title = 'RSVP'
    parameter_name = 'rsvp'
    
    def lookups(self, request, model_admin):
        return (
                    ('no_response', 'No response'),
                    ('all_attending', 'All attending'),
                    ('some_attending', 'At least one attending'),
                    ('some_declined', 'At least one declined'),
                    ('mixed', 'Mix of attending and declined'),
                    ('none_attending', 'None attending'),
                )

    def queryset(self, request, queryset):
        if self.value() == 'no_response':
            return queryset.filter(person__rsvp_status=models.Person.RSVP_UNKNOWN).distinct()
        elif self.value() == 'all_attending':
            return queryset.exclude(person__rsvp_status__in=(models.Person.RSVP_UNKNOWN, models.Person.RSVP_NOT_ATTENDING)).distinct()
        elif self.value() == 'some_attending':
            return queryset.filter(person__rsvp_status=models.Person.RSVP_ATTENDING).distinct()
        elif self.value() == 'some_declined':
            return queryset.filter(person__rsvp_status=models.Person.RSVP_NOT_ATTENDING).distinct()
        elif self.value() == 'mixed':
            return queryset.filter(person__rsvp_status=models.Person.RSVP_ATTENDING).filter(person__rsvp_status=models.Person.RSVP_NOT_ATTENDING).distinct()
        elif self.value() == 'none_attending':
            return queryset.exclude(person__rsvp_status__in=(models.Person.RSVP_UNKNOWN, models.Person.RSVP_ATTENDING)).distinct()
        return queryset
