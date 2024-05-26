from django.db import models

# Create your models here.
class Tiporol(models.Model):
    idtiporol_int = models.AutoField(db_column='idTipoRol_int', primary_key=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipoRol'


class Usuario(models.Model):
    idusuario_int = models.AutoField(db_column='idUsuario_int', primary_key=True)  # Field name made lowercase.
    idtiporol_int = models.ForeignKey(Tiporol, models.DO_NOTHING, db_column='idTipoRol_int', blank=True, null=True)  # Field name made lowercase.
    rut_str = models.CharField(max_length=20, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    contrasena_str = models.CharField(max_length=20, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    fechacreacion_dat = models.DateField(db_column='fechaCreacion_dat', blank=True, null=True)  # Field name made lowercase.
    fechaultimoacceso_dat = models.DateField(db_column='fechaUltimoAcceso_dat', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuario'
        
        
        