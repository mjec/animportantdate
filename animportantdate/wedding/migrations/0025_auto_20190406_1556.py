# Generated by Django 2.0.13 on 2019-04-06 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wedding', '0024_auto_20181125_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='needtosend',
            name='what',
            field=models.IntegerField(choices=[(1, 'Invitation'), (2, 'Thank you card'), (3, 'Save the date'), (4, 'Reminder')]),
        ),
    ]
