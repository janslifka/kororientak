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
    player_category = request.COOKIES.get('player_category')
    return player_uuid, player_nickname, player_category


def _valid_player(player):
    return all([prop is not None for prop in player])


def _set_player_for_template(player, options):
    if _valid_player(player):
        options['player_nickname'] = player[1]
        options['player_category'] = 'Výletník' if player[2] == 'V' else 'Běžec'
    return options


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
    player_uuid, player_nickname, player_category = player

    if _valid_player(player):
        Time.objects.get_or_create(
            player_uuid=player_uuid,
            player_nickname=player_nickname,
            player_category=player_category,
            task=task
        )

    return render(request, 'task.html', _set_player_for_template(player, {
        'task': task,
        'info_url': settings.INFO_URL
    }))


def handle_finish(request, task, player):
    player_uuid, player_nickname, player_category = player
    times = Time.objects.filter(player_uuid=player_uuid, task__registration=False, task__finish=False).count()
    can_finish = _valid_player(player) and times > 0

    if can_finish:
        Time.objects.get_or_create(
            player_uuid=player_uuid,
            player_nickname=player_nickname,
            player_category=player_category,
            task=task
        )

    return render(request, 'finish.html', _set_player_for_template(player, {
        'can_finish': can_finish,
        'task': task
    }))


def handle_register(request, task):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            player_uuid = uuid.uuid4()
            player_nickname = form.cleaned_data.get('nickname')
            player_category = form.cleaned_data.get('category')

            response = render(request, 'registration_complete.html',
                              _set_player_for_template((player_uuid, player_nickname, player_category), {}))
            _set_cookie(response, 'player_uuid', player_uuid)
            _set_cookie(response, 'player_nickname', player_nickname)
            _set_cookie(response, 'player_category', player_category)

            Time.objects.create(
                player_uuid=player_uuid,
                player_nickname=player_nickname,
                player_category=player_category,
                task=task
            )

            return response

    else:
        form = RegistrationForm()

    return render(request, 'registration.html', {
        'form': form,
        'task': task
    })
