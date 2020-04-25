import datetime

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound, HttpResponseNotAllowed
from django.shortcuts import render
from django.views import View

from .forms import RegistrationForm
from .models import Task, Time, Category, Player


class TaskView(View):
    def get(self, request, task_uuid):
        self._initialize(request, task_uuid)

        if self.task is None:
            return HttpResponseNotFound()

        if self.task.registration:
            return self._handle_register()

        if self.task.finish:
            return self._handle_finish()

        return self._handle_task()

    def post(self, request, task_uuid):
        self._initialize(request, task_uuid)

        if self.task is None:
            return HttpResponseNotFound()

        if self.task.registration:
            return self._handle_register()

        return HttpResponseNotAllowed(['GET'])

    def _initialize(self, request, task_uuid):
        self.request = request
        self.task = Task.objects.get(uuid=task_uuid)
        self.player = self._get_player()

    def _get_player(self):
        try:
            player_uuid = self.request.COOKIES.get('player_uuid')
            return Player.objects.get(uuid=player_uuid) if player_uuid else None
        except Exception:
            return None

    def _handle_register(self):
        choices = Category.objects.form_choices(self.task.race)
        if self.request.method == 'POST':
            form = RegistrationForm(choices, self.request.POST)

            if form.is_valid():
                player_name = form.cleaned_data.get('name')
                category = Category.objects.get(pk=form.cleaned_data.get('category'))

                self.player = Player.objects.create(name=player_name, category=category, race=self.task.race)
                self._create_time()

                response = self._render('registration_complete.html', {})
                self._set_cookie(response, 'player_uuid', self.player.uuid)

                return response

        else:
            self.player = None
            form = RegistrationForm(choices)

        return self._render('registration.html', {
            'form': form,
        })

    def _handle_finish(self):
        times = Time.objects.filter(player=self.player, task__registration=False, task__finish=False).count()
        can_finish = self.player is not None and times > 0

        if can_finish:
            self._create_time()

        return self._render('finish.html', {
            'can_finish': can_finish
        })

    def _handle_task(self):
        if self.player:
            self._create_time()

        return self._render('task.html', {
            'info_url': settings.INFO_URL,
        })

    def _create_time(self):
        Time.objects.get_or_create(player=self.player, task=self.task)

    def _render(self, template, template_data):
        template_data['player'] = self.player
        template_data['task'] = self.task
        return render(self.request, template, template_data)

    def _set_cookie(self, response, key, value, days_expire=7):
        max_age = days_expire * 24 * 60 * 60
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                             "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(key, value, max_age=max_age, expires=expires)


class QRCodesView(LoginRequiredMixin, View):
    def get(self, request):
        tasks = Task.objects.all()

        return render(request, 'qr-codes.html', {
            'tasks': tasks
        })
