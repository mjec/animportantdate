# Generated by Django 2.0.5 on 2018-11-25 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wedding', '0023_auto_20181125_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(help_text='HTML is allowed, but paragraph tags will be automatically inserted'),
        ),
    ]
