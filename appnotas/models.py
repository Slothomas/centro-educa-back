from django.db import models
from appasignaturas.models import Asignatura

# Create your models here.

class Tiponota(models.Model):
    idtiponota_int = models.AutoField(db_column='idTipoNota_int', primary_key=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=30, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipoNota'


class Nota(models.Model):
    idnota_int = models.AutoField(db_column='idNota_int', primary_key=True)  # Field name made lowercase.
    idasignatura_int = models.ForeignKey(Asignatura, models.DO_NOTHING, db_column='idAsignatura_int', blank=True, null=True)  # Field name made lowercase.
    valor_flo = models.FloatField(blank=True, null=True)
    idtiponota_int = models.ForeignKey(Tiponota, models.DO_NOTHING, db_column='idTipoNota_int', blank=True, null=True)  # Field name made lowercase.
    fecharegistro_dat = models.DateField(db_column='fechaRegistro_dat', blank=True, null=True)  # Field name made lowercase.
    fechamodificacion_dat = models.DateField(db_column='fechaModificacion_dat', blank=True, null=True)  # Field name made lowercase.
    usuariomoficicacion_str = models.CharField(db_column='usuarioMoficicacion_str', max_length=20, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)  # Field name made lowercase.
    motivomodificacion_str = models.CharField(db_column='motivoModificacion_str', max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'nota'

