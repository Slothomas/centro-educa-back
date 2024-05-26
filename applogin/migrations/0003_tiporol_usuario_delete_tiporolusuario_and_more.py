# Generated by Django 5.0.6 on 2024-05-20 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applogin', '0002_tiporolusuario_usuarios_delete_tiporol_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tiporol',
            fields=[
                ('idtiporol_int', models.AutoField(db_column='idTipoRol_int', primary_key=True, serialize=False)),
                ('nombre_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=100, null=True)),
            ],
            options={
                'db_table': 'tipoRol',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('idusuario_int', models.AutoField(db_column='idUsuario_int', primary_key=True, serialize=False)),
                ('rut_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=20, null=True)),
                ('contrasena_str', models.CharField(blank=True, db_collation='Modern_Spanish_CI_AS', max_length=20, null=True)),
                ('fechacreacion_dat', models.DateField(blank=True, db_column='fechaCreacion_dat', null=True)),
                ('fechaultimoacceso_dat', models.DateField(blank=True, db_column='fechaUltimoAcceso_dat', null=True)),
            ],
            options={
                'db_table': 'usuario',
                'managed': False,
            },
        ),
        migrations.DeleteModel(
            name='TiporolUsuario',
        ),
        migrations.DeleteModel(
            name='Usuarios',
        ),
    ]
