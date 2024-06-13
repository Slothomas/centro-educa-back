from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name ='login'),
    path('perfil', views.perfil, name ='perfil'),
    path('actualizarClave', views.actualizarClave, name ='actualizarClave'),
    path('actualizarDatos', views.actualizarDatos, name ='actualizarDatos'),
]
