import uuid as uuid
from django.db import models


# Create your models here.

class Task(models.Model):
    uuid = models.UUIDField('uuid', default=uuid.uuid4)
    name = models.CharField('název', max_length=255, default='')
    text = models.TextField('text')
    registration = models.BooleanField('registrace', default=False)
    finish = models.BooleanField('cíl', default=False)

    class Meta:
        verbose_name = 'Úkol'
        verbose_name_plural = 'Úkoly'
        ordering = ('name',)
        indexes = [
            models.Index(fields=('uuid',)),
            models.Index(fields=('registration',)),
            models.Index(fields=('finish',))
        ]

    def __str__(self):
        registration = ' (registrace)' if self.registration else ''
        finish = ' (cíl)' if self.finish else ''
        return f'{self.name}{registration}{finish}'


class Time(models.Model):
    created = models.DateTimeField('čas', auto_now_add=True)
    player_uuid = models.UUIDField('UUID hráče')
    player_nickname = models.CharField('přezdívka hráče', max_length=255)
    task = models.ForeignKey(Task, verbose_name='úkol', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Čas'
        verbose_name_plural = 'Časy'
        ordering = ('created',)
