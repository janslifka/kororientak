import datetime
import uuid

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render

from competition.models import Task, Time, Answer
from .forms import RegistrationForm, AnswerForm


def _set_cookie(response, key, value, days_expire=7):
    max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                         "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires)


def _get_player(request):
    player_uuid = request.COOKIES.get('player_uuid')
    player_nickname = request.COOKIES.get('player_nickname')
    return player_uuid, player_nickname


def index(request):
    return HttpResponse("hello, world")


def view_task(request, task_uuid):
    task = Task.objects.filter(uuid=task_uuid).first()

    if task is None:
        return HttpResponseNotFound()

    if task.registration:
        return handle_register(request, task)

    player_uuid, player_nickname = _get_player(request)

    if player_uuid is None or player_nickname is None:
        return render(request, 'not_registered.html')

    Time.objects.get_or_create(
        player_uuid=player_uuid,
        player_nickname=player_nickname,
        task=task
    )

    if task.finish:
        return render(request, 'finish.html', {
            'player_nickname': player_nickname,
            'task': task
        })

    return handle_answer(request, task, player_uuid, player_nickname)


def handle_answer(request, task, player_uuid, player_nickname):
    if request.method == 'POST':
        form = AnswerForm(request.POST)

        if form.is_valid():
            answer = form.cleaned_data.get('answer')
            Answer.objects.create(
                player_uuid=player_uuid,
                player_nickname=player_nickname,
                task=task,
                answer=answer
            )

            return HttpResponse("Uloženo, můžeš pokračovat")

    else:
        form = AnswerForm()

    return render(request, 'task.html', {
        'player_nickname': player_nickname,
        'form': form,
        'task': task
    })


def handle_register(request, task):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            player_uuid = uuid.uuid4()
            player_nickname = form.cleaned_data.get('nickname')

            response = HttpResponse("Výborně, můžeš vyrazit")
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