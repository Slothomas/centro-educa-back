from django.db import models
from appcomunes.models import *


# Create your models here.

class Tipoapoderado(models.Model):
    idtipoapoderado_int = models.AutoField(db_column='idTipoApoderado_int', primary_key=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipoApoderado'



class Apoderado(models.Model):
    
    
    nombres_str = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    apellidos_str = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    correo_str = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    rut_str = models.CharField(primary_key=True, max_length=20, db_collation='Modern_Spanish_CI_AS')
    direccion_str = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    fechanacimiento_dat = models.DateField(db_column='fechaNacimiento_dat', blank=True, null=True)  # Field name made lowercase.
    fecharegistro_dat = models.DateField(db_column='fechaRegistro_dat', blank=True, null=True)  # Field name made lowercase.
    fechamodificacion_dat = models.DateField(db_column='fechaModificacion_dat', blank=True, null=True)  # Field name made lowercase.
    usuariomodificacion_str = models.CharField(db_column='usuarioModificacion_str', max_length=30, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)  # Field name made lowercase.
    motivomodificacion_str = models.CharField(db_column='motivoModificacion_str', max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)  # Field name made lowercase.
    idnivelsocioeconomico_int = models.ForeignKey(Nivelsocioeconomico, models.DO_NOTHING, db_column='idNivelSocioEconomico_int', blank=True, null=True)  # Field name made lowercase.
    idregion_int = models.ForeignKey(Region, models.DO_NOTHING, db_column='idRegion_int', blank=True, null=True)  # Field name made lowercase.
    idcomuna_int = models.ForeignKey(Comuna, models.DO_NOTHING, db_column='idComuna_int', blank=True, null=True)  # Field name made lowercase.
    idnacionalidad_int = models.ForeignKey(Pais, models.DO_NOTHING, db_column='idNacionalidad_int', blank=True, null=True)  # Field name made lowercase.
    idtipoapoderado_int = models.ForeignKey(Tipoapoderado, models.DO_NOTHING, db_column='idTipoApoderado_int', blank=True, null=True)  # Field name made lowercase.
    idprofesion_int = models.ForeignKey(Tipoprofesion, models.DO_NOTHING, db_column='idProfesion_int', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'apoderado'
