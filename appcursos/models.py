# appcursos/models.py

from django.db import models
from appestudiantes.models import Estudiante
from appprofesores.models import Profesor

class Curso(models.Model):
    idCurso_int = models.AutoField(primary_key=True, db_column='idCurso_int')
    rutProfesorJefe_str = models.ForeignKey(
        Profesor,
        models.DO_NOTHING,
        db_column='rutProfesorJefe_str',
        blank=True,
        null=True
    )
    letraCurso_str = models.CharField(max_length=2, db_column='letraCurso_str', blank=True, null=True)
    nivelCurso_str = models.CharField(max_length=25, db_column='nivelCurso_str', blank=True, null=True)

    class Meta:
        db_table = 'curso'
        managed = False  # Si no quieres que Django intente crear/modificar la tabla en migraciones


class CursoEstudiante(models.Model):
    idCursoEstudiante_int = models.IntegerField(primary_key=True, db_column='idCursoEstudiante_int')
    rutEstudiante_str = models.ForeignKey(
        Estudiante,
        models.DO_NOTHING,
        db_column='rutEstudiante_str',
        blank=True,
        null=True
    )
    idCurso_int = models.ForeignKey(
        Curso,
        models.DO_NOTHING,
        db_column='idCurso_int',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'cursoEstudiante'
        managed = False
