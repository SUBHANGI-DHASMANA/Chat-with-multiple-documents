from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.upload_files, name='upload_files'),
    path('ask', views.ask_question, name='ask_question'),
]