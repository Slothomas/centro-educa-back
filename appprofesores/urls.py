from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('getAllTeachers', views.getAllTeachers, name='getAllTeachers'),
    path('resumeAsignaturas', views.resumeAsignaturas, name='resumeAsignaturas'),
    path('datosProfesor', views.datosProfesor, name='datosProfesor'),
    path('resumeSemanal', views.resumeSemanal, name='resumeSemanal'),
    path('resumeNotas', views.resumeNotas, name='resumeNotas'),
    path('resumeProximos', views.resumeProximos, name='resumeProximos'),
    path('detalleAsignatura', views.detalleAsignatura, name='detalleAsignatura'),
    path('detallePromedioNotaAsistencia', views.detallePromedioNotaAsistencia, name='detallePromedioNotaAsistencia'),
    path('detallePromedioNotaAsistenciaXAlumno', views.detallePromedioNotaAsistenciaXAlumno, name='detallePromedioNotaAsistenciaXAlumno'),
    path('detalleRegistrosNotasAsistenciaXAlumno', views.detalleRegistrosNotasAsistenciaXAlumno, name='detalleRegistrosNotasAsistenciaXAlumno'),
    path('actualizarNota', views.actualizarNota, name='actualizarNota'),
    path('detalleEventos', views.detalleEventos, name='detalleEventos'),
    path('asignaturasProfesor', views.asignaturasProfesor, name='asignaturasProfesor'),
    path('crearEvento', views.crearEvento, name='crearEvento'),
    path('obtenerObservaciones', views.obtenerObservaciones, name='obtenerObservaciones'),
    path('crearObservacion', views.crearObservacion, name='crearObservacion'),
    path('obtenerLista', views.obtenerLista, name='obtenerLista'),
    path('enviarAsistencia', views.enviarAsistencia, name='enviarAsistencia'),
    path('crearEvaluacion', views.crearEvaluacion, name='crearEvaluacion'),
]
