import re
import uuid as uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Race(models.Model):
    name = models.CharField('název', max_length=255)
    start = models.DateTimeField('začátek')
    end = models.DateTimeField('konec')
    qr_code_text = models.TextField('Text ke QR kódu', null=True, blank=True)
    not_registered_text = models.TextField('Text pro neregistrované', null=True, blank=True)

    class Meta:
        verbose_name = 'Závod'
        verbose_name_plural = 'Závody'
        ordering = ('-start',)

    def __str__(self):
        return self.name

    @property
    def is_future(self):
        return self.start > timezone.now()

    @property
    def is_past(self):
        return self.end < timezone.now()

    @property
    def is_active(self):
        return not self.is_future and not self.is_past


class CategoryManager(models.Manager):
    def form_choices(self, race):
        categories = super().get_queryset().filter(race=race)
        return [(c.pk, c.name) for c in categories]


class Category(models.Model):
    objects = CategoryManager()

    name = models.CharField('název', max_length=255)
    competitive = models.BooleanField('závodní', default=False)
    race = models.ForeignKey(Race, verbose_name='závod', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Kategorie'
        verbose_name_plural = 'Kategorie'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Player(models.Model):
    uuid = models.UUIDField('uuid', default=uuid.uuid4, unique=True)
    name = models.CharField('jméno', max_length=255)
    race = models.ForeignKey(Race, verbose_name='závod', on_delete=models.PROTECT)
    category = models.ForeignKey(Category, verbose_name='kategorie', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Závodník'
        verbose_name_plural = 'Závodníci'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def complete_tasks_list(self):
        tasks = Task.objects.filter(race=self.race, registration=False, finish=False)
        times = [time.task for time in Time.objects.filter(player=self).only('task')]

        def is_complete(task):
            return task in times

        return [(is_complete(task), task.name) for task in tasks]


class Task(models.Model):
    uuid = models.UUIDField('uuid', default=uuid.uuid4, unique=True)
    name = models.CharField('název', max_length=255, default='')
    text = models.TextField('text', null=True, blank=True)
    youtube_link = models.CharField('YouTube video', max_length=255, null=True, blank=True)
    assignment_link = models.CharField('odkaz na zadání', max_length=255, null=True, blank=True)
    help_link = models.CharField('odkaz na nápovědu', max_length=255, null=True, blank=True)
    registration = models.BooleanField('registrace', default=False)
    registration_successful = models.TextField('registrace úspěšná', null=True, blank=True)
    finish = models.BooleanField('cíl', default=False)
    finish_failed = models.TextField('neúspěšný cíl', null=True, blank=True)
    race = models.ForeignKey(Race, verbose_name='závod', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Úkol'
        verbose_name_plural = 'Úkoly'
        ordering = ('-registration', '-finish', 'name',)
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

        m = re.search(r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})',
                      self.youtube_link)
        if m is None:
            return None
        return m.group(1)

    def qr_code(self):
        url = settings.PUBLIC_URL + reverse('task', args=[self.uuid])
        return f'https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={url}'


class Time(models.Model):
    created = models.DateTimeField('čas', auto_now_add=True)
    player = models.ForeignKey(Player, verbose_name='závodník', on_delete=models.PROTECT)
    task = models.ForeignKey(Task, verbose_name='úkol', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Čas'
        verbose_name_plural = 'Časy'
        ordering = ('created',)
