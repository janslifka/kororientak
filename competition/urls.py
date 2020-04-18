from django.urls import path

from . import views

urlpatterns = [
    path('ukol/<uuid:task_uuid>', views.view_task, name='task'),
]
