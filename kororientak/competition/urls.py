from django.urls import path

from .views import QRCodesView, TaskView

urlpatterns = [
    path('ukol/<uuid:task_uuid>', TaskView.as_view(), name='task'),
    path('qr-kody', QRCodesView.as_view(), name='qr_codes'),
]
