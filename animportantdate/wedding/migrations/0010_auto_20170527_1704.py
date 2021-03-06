# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-27 17:04

from __future__ import unicode_literals

import string

from django.db import migrations


def create_short_name(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Event = apps.get_model('wedding', 'Event')
    for event in Event.objects.all():
        short_name = "".join(
            i for i in event.name.lower() if i in string.ascii_lowercase
        )
        short_name = short_name[:20]
        event.short_name = short_name
        event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('wedding', '0009_auto_20170527_1704'),
    ]

    operations = [
        migrations.RunPython(create_short_name),
    ]
