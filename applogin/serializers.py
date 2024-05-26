from rest_framework import serializers

from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Usuario
        fields = ['rut_str', 'contrasena_str', 'idtiporol_int']