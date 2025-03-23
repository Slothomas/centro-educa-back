from rest_framework import serializers
from .models import Usuario, TipoRol

# Serializador para el modelo TipoRol: convierte instancias del modelo a formato JSON (y viceversa)
class TipoRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRol  # Modelo que representa la tabla tipoRol en la base de datos
        fields = ['idTipoRol_int', 'nombre_str']  # Campos que queremos exponer en la API


# Serializador para el modelo Usuario, incluyendo la información del rol (tipoRol) como un objeto anidado
class UsuarioSerializer(serializers.ModelSerializer):
    # En vez de mostrar solo el ID del rol, usamos el serializador completo para mostrar los detalles del rol
    idTipoRol_int = TipoRolSerializer(read_only=True)

    class Meta:
        model = Usuario  # Modelo que representa la tabla usuario
        # Lista de campos que queremos exponer al consumir la API
        fields = [
            'idUsuario_int',           # ID interno del usuario
            'idTipoRol_int',           # Detalles del rol asignado al usuario (como objeto anidado)
            'rut_str',                 # RUT del usuario
            'contrasena_str',          # Contraseña (en texto plano en la BD actual)
            'fechaCreacion_dat',       # Fecha de creación del usuario
            'fechaUltimoAcceso_dat'    # Fecha del último acceso (puede ser null)
        ]
