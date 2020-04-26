import codecs
import csv
import uuid

from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import reverse, path
from django.utils.safestring import mark_safe

from .forms import TaskImportForm
from .models import Task, Time, Race, Category, Player

# Admin settings
admin.site.site_header = settings.APP_NAME
admin.site.site_title = settings.APP_NAME


def short_description(description):
    def decorator(fn):
        fn.short_description = description
        return fn

    return decorator


def generate_change_link(admin_url, model_id, name):
    url = reverse(admin_url, args=[model_id])
    link = '<a href="%s">%s</a>' % (url, name)

    return mark_safe(link)


class ReadOnlyInlineMixin:
    def get_max_num(self, request, obj=None, **kwargs):
        return 0


class ReadOnlyAdminMixin:
    def has_add_permission(self, request, obj=None):
        return False


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class TaskInline(ReadOnlyInlineMixin, admin.TabularInline):
    model = Task
    fields = ('name', 'registration', 'finish')
    readonly_fields = ('name', 'registration', 'finish')
    extra = 0
    show_change_link = True


class TimeInline(ReadOnlyInlineMixin, admin.TabularInline):
    model = Time
    fields = ('created', 'task')
    readonly_fields = ('created', 'task')
    extra = 0


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'end')

    inlines = (CategoryInline, TaskInline)

    change_form_template = 'admin/race_change_form.html'


@admin.register(Player)
class PlayerAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    readonly_fields = ('uuid', 'name', 'category', 'race')

    list_display = ('name', 'category', 'race_link')
    list_filter = ('race',)

    inlines = (TimeInline,)

    @short_description('Závod')
    def race_link(self, player):
        return generate_change_link('admin:competition_race_change', player.race.id, player.race.name)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('qr_code', 'link')

    list_display = ('name', 'race_link', 'registration', 'finish')
    list_filter = ('race',)

    change_list_template = 'admin/task_change_list.html'

    def get_fields(self, request, obj=None):
        if obj:
            return ('race',
                    'uuid',
                    'name',
                    'text',
                    'youtube_link',
                    'registration',
                    'registration_successful',
                    'finish',
                    'finish_failed',
                    'qr_code',
                    'link',)
        else:
            return ('race',
                    'uuid',
                    'name',
                    'text',
                    'youtube_link',
                    'registration',
                    'registration_successful',
                    'finish',
                    'finish_failed',)

    def qr_code(self, obj):
        src = f'https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={self._url(obj)}'
        return mark_safe(f'<img src="{src}">')

    def link(self, obj):
        href = self._url(obj)
        return mark_safe(f'<a href="{href}">{href}</a>')

    @short_description('Závod')
    def race_link(self, task):
        return generate_change_link('admin:competition_race_change', task.race.id, task.race.name)

    def _url(self, obj):
        return settings.PUBLIC_URL + reverse('task', args=[obj.uuid])

    def get_urls(self):
        urls = super().get_urls()
        model_urls = [path('import-csv/', self.import_csv)]
        return model_urls + urls

    def import_csv(self, request):
        if request.method == 'POST':
            try:
                form = TaskImportForm(request.POST)
                form.is_valid()
                race = form.cleaned_data.get('race')

                csv_file = request.FILES['csv_file']
                reader = csv.reader(codecs.iterdecode(csv_file, 'utf-8'))

                def clean_value(string):
                    return string if len(string) > 0 else None

                def bool_value(string):
                    return True if string == '1' else False

                first = True
                for row in reader:
                    if first:
                        first = False
                        continue

                    if len(row) != 8:
                        raise AssertionError

                    task_uuid = clean_value(row[0])

                    Task.objects.create(
                        uuid=task_uuid if task_uuid else uuid.uuid4(),
                        name=row[1],
                        text=clean_value(row[2]),
                        youtube_link=clean_value(row[3]),
                        registration=bool_value(row[4]),
                        registration_successful=clean_value(row[5]),
                        finish=bool_value(row[6]),
                        finish_failed=clean_value(row[7]),
                        race=race
                    )

                self.message_user(request, 'Úkoly byly importovány.')
            except Exception:
                self.message_user(request, 'Úkoly se nepodařilo importovat.', level=messages.ERROR)
            return redirect('..')

        form = TaskImportForm()
        return render(request, 'admin/task_import_form.html', {
            'form': form
        })


@admin.register(Time)
class TimeAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    fields = ('created', 'player', 'task')
    readonly_fields = ('created', 'player', 'task')

    list_display = ('created', 'race_link', 'player_link', 'task_link')
    list_filter = ('task__race',)

    @short_description('závod')
    def get_race(self, obj):
        return obj.task.race.name

    @short_description('Závod')
    def race_link(self, time):
        return generate_change_link('admin:competition_race_change', time.task.race.id, time.task.race.name)

    @short_description('Závodník')
    def player_link(self, time):
        return generate_change_link('admin:competition_player_change', time.player.id, time.player.name)

    @short_description('Úkol')
    def task_link(self, time):
        return generate_change_link('admin:competition_task_change', time.task.id, time.task.__str__())
