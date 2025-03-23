# appadministrador/models.py

from django.db import models

class TipoRol(models.Model):
    idTipoRol_int = models.AutoField(primary_key=True, db_column='idTipoRol_int')
    nombre_str = models.CharField(max_length=100, db_column='nombre_str', blank=True, null=True)

    def __str__(self):
        return self.nombre_str or "Rol sin nombre"

    class Meta:
        db_table = 'tipoRol'
        managed = False


class Usuario(models.Model):
    idUsuario_int = models.AutoField(primary_key=True, db_column='idUsuario_int')
    idTipoRol_int = models.ForeignKey(
        TipoRol,
        models.CASCADE,
        db_column='idTipoRol_int',
        blank=True,
        null=True
    )
    rut_str = models.CharField(max_length=20, db_column='rut_str', blank=True, null=True)
    contrasena_str = models.CharField(max_length=20, db_column='contrasena_str', blank=True, null=True)
    fechaCreacion_dat = models.DateField(db_column='fechaCreacion_dat', blank=True, null=True)
    fechaUltimoAcceso_dat = models.DateField(db_column='fechaUltimoAcceso_dat', blank=True, null=True)

    def __str__(self):
        return f"{self.rut_str} - {self.idTipoRol_int}"

    class Meta:
        db_table = 'usuario'
        managed = False
