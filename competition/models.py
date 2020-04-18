import uuid as uuid
from django.db import models


# Create your models here.

class Task(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)
    order = models.IntegerField()
    text = models.TextField()
    registration = models.BooleanField(default=False)
    finish = models.BooleanField(default=False)

    class Meta:
        ordering = ('order',)
        indexes = [
            models.Index(fields=('uuid',)),
            models.Index(fields=('order',)),
            models.Index(fields=('registration',)),
            models.Index(fields=('finish',))
        ]


class Time(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    player_uuid = models.UUIDField()
    player_nickname = models.CharField(max_length=255)
    task = models.ForeignKey(Task, on_delete=models.PROTECT)


class Answer(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    player_uuid = models.UUIDField()
    player_nickname = models.CharField(max_length=255)
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    answer = models.TextField()
