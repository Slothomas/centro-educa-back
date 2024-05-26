from django.db import models

# Create your models here.

class Tipoestado(models.Model):
    idtipoestado_int = models.AutoField(db_column='idTipoEstado_int', primary_key=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipoEstado'

class Anio(models.Model):
    idanio_int = models.AutoField(db_column='idAnio_int', primary_key=True)  # Field name made lowercase.
    numero_int = models.IntegerField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'anio'


class Certificacion(models.Model):
    idcertificacion_int = models.AutoField(db_column='idCertificacion_int', primary_key=True)  # Field name made lowercase.
    idanio_int = models.ForeignKey(Anio, models.DO_NOTHING, db_column='idAnio_int', blank=True, null=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    lugarobtenido_str = models.CharField(db_column='lugarObtenido_str', max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)  # Field name made lowercase.
    vigente_boo = models.BooleanField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'certificacion'


class Nivelsocioeconomico(models.Model):
    idnivelsocioeconomico_int = models.AutoField(db_column='idNivelSocioEconomico_int', primary_key=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nivelSocioEconomico'


class Comuna(models.Model):
    idcomuna_int = models.AutoField(db_column='idComuna_int', primary_key=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comuna'


class Pais(models.Model):
    idpais_int = models.AutoField(db_column='idPais_int', primary_key=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    nacionalidad_str = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pais'
        
        
class Tipoprofesion(models.Model):
    idtipoprofesion_int = models.AutoField(db_column='idTipoProfesion_int', primary_key=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipoProfesion'


class Region(models.Model):
    idregion_int = models.AutoField(db_column='idRegion_int', primary_key=True)  # Field name made lowercase.
    numregion_int = models.IntegerField(db_column='numRegion_int', blank=True, null=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'region'

class Tipobeca(models.Model):
    idtipobeca_int = models.AutoField(db_column='idTipoBeca_int', primary_key=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    monto_int = models.IntegerField(blank=True, null=True)
    porcentaje_int = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipoBeca'
        
        
class Beca(models.Model):
    idbeca_int = models.AutoField(db_column='idBeca_int', primary_key=True)  # Field name made lowercase.
    idtipobeca_int = models.ForeignKey(Tipobeca, models.DO_NOTHING, db_column='idTipoBeca_int', blank=True, null=True)  # Field name made lowercase.
    cobertura_str = models.CharField(max_length=10, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    montocobertura_int = models.IntegerField(db_column='montoCobertura_int', blank=True, null=True)  # Field name made lowercase.
    fechaotorgamiento_dat = models.DateField(db_column='fechaOtorgamiento_dat', blank=True, null=True)  # Field name made lowercase.
    fechavencimiento_dat = models.DateField(db_column='fechaVencimiento_dat', blank=True, null=True)  # Field name made lowercase.
    idtipoestado_int = models.ForeignKey(Tipoestado, models.DO_NOTHING, db_column='idTipoEstado_int', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'beca'

class Semestre(models.Model):
    idsemestre_int = models.AutoField(db_column='idSemestre_int', primary_key=True)  # Field name made lowercase.
    nombre_str = models.CharField(max_length=15, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'semestre'

