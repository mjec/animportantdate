# Generated by Django 2.0.5 on 2018-05-23 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wedding', '0019_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='photo',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]