# Generated by Django 3.0.5 on 2020-04-19 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0006_auto_20200419_2240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='text',
            field=models.TextField(default=None, null=True, verbose_name='text'),
        ),
        migrations.AlterField(
            model_name='task',
            name='youtube_link',
            field=models.CharField(default=None, max_length=255, null=True, verbose_name='YouTube video'),
        ),
    ]
