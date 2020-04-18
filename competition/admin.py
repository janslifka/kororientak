import csv

from django.contrib import admin

# Register your models here.
from django.http import HttpResponse

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

    fields = ('order', 'text', 'registration', 'finish')
    readonly_fields = ('uuid',)


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
