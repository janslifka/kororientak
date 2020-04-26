import csv
import datetime

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound, HttpResponseNotAllowed, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from .forms import RegistrationForm
from .models import Task, Time, Category, Player, Race


class TaskView(View):
    PLAYER_UUID_COOKIE = 'player_uuid'

    def get(self, request, task_uuid):
        self._initialize(request, task_uuid)

        if not self._can_be_served():
            return HttpResponseNotFound()

        if self.task.registration:
            return self._handle_register()

        if self.task.finish:
            return self._handle_finish()

        return self._handle_task()

    def post(self, request, task_uuid):
        self._initialize(request, task_uuid)

        if self.task.registration:
            return self._handle_register()

        return HttpResponseNotAllowed(['GET'])

    def _initialize(self, request, task_uuid):
        self.request = request
        self.task = get_object_or_404(Task, uuid=task_uuid)
        self.player = self._get_player()

    def _get_player(self):
        try:
            player_uuid = self.request.COOKIES.get(self.PLAYER_UUID_COOKIE)
            player = Player.objects.get(uuid=player_uuid) if player_uuid else None
            return player if player.race == self.task.race else None
        except Exception:
            return None

    def _can_be_served(self):
        return self.task.race.is_active or (self.task.race.is_past and not (self.task.registration or self.task.finish))

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
                self._set_cookie(response, self.PLAYER_UUID_COOKIE, self.player.uuid)

                return response

        else:
            self.player = None
            form = RegistrationForm(choices)

        return self._render('registration.html', {'form': form, })

    def _handle_finish(self):
        times = Time.objects.filter(player=self.player, task__registration=False, task__finish=False).count()
        can_finish = self.player is not None and times > 0
        response = self._render('finish.html', {'can_finish': can_finish})

        if can_finish:
            self._create_time()
            response.delete_cookie(self.PLAYER_UUID_COOKIE)

        return response

    def _handle_task(self):
        if self.player:
            self._create_time()

        return self._render('task.html', {'info_url': settings.INFO_URL})

    def _create_time(self):
        Time.objects.get_or_create(player=self.player, task=self.task)

    def _render(self, template, template_data):
        template_data['app_name'] = settings.APP_NAME
        template_data['task'] = self.task

        if self.task.race.is_active:
            template_data['player'] = self.player

            if self.player and not self.player.category.competitive:
                complete_tasks = self.player.complete_tasks_list()
                template_data['complete_tasks'] = complete_tasks
                template_data['complete_tasks_total_count'] = len(complete_tasks)
                template_data['complete_tasks_complete_count'] = len([i for i in complete_tasks if i[0]])

        return render(self.request, template, template_data)

    def _set_cookie(self, response, key, value, days_expire=7):
        max_age = days_expire * 24 * 60 * 60
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                             "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(key, value, max_age=max_age, expires=expires)


class CookiesInfoView(View):
    def get(self, request):
        return render(request, 'cookies-info.html')


class QRCodesView(LoginRequiredMixin, View):
    raise_exception = True

    def get(self, request, race_id):
        race = get_object_or_404(Race, pk=race_id)
        return render(request, 'qr-codes.html', {
            'tasks': race.task_set.all(),
            'text': race.qr_code_text
        })


class ExportCsvView(LoginRequiredMixin, View):
    raise_exception = True

    def get(self, request, race_id):
        race = get_object_or_404(Race, pk=race_id)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=export.csv'
        writer = csv.writer(response)

        times = Time.objects.filter(task__race=race)

        writer.writerow([
            'created',
            'player_uuid',
            'player_name',
            'player_category_id',
            'player_category_name',
            'player_category_competitive',
            'task_uuid',
            'task_name',
            'task_registration',
            'task_finish',
            'task_text',
            'task_youtube_link',
        ])

        for time in times:
            writer.writerow([
                time.created,
                time.player.uuid,
                time.player.name,
                time.player.category.id,
                time.player.category.name,
                int(time.player.category.competitive),
                time.task.uuid,
                time.task.name,
                int(time.task.registration),
                int(time.task.finish),
                time.task.text,
                time.task.youtube_link,
            ])

        return response
