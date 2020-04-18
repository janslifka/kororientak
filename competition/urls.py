from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ukol/<uuid:task_uuid>', views.view_task, name='task'),
]
