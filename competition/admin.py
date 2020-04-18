import csv

from django.contrib import admin

# Register your models here.
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from competition.models import Task, Time, Answer

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

    readonly_fields = ('uuid', 'qr_code')

    def get_fields(self, request, obj=None):
        if obj:
            return 'order', 'text', 'registration', 'finish', 'qr_code'
        else:
            return 'order', 'text', 'registration', 'finish'

    def qr_code(self, obj):
        link = settings.PUBLIC_URL + reverse('task', args=[obj.uuid])
        src = f'https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={link}'
        return mark_safe(f'<img src={src}>')


@admin.register(Time)
class TimeAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('created', 'player_uuid', 'player_nickname', 'task')
    readonly_fields = ('created', 'player_uuid', 'player_nickname', 'task')

    actions = ('export_as_csv',)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('created', 'player_uuid', 'player_nickname', 'task', 'answer')
    readonly_fields = ('created', 'player_uuid', 'player_nickname', 'task', 'answer')

    actions = ('export_as_csv',)

    def has_add_permission(self, request, obj=None):
        return False
