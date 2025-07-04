from django.urls import path

from .views import download_file, upload_file

urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
    path('download/<str:archive_name>', download_file, name='download_file'),
]
