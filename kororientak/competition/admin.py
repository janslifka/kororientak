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


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Exportovat jako CSV"


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


@admin.register(Player)
class PlayerAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    readonly_fields = ('uuid', 'name', 'category', 'race')

    list_display = ('name', 'category', 'race')
    list_filter = ('race',)

    inlines = (TimeInline,)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('qr_code', 'link')

    list_display = ('name', 'race', 'registration', 'finish')
    list_filter = ('race',)

    def get_fields(self, request, obj=None):
        if obj:
            return 'race', 'uuid', 'name', 'text', 'youtube_link', 'registration', 'finish', 'qr_code', 'link'
        else:
            return 'race', 'uuid', 'name', 'text', 'youtube_link', 'registration', 'finish'

    def qr_code(self, obj):
        src = f'https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={self._url(obj)}'
        return mark_safe(f'<img src={src}>')

    def link(self, obj):
        href = self._url(obj)
        return mark_safe(f'<a href={href}>{href}</a>')

    def _url(self, obj):
        return settings.PUBLIC_URL + reverse('task', args=[obj.uuid])


@admin.register(Time)
class TimeAdmin(ReadOnlyAdminMixin, ExportCsvMixin, admin.ModelAdmin):
    fields = ('created', 'player', 'task')
    readonly_fields = ('created', 'player', 'task')

    list_display = ('created', 'get_race', 'player', 'task')
    list_filter = ('task__race',)

    actions = ('export_as_csv',)

    @short_description('závod')
    def get_race(self, obj):
        return obj.task.race.name
