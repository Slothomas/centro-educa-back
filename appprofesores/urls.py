from django.urls import path
from . import views

urlpatterns = [
    path('getTeacher', views.getTeacher, name ='getTeacher'),
    path('getAllTeachers', views.getAllTeachers, name ='getAllTeachers'),
]
