from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
from ModelBase.models import ModeloBase

class Maquina(ModeloBase):
    ESTADOS_CHOICES = [
        # En mayúsculas para diferenciar de los estados en la base de datos
        ('OPERATIVA', 'Operativa y Sin Fallas'),
        ('DAÑADA_OPERATIVA', 'Dañada pero Operativa (Con Fallas)'),
        ('DAÑADA', 'Dañada y No Operativa (No Funciona)'),
        ('MANTENIMIENTO', 'En Mantenimiento o Reparación'),
        ('OBSERVACION', 'En Observación o Pruebas de Funcionamiento'),
        ('PRUEBAS', 'Realizando Pruebas de Funcionamiento (No Disponible)'),
    ]

    PISO_CHOICES = [
        ('PISO_1', 'Piso 1'),
        ('PISO_2', 'Piso 2'),
        ('PISO_3', 'Piso 3'),
        ('PISO_4', 'Piso 4'),
        ('PLANTA_BAJA', 'Planta Baja'),
        ('VIP', 'Área VIP'),
        ('TERRAZA', 'Terraza'),
        ('SOTANO', 'Sótano'),
        ('OTRO', 'Otro'),
    ]

    SALA_CHOICES = [
        ('SALA_A', 'Sala A'),
        ('SALA_B', 'Sala B'),
        ('SALA_C', 'Sala C'),
        ('SALA_D', 'Sala D'),
        ('SALA_PRINCIPAL', 'Sala Principal'),
        ('ZONA_FUMADORES', 'Zona Fumadores'),
        ('ZONA_NO_FUMADORES', 'Zona No Fumadores'),
        ('ZONA_ALTA_DENOMINACION', 'Zona Alta Denominación'),
        ('BAR', 'Bar / Restaurante'),
        ('ENTRADA', 'Entrada / Lobby'),
        ('OTRO', 'Otro'),
    ]

    # Relaciones
    modelo = models.ForeignKey(
        'ModelosMaquinas.ModeloMaquina', 
        on_delete=models.PROTECT, 
        related_name='maquinas',
        help_text="Modelo específico de la máquina, con detalles técnicos y características"
    )
    casino = models.ForeignKey(
        'Casinos.Casino', 
        related_name='maquinas', 
        on_delete=models.CASCADE,
        help_text="Casino al que pertenece esta máquina"
    )

    denominaciones = models.ManyToManyField(
        'Denominaciones.Denominacion', 
        related_name='maquinas',
        help_text="Denominaciones aceptadas por la máquina (puede ser múltiple)"
    )
    
    # Identificadores y Red
    uid_sala = models.CharField(
        max_length=20,
        help_text="Identificador único dentro de la sala del casino (ej. A01, B12)"
    )
    numero_serie = models.CharField(
        max_length=100, 
        help_text="Número de serie único de la máquina"
    )
    ip_maquina = models.GenericIPAddressField(
        help_text="Dirección IP asignada a la máquina (opcional, pero debe ser única si se proporciona)"
    )
    juego = models.CharField(
        max_length=150,
        help_text="Nombre del juego o título que ofrece la máquina o MULTIJUEGO"
    )
    
    # Ubicación Física y Layout (Cuadrícula Enteros Positivos)
    ubicacion_piso = models.CharField(
        max_length=50,
        choices=PISO_CHOICES,
        default='PISO_1',
        help_text="Piso donde se encuentra la máquina (selección predefinida)"
    )
    ubicacion_sala = models.CharField(
        max_length=100,
        choices=SALA_CHOICES,
        default='SALA_PRINCIPAL',
        help_text="Sala o sección específica dentro del piso del casino (selección predefinida)"
    )
    coordenada_x = models.PositiveIntegerField(
        default=0,
        help_text="Coordenada X en la cuadrícula del piso del casino (entero positivo)"
    )
    coordenada_y = models.PositiveIntegerField(
        default=0,
        help_text="Coordenada Y en la cuadrícula del piso del casino (entero positivo)"
    )
    
    # Estado Técnico
    estado_actual = models.CharField(
        max_length=30, 
        choices=ESTADOS_CHOICES, 
        default='OPERATIVA',
        help_text="Estado técnico actual de la máquina"
    )
    contador_fallas = models.PositiveIntegerField(
        default=0,
        help_text="Contador de fallas encontradas en la máquina"
    )
    ultimo_mantenimiento = models.DateField(
        null=True, blank=True,
        help_text="Fecha del último mantenimiento realizado a la máquina"
    )
    fecha_vencimiento_licencia = models.DateField(
        null=True, blank=True,
        help_text="Fecha de vencimiento de la licencia de uso de la máquina"
    )


    class Meta:
        db_table = 'maquinas'
        unique_together = ('casino', 'uid_sala')

    def clean(self):
        """Validación de identificadores y ubicaciones."""
        # Unicidad de IP por casino
        if self.ip_maquina:
            exists_ip = Maquina.objects.filter(
                casino=self.casino,
                ip_maquina=self.ip_maquina
            ).exclude(id=self.id).exists()
            if exists_ip:
                raise ValidationError({"ip_maquina": f"La IP {self.ip_maquina} ya está en uso en este casino."})
                
        # Unicidad de numero de serie por casino
        if self.numero_serie:
            exists_serie = Maquina.objects.filter(
                casino=self.casino,
                numero_serie=self.numero_serie
            ).exclude(id=self.id).exists()
            if exists_serie:
                raise ValidationError({"numero_serie": f"El número de serie {self.numero_serie} ya está registrado en este casino."})
            
        # Validación de fechas: Último mantenimiento no puede ser futuro, vencimiento licencia no puede ser pasado
        if self.ultimo_mantenimiento and self.ultimo_mantenimiento > date.today():
            raise ValidationError({"ultimo_mantenimiento": "La fecha del último mantenimiento no puede ser futura."})
        if self.fecha_vencimiento_licencia and self.fecha_vencimiento_licencia < date.today():
            raise ValidationError({"fecha_vencimiento_licencia": "La fecha de vencimiento de la licencia no puede ser pasada."})

        # Validación campos requeridos
        if not self.ubicacion_piso:
            raise ValidationError({"ubicacion_piso": "El piso es requerido."})
        if not self.ubicacion_sala:
            raise ValidationError({"ubicacion_sala": "La sala es requerida."})
        if self.coordenada_x is None or self.coordenada_y is None:
            raise ValidationError("Las coordenadas X e Y son requeridas.")

        if self.coordenada_x < 0 or self.coordenada_y < 0:
            raise ValidationError("Las coordenadas X e Y deben ser enteros positivos.")
            
        if self.coordenada_x > self.casino.grid_width or self.coordenada_y > self.casino.grid_height:
            raise ValidationError(
                "Las coordenadas X e Y no pueden exceder los límites configurados en el mapa del casino "
                f"({self.casino.grid_width}x{self.casino.grid_height})."
            )
            
        # Validación coordenadas únicas por piso y sala en el mismo casino
        exists_coordenada = Maquina.objects.filter(
            casino=self.casino,
            ubicacion_sala=self.ubicacion_sala,
            ubicacion_piso=self.ubicacion_piso,
            coordenada_x=self.coordenada_x,
            coordenada_y=self.coordenada_y
        ).exclude(id=self.id).exists()
        
        if exists_coordenada:
            raise ValidationError("Ya existe una máquina con las mismas coordenadas en esta sala y piso del casino.")

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        
        if not update_fields:
            # Solo validar si no se especifican campos específicos
            self.full_clean()
        
        super().save(*args, **kwargs)
