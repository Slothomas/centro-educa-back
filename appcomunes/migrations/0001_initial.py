# Generated by Django 5.0.6 on 2024-05-25 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Anio',
            fields=[
                ('idanio_int', models.AutoField(db_column='idAnio_int', primary_key=True, serialize=False)),
                ('numero_int', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'anio',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Beca',
            fields=[
                ('idbeca_int', models.AutoField(db_column='idBeca_int', primary_key=True, serialize=False)),
                ('cobertura_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=10, null=True)),
                ('montocobertura_int', models.IntegerField(blank=True, db_column='montoCobertura_int', null=True)),
                ('fechaotorgamiento_dat', models.DateField(blank=True, db_column='fechaOtorgamiento_dat', null=True)),
                ('fechavencimiento_dat', models.DateField(blank=True, db_column='fechaVencimiento_dat', null=True)),
            ],
            options={
                'db_table': 'beca',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Certificacion',
            fields=[
                ('idcertificacion_int', models.AutoField(db_column='idCertificacion_int', primary_key=True, serialize=False)),
                ('nombre_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=50, null=True)),
                ('lugarobtenido_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', db_column='lugarObtenido_str', max_length=100, null=True)),
                ('vigente_boo', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'certificacion',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Comuna',
            fields=[
                ('idcomuna_int', models.AutoField(db_column='idComuna_int', primary_key=True, serialize=False)),
                ('nombre_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=50, null=True)),
            ],
            options={
                'db_table': 'comuna',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Nivelsocioeconomico',
            fields=[
                ('idnivelsocioeconomico_int', models.AutoField(db_column='idNivelSocioEconomico_int', primary_key=True, serialize=False)),
                ('nombre_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=50, null=True)),
            ],
            options={
                'db_table': 'nivelSocioEconomico',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('idpais_int', models.AutoField(db_column='idPais_int', primary_key=True, serialize=False)),
                ('nombre_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=50, null=True)),
                ('nacionalidad_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=50, null=True)),
            ],
            options={
                'db_table': 'pais',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('idregion_int', models.AutoField(db_column='idRegion_int', primary_key=True, serialize=False)),
                ('numregion_int', models.IntegerField(blank=True, db_column='numRegion_int', null=True)),
                ('nombre_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=50, null=True)),
            ],
            options={
                'db_table': 'region',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Semestre',
            fields=[
                ('idsemestre_int', models.AutoField(db_column='idSemestre_int', primary_key=True, serialize=False)),
                ('nombre_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=15, null=True)),
            ],
            options={
                'db_table': 'semestre',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tipobeca',
            fields=[
                ('idtipobeca_int', models.AutoField(db_column='idTipoBeca_int', primary_key=True, serialize=False)),
                ('nombre_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=50, null=True)),
                ('monto_int', models.IntegerField(blank=True, null=True)),
                ('porcentaje_int', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tipoBeca',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tipoestado',
            fields=[
                ('idtipoestado_int', models.AutoField(db_column='idTipoEstado_int', primary_key=True, serialize=False)),
                ('nombre_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=50, null=True)),
            ],
            options={
                'db_table': 'tipoEstado',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tipoprofesion',
            fields=[
                ('idtipoprofesion_int', models.AutoField(db_column='idTipoProfesion_int', primary_key=True, serialize=False)),
                ('nombre_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=50, null=True)),
            ],
            options={
                'db_table': 'tipoProfesion',
                'managed': False,
            },
        ),
    ]
