from django.urls import path

from .views import QRCodesView, view_task

urlpatterns = [
    path('ukol/<uuid:task_uuid>', view_task, name='task'),
    path('qr-kody', QRCodesView.as_view(), name='qr_codes'),
]
