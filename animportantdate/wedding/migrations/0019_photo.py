# Generated by Django 2.0.5 on 2018-05-21 03:09

from django.db import migrations, models
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wedding', '0018_auto_20180520_1743'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', sorl.thumbnail.fields.ImageField(upload_to='')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('order', models.IntegerField()),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]