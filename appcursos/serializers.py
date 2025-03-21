# appcursos/serializers.py

from rest_framework import serializers
from appcursos.models import Curso, CursoEstudiante
from appestudiantes.models import Estudiante


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ['idCurso_int', 'nivelCurso_str', 'letraCurso_str']


class EstudianteCursoSerializer(serializers.ModelSerializer):
    idCurso_int = serializers.SerializerMethodField()

    class Meta:
        model = Estudiante
        fields = ['rut_str', 'nombres_str', 'idCurso_int']

    def get_idCurso_int(self, obj):
        # Buscar el primer curso asociado al estudiante (si hay)
        curso_estudiante = CursoEstudiante.objects.filter(rutEstudiante_str=obj.rut_str).select_related('idCurso_int').first()
        if curso_estudiante and curso_estudiante.idCurso_int:
            return CursoSerializer(curso_estudiante.idCurso_int).data
        return None
