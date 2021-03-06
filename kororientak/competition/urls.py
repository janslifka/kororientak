from django.urls import path

from .views import CookiesInfoView, QRCodesView, TaskView, ExportCsvView

urlpatterns = [
    path('ukol/<uuid:task_uuid>', TaskView.as_view(), name='task'),
    path('cookies', CookiesInfoView.as_view(), name='cookies_info'),
    path('qr-kody/<int:race_id>', QRCodesView.as_view(), name='qr_codes'),
    path('export/<int:race_id>', ExportCsvView.as_view(), name='export_csv'),
]
