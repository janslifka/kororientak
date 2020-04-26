import csv

from django.contrib import admin

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

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
