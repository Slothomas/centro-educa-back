from django.urls import path
from . import views

urlpatterns = [
    path('crear-usuario', views.crear_usuario, name='crear_usuario'),
    path('listar-usuarios', views.listar_usuarios, name='listar_usuarios'),
]
