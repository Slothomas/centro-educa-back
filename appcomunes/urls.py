from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('getAllEvents', views.getAllEvents, name='getAllEvents'),
    path('envioCorreo', views.envioCorreo, name='envioCorreo'),

]
