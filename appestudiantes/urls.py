from django.urls import path
from . import views

urlpatterns = [
    path('datosEstudiante',views.datosEstudiante, name='datosEstudiante'),
    path('resumeAsignaturas', views.resumeAsignaturas, name ='resumeAsignaturas'),
    path('resumeNotas', views.resumeNotas, name ='resumeNotas'),
    path('proximosFeed', views.proximosFeed, name ='proximosFeed'),  
    path('resumeSemanal', views.resumeSemanal, name ='resumeSemanal'),
    path('detalleAsignatura', views.detalleAsignatura, name ='detalleAsignatura'),
    path('detalleCompaneros', views.detalleCompaneros, name ='detalleCompaneros'    ),  
    path('detallePromedioNotaAsistencia', views.detallePromedioNotaAsistencia, name ='detallePromedioNotaAsistencia'),
    path('detallePromedioAsignaturas', views.detallePromedioAsignaturas, name ='detallePromedioAsignaturas'),
    path('detalleRegistrosNotasAsignaturas', views.detalleRegistrosNotasAsignaturas, name ='detalleRegistrosNotasAsignaturas'),
]
