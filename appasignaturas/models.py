from django.db import models
from appcomunes.models import *
from appestudiantes.models import Estudiante
from appprofesores.models import Profesor

# Create your models here.

class Tipoasignatura(models.Model):
    idtipoasignatura_int = models.AutoField(db_column='idTipoAsignatura_int', primary_key=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=30, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipoAsignatura'
        
        
class Asignatura(models.Model):
    
    rutestudiante_str = models.ForeignKey(Estudiante, models.DO_NOTHING, db_column='rutEstudiante_str', blank=True, null=True)  # Field name made lowercase.
    rutprofesor_str = models.ForeignKey(Profesor, models.DO_NOTHING, db_column='rutProfesor_str', blank=True, null=True)  # Field name made lowercase.
    idtipoasignatura_int = models.ForeignKey(Tipoasignatura, models.DO_NOTHING, db_column='idTipoAsignatura_int', blank=True, null=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    idsemestre_int = models.ForeignKey(Semestre, models.DO_NOTHING, db_column='idSemestre_int', blank=True, null=True)  # Field name made lowercase.
    idanio_int = models.ForeignKey(Anio, models.DO_NOTHING, db_column='idAnio_int', blank=True, null=True)  # Field name made lowercase.
    fecharegistro_dat = models.DateField(db_column='fechaRegistro_dat', blank=True, null=True)  # Field name made lowercase.
    fechamodificacion_dat = models.DateField(db_column='fechaModificacion_dat', blank=True, null=True)  # Field name made lowercase.
    usuariomoficicacion_str = models.CharField(db_column='usuarioMoficicacion_str', max_length=20, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)  # Field name made lowercase.
    motivomodificacion_str = models.CharField(db_column='motivoModificacion_str', max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)  # Field name made lowercase.
    idtipoestado_int = models.ForeignKey(Tipoestado, models.DO_NOTHING, db_column='idTipoEstado_int', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'asignatura'

