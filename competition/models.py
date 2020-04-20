import re
import uuid as uuid
from django.db import models



class Task(models.Model):
    uuid = models.UUIDField('uuid', default=uuid.uuid4)
    name = models.CharField('název', max_length=255, default='')
    text = models.TextField('text', null=True, blank=True)
    youtube_link = models.CharField('YouTube video', max_length=255, null=True, blank=True)
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

    def youtube_id(self):
        if self.youtube_link is None:
            return None

        m = re.search('(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})', self.youtube_link)
        if m is None:
            return None
        return m.group(1)


class Time(models.Model):
    created = models.DateTimeField('čas', auto_now_add=True)
    player_uuid = models.UUIDField('UUID hráče')
    player_nickname = models.CharField('přezdívka', max_length=255)
    player_category = models.CharField('kategorie', max_length=1)
    task = models.ForeignKey(Task, verbose_name='úkol', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Čas'
        verbose_name_plural = 'Časy'
        ordering = ('created',)

    def category(self):
        return 'Výletník' if self.player_category == 'V' else 'Borec'

    category.short_description = 'kategorie'
