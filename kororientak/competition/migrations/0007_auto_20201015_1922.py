# Generated by Django 3.0.5 on 2020-10-15 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0006_auto_20200426_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='assignment_link',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='odkaz na zadání'),
        ),
        migrations.AddField(
            model_name='task',
            name='help_link',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='odkaz na nápovědu'),
        ),
    ]
