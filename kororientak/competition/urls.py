from django.urls import path

from .views import CookiesInfoView, QRCodesView, TaskView

urlpatterns = [
    path('ukol/<uuid:task_uuid>', TaskView.as_view(), name='task'),
    path('cookies', CookiesInfoView.as_view(), name='cookies_info'),
    path('qr-kody', QRCodesView.as_view(), name='qr_codes'),
]
