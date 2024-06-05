from django.urls import path
from . import views

urlpatterns = [
    path('datosEstadudiante',views.datosEstudiante, name='datosEstudiante'),
    path('resumeAsignaturas', views.resumeAsignaturas, name ='resumeAsignaturas'),
    path('resumeNotas', views.resumeNotas, name ='resumeNotas'),
    path('proximosFeed', views.proximosFeed, name ='proximosFeed'),  
    path('resumeSemanal', views.resumeSemanal, name ='resumeSemanal'),
    
]
