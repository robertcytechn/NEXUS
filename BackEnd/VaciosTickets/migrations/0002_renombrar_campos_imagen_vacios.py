# Migración manual: renombra los campos de imagen de TicketVacio para
# reflejar la nueva nomenclatura operativa del módulo de Vacíos.
# Se usa RenameField para preservar los datos existentes en la BD.

import VaciosTickets.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VaciosTickets', '0001_initial'),
    ]

    operations = [
        # 1. foto_ultimas_operaciones → foto_ultimas_operaciones_cliente (Requerido)
        migrations.RenameField(
            model_name='ticketvacio',
            old_name='foto_ultimas_operaciones',
            new_name='foto_ultimas_operaciones_cliente',
        ),
        # 2. foto_carga_sistema → foto_sistema_carga_error (Requerido)
        migrations.RenameField(
            model_name='ticketvacio',
            old_name='foto_carga_sistema',
            new_name='foto_sistema_carga_error',
        ),
        # 3. foto_seguimiento_slot → foto_seguimiento_slot_maquina (Requerido)
        migrations.RenameField(
            model_name='ticketvacio',
            old_name='foto_seguimiento_slot',
            new_name='foto_seguimiento_slot_maquina',
        ),
        # 4. foto_recarga_error → foto_ultimas_operaciones_maquina (Opcional)
        migrations.RenameField(
            model_name='ticketvacio',
            old_name='foto_recarga_error',
            new_name='foto_ultimas_operaciones_maquina',
        ),
        # 5. Hacer foto_ultimas_operaciones_maquina opcional (null=True, blank=True)
        migrations.AlterField(
            model_name='ticketvacio',
            name='foto_ultimas_operaciones_maquina',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=VaciosTickets.models.vacio_foto_upload,
                verbose_name='Foto: Últimas Operaciones de la Máquina (Opcional)',
                help_text='Captura opcional de las últimas operaciones registradas directamente en la máquina',
            ),
        ),
    ]
