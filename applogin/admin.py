from django.contrib import admin
from .models import Tiporol, Usuario

# Registro de modelos para el panel de administración
admin.site.register(Tiporol)
admin.site.register(Usuario)