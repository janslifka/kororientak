import datetime
import uuid

import unidecode as unidecode
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.views import View

from .models import Task, Time, Category, Player
from .forms import RegistrationForm


def _set_cookie(response, key, value, days_expire=7):
    max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                         "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires)


def _get_player(request):
    try:
        player_uuid = request.COOKIES.get('player_uuid')
        player = Player.objects.get(uuid=player_uuid)
        return player
    except Exception:
        return None


def view_task(request, task_uuid):
    task = Task.objects.filter(uuid=task_uuid).first()

    if task is None:
        return HttpResponseNotFound()

    if task.registration:
        return handle_register(request, task)

    player = _get_player(request)

    if task.finish:
        return handle_finish(request, task, player)

    return handle_task(request, task, player)


def handle_task(request, task, player):
    player = _get_player(request)

    if player:
        Time.objects.get_or_create(
            player=player,
            task=task
        )

    return render(request, 'task.html', {
        'task': task,
        'info_url': settings.INFO_URL,
        'player': player
    })


def handle_finish(request, task, player):
    times = Time.objects.filter(player=player, task__registration=False, task__finish=False).count()
    can_finish = player is not None and times > 0

    if can_finish:
        Time.objects.get_or_create(
            player=player,
            task=task
        )

    return render(request, 'finish.html', {
        'can_finish': can_finish,
        'player': player,
        'task': task
    })


def handle_register(request, task):
    choices = Category.objects.form_choices(task.race)
    if request.method == 'POST':
        form = RegistrationForm(choices, request.POST)

        if form.is_valid():
            player_name = form.cleaned_data.get('name')
            category = Category.objects.get(pk=form.cleaned_data.get('category'))

            player = Player.objects.create(name=player_name, category=category, race=task.race)
            Time.objects.create(player=player, task=task)

            response = render(request, 'registration_complete.html', {
                'player': player
            })
            _set_cookie(response, 'player_uuid', player.uuid)

            return response

    else:
        form = RegistrationForm(choices)

    return render(request, 'registration.html', {
        'form': form,
        'task': task
    })


class QRCodesView(LoginRequiredMixin, View):
    def get(self, request):
        tasks = Task.objects.all()

        return render(request, 'qr-codes.html', {
            'tasks': tasks
        })
