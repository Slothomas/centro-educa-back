from django.urls import path
from . import views

urlpatterns = [
    path('resumeAsignaturas', views.resumeAsignaturas, name ='resumeAsignaturas'),
]
