from django.db import models
from appcomunes.models import *
from appapoderados.models import Apoderado

# Create your models here.
class Estudiante(models.Model):
    
    rutapoderado_str = models.ForeignKey(Apoderado, models.DO_NOTHING, db_column='rutApoderado_str', blank=True, null=True)  # Field name made lowercase.
    idbeca_int = models.ForeignKey(Beca, models.DO_NOTHING, db_column='idBeca_int', blank=True, null=True)  # Field name made lowercase.
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
    telcontacto_str = models.CharField(db_column='telContacto_str', max_length=20, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'estudiante'
        managed = False


