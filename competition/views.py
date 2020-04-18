import datetime
import uuid

from django.conf import settings
from django.http import HttpResponseNotFound
from django.shortcuts import render

from .models import Task, Time
from .forms import RegistrationForm


def _set_cookie(response, key, value, days_expire=7):
    max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                         "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires)


def _get_player(request):
    player_uuid = request.COOKIES.get('player_uuid')
    player_nickname = request.COOKIES.get('player_nickname')
    return player_uuid, player_nickname


def view_task(request, task_uuid):
    task = Task.objects.filter(uuid=task_uuid).first()

    if task is None:
        return HttpResponseNotFound()

    if task.registration:
        return handle_register(request, task)

    player_uuid, player_nickname = _get_player(request)

    if task.finish:
        return handle_finish(request, task, player_uuid, player_nickname)

    return handle_task(request, task, player_uuid, player_nickname)


def handle_task(request, task, player_uuid, player_nickname):
    if player_uuid is not None and player_nickname is not None:
        Time.objects.get_or_create(
            player_uuid=player_uuid,
            player_nickname=player_nickname,
            task=task
        )

    return render(request, 'task.html', {
        'player_nickname': player_nickname,
        'task': task,
        'info_url': settings.INFO_URL
    })


def handle_finish(request, task, player_uuid, player_nickname):
    times = Time.objects.filter(player_uuid=player_uuid, task__registration=False, task__finish=False).count()

    if times > 0:
        Time.objects.get_or_create(
            player_uuid=player_uuid,
            player_nickname=player_nickname,
            task=task
        )

    return render(request, 'finish.html', {
        'can_finish': times > 0,
        'player_nickname': player_nickname,
        'task': task
    })


def handle_register(request, task):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            player_uuid = uuid.uuid4()
            player_nickname = form.cleaned_data.get('nickname')

            response = render(request, 'registration_complete.html', {
                'player_nickname': player_nickname
            })
            _set_cookie(response, 'player_uuid', player_uuid)
            _set_cookie(response, 'player_nickname', player_nickname)

            Time.objects.create(
                player_uuid=player_uuid,
                player_nickname=player_nickname,
                task=task
            )

            return response

    else:
        form = RegistrationForm()

    return render(request, 'registration.html', {
        'form': form,
        'task': task
    })
