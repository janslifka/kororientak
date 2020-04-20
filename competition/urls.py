from django.urls import path

from competition.views import QRCodesView
from . import views

urlpatterns = [
    path('ukol/<uuid:task_uuid>', views.view_task, name='task'),
    path('qr-kody', QRCodesView.as_view(), name='qr_codes'),
]
