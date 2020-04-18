import csv

from django.contrib import admin

# Register your models here.
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from competition.models import Task, Time

# Admin settings
admin.site.site_header = 'Kororienťák'
admin.site.site_title = 'Kororienťák'


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


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('order', 'uuid', 'text', 'registration', 'finish')

    readonly_fields = ('uuid', 'qr_code', 'link')

    def get_fields(self, request, obj=None):
        if obj:
            return 'order', 'text', 'registration', 'finish', 'qr_code', 'link'
        else:
            return 'order', 'text', 'registration', 'finish'

    def qr_code(self, obj):
        src = f'https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={self._url(obj)}'
        return mark_safe(f'<img src={src}>')

    def link(self, obj):
        href = self._url(obj)
        return mark_safe(f'<a href={href}>{href}</a>')

    def _url(self, obj):
        return settings.PUBLIC_URL + reverse('task', args=[obj.uuid])


@admin.register(Time)
class TimeAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('created', 'player_uuid', 'player_nickname', 'task')
    readonly_fields = ('created', 'player_uuid', 'player_nickname', 'task')

    actions = ('export_as_csv',)

    def has_add_permission(self, request, obj=None):
        return False
