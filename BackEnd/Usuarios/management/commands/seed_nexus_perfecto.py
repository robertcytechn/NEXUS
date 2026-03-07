"""
=============================================================================
NEXUS — Script de Seeding PERFECTO v2.0
Management Command: seed_nexus_perfecto
=============================================================================
Genera un entorno de pruebas completo, realista y 100% coherente con la
lógica de negocio del sistema (últimos 90 días).

Uso:
    python manage.py seed_nexus_perfecto
    python manage.py seed_nexus_perfecto --flush   (limpia datos del seed prev.)
=============================================================================
"""

import random
import io
from datetime import timedelta, date, datetime
from decimal import Decimal
from pathlib import Path
from django.conf import settings

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.core.files.base import ContentFile

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES GLOBALES
# ─────────────────────────────────────────────────────────────────────────────

NOW   = timezone.now()
TODAY = NOW.date()

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE FECHA / UTILIDADES
# ─────────────────────────────────────────────────────────────────────────────

def rand_dt(start=None, end=None):
    s = start or (NOW - timedelta(days=90))
    e = end   or NOW
    if isinstance(s, date) and not isinstance(s, datetime):
        s = timezone.make_aware(datetime.combine(s, datetime.min.time()))
    if isinstance(e, date) and not isinstance(e, datetime):
        e = timezone.make_aware(datetime.combine(e, datetime.min.time()))
    delta = int((e - s).total_seconds())
    return s + timedelta(seconds=random.randint(0, max(delta, 1)))


def rand_date(start=None, end=None):
    s = start or TODAY - timedelta(days=90)
    e = end   or TODAY
    delta = (e - s).days
    return s + timedelta(days=random.randint(0, max(delta, 0)))


def ip_unica(pool):
    for _ in range(5000):
        ip = f"192.168.{random.randint(1, 20)}.{random.randint(2, 254)}"
        if ip not in pool:
            pool.add(ip)
            return ip
    raise RuntimeError("No se pudo generar IP única")


def serie_unica(pool, prefijo="SN"):
    for _ in range(5000):
        s = f"{prefijo}-{random.randint(10000, 99999)}-{random.randint(100, 999)}"
        if s not in pool:
            pool.add(s)
            return s
    raise RuntimeError("No se pudo generar serie única")


def fake_pdf_bytes():
    return (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\ntrailer<</Size 4/Root 1 0 R>>\n%%EOF"
    )


def fake_png_bytes():
    return (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'
        b'\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx'
        b'\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00'
        b'\x00IEND\xaeB`\x82'
    )


# ─────────────────────────────────────────────────────────────────────────────
# DATOS REALISTAS FIJOS (sin Faker para coherencia)
# ─────────────────────────────────────────────────────────────────────────────

NOMBRES_H = ["Carlos", "Roberto", "Miguel", "Juan", "Alejandro", "Daniel", "Fernando",
             "Luis", "Eduardo", "Ricardo", "Mario", "Sergio", "Javier", "Antonio", "Héctor"]
NOMBRES_M = ["Ana", "María", "Laura", "Sofía", "Gabriela", "Patricia", "Claudia",
             "Diana", "Mónica", "Verónica", "Sandra", "Leticia", "Rosa", "Carmen", "Alicia"]
AP_PAT    = ["González", "Martínez", "López", "García", "Hernández", "Pérez", "Rodríguez",
             "Sánchez", "Ramírez", "Torres", "Flores", "Morales", "Jiménez", "Vargas", "Castro"]
AP_MAT    = ["Cruz", "Reyes", "Mendoza", "Ortega", "Gutiérrez", "Vega", "Ramos",
             "Medina", "Aguilar", "Navarro", "Ruiz", "Estrada", "Campos", "Nava", "Leal"]

def nombre_aleatorio():
    pool = NOMBRES_H + NOMBRES_M
    return random.choice(pool)

def ap_pat_aleatorio():
    return random.choice(AP_PAT)

def ap_mat_aleatorio():
    return random.choice(AP_MAT)


# Juegos realistas de slots
JUEGOS_SLOTS = [
    "Buffalo Gold Revolution",
    "Lightning Link — Happy Lantern",
    "Dragon Link — Golden Century",
    "Wheel of Fortune — Triple Extreme Spin",
    "Zeus III",
    "Quick Hit Platinum",
    "Cleopatra Plus",
    "Lobstermania 2",
    "Double Diamond",
    "Wild Cherry",
    "Super Times Pay Hot Roll",
    "Fu Dai Lian Lian — Panda",
    "50 Lions Gold",
    "More Chilli",
    "5 Dragons Gold",
    "Panda Magic",
    "Lightning Cash — Big Wins",
    "Ainsworth A640 — Cash Express",
    "MULTIJUEGO — 20 títulos",
    "Heart of Vegas — Golden Gems",
]

# Subcategorías realistas de tickets
TICKET_SUBCATS = {
    "hardware": [
        "Billetero JCM trabado",
        "Pantalla táctil sin respuesta",
        "Tarjeta madre no arranca",
        "Fuente de poder sin voltaje",
        "Módulo RAM dañado",
        "Disco SSD con error de lectura",
        "Printers de ticket atascado",
        "Botón de apuesta físico roto",
        "Placa de video con artefactos",
        "Ventilador interno ruidoso",
    ],
    "perifericos": [
        "Lector de tarjeta TITO sin comunicación",
        "Canopy LED superior apagado",
        "Altavoces sin audio",
        "Botón de llamada a atencionista inactivo",
        "Sensor de billete mal calibrado",
        "Touch externo desalineado",
        "Puerto USB bloqueado",
        "Impresora de tickets sin papel",
    ],
    "software": [
        "Error de RAM al iniciar juego",
        "Cuelgue en pantalla de bienvenida",
        "Error código E-032 en billetero",
        "SAS sin comunicación con servidor",
        "Actualización de firmware fallida",
        "Corrupción de tabla de pagos",
        "Error de certificación de software",
        "Log de errores lleno al 100%",
    ],
    "red": [
        "Pérdida de comunicación SAS",
        "IP duplicada detectada en red",
        "Cable de red dañado — sin enlace",
        "Switch de sala sin respuesta",
        "Latencia excesiva al servidor",
        "Certificado SSL vencido en sistema",
    ],
    "otros": [
        "Revisión general solicitada por gerencia",
        "Verificación post-mantenimiento preventivo",
        "Inspección por auditoría externa",
        "Revisión por queja de cliente",
    ],
}

# Descripciones técnicas realistas por categoría
DESCRIPCIONES_TICKET = {
    "hardware": [
        "El técnico detecta que el billetero JCM no acepta billetes y presenta luz de error intermitente. "
        "Se sospecha del sensor de transporte obstruido por suciedad acumulada.",
        "La máquina no enciende correctamente; al presionar el botón de encendido la fuente emite un clic "
        "pero los indicadores LED no responden. Se requiere revisión de fuente y cableado interno.",
        "Pantalla táctil reportada por el cliente como 'fantasma': registra toques sin que el usuario interactúe. "
        "Se requiere remplazo de digitalizador.",
        "Tarjeta de video presenta artefactos visuales en la pantalla principal; el juego se ve corrupto "
        "con píxeles aleatorios en zonas de animación.",
    ],
    "perifericos": [
        "El lector de tarjetas TITO no responde al insertar vouchers; el sistema reporta timeout de "
        "comunicación serial. Se probaron diferentes tickets sin éxito.",
        "Los altavoces internos no emiten audio aunque el sistema de sonido aparece activo. "
        "Se verifica que el cable de audio esté bien conectado y que el volumen no esté en cero.",
        "Impresora interna sin papel; se agotó el rollo durante la jornada. Requiere reposición inmediata "
        "y verificación del sensor de fin de papel.",
    ],
    "software": [
        "La máquina muestra error E-032 al arrancar: 'Billing device communication failure'. "
        "Los logs del sistema indican que el billetero no responde en el canal COM3.",
        "El juego reinicia solo cada 15–20 minutos aproximadamente. El log registra 'kernel panic' "
        "relacionado con módulo de red. Se requiere diagnóstico de software y posible reinstalación.",
        "La certificación de software no coincide con el hash del servidor. La máquina quedó bloqueada "
        "automáticamente por el sistema de integridad. Se requiere actualización desde USB autorizado.",
    ],
    "red": [
        "La máquina se desconectó del servidor SAS. El switch del rack de sala muestra el puerto "
        "correspondiente en orange. Se verifica el cable UTP y el estado del conector RJ45.",
        "Se detectó IP duplicada: esta máquina y la #A0234 tienen asignada la misma dirección "
        "192.168.10.45. Se requiere reconfiguración manual del DHCP.",
    ],
    "otros": [
        "Gerencia solicitó revisión general del equipo antes de la visita del regulador programada "
        "para la próxima semana. Incluir verificación de software, hardware y conectividad.",
        "Revisión post-turno: técnico entrante reporta que la máquina fue dejada en observación "
        "por el técnico anterior. Verificar el estado antes de reactivar.",
    ],
}

# Descripciones de bitácora realistas
BITACORA_TRABAJOS = [
    "Se retiró el billetero para limpieza profunda del sistema de transporte. Se encontraron dos billetes "
    "atrapados en el rodillo de entrada. Se limpió con aire comprimido y brocha antiestática.",

    "Se sustituyó la tarjeta de red de la unidad por una compatible de repuesto en stock. "
    "Se verificó comunicación SAS tras el cambio: prueba exitosa, la máquina recuperó enlace.",

    "Se realizó diagnóstico completo de la placa madre con el lector de POST codes. "
    "Se identificó falla en condensador C12 del módulo de alimentación. Pendiente orden de refacción.",

    "Se actualizó el firmware del billetero JCM de la versión 4.2.1 a 4.3.0 mediante USB autorizado. "
    "Posterior a la actualización se realizaron 10 pruebas de aceptación con resultados satisfactorios.",

    "Se calibró la pantalla táctil principal con la herramienta de ajuste del fabricante. "
    "Se realizaron 20 puntos de calibración. Touch responde con precisión después del ajuste.",

    "Se inspeccionó el cableado interno del gabinete. Se encontró cable de alimentación del ventilador "
    "con aislante dañado. Se realizó empalme y protección con termofit.",

    "Se verificó la configuración de red: IP, máscara y gateway correctos. Se reinició el servicio "
    "SAS y la máquina recuperó comunicación con el servidor central.",

    "Se realizó prueba de ciclo completo: arranque, carga de juego, apuesta de prueba, pago de prueba "
    "e impresión de ticket. Todos los procesos funcionaron sin errores.",

    "Se limpió el filtro de polvo del sistema de ventilación, se aplicó pasta térmica al procesador "
    "y se reemplazó el ventilador del disipador que presentaba ruido mecánico.",

    "Se revisó el sistema de audio: el amplificador estaba saturado por ganancia alta. "
    "Se ajustó el potenciómetro y se verificó la respuesta en frecuencia de los altavoces.",

    "Nota de seguimiento: se escaló el caso al proveedor IGT para solicitar diagnóstico remoto. "
    "Se abrió ticket de soporte con folio IGT-2026-4412 y número de serie del equipo.",

    "Se sustituyó la impresora de tickets interna por unidad de repuesto del almacén. "
    "Se verificó la alineación del papel y se imprimeron 5 tickets de prueba exitosamente.",
]

# Notas de cierre realistas
EXPLICACIONES_CIERRE = [
    "Máquina reparada y verificada. Billetero funcional, comunicación SAS establecida, "
    "prueba de ciclo completo aprobada. Se regresa a operación normal.",

    "Falla corregida mediante actualización de firmware. Equipo monitoreado por 2 horas "
    "sin recurrencia. Cerrado y devuelto a sala.",

    "Refacción instalada y probada. Equipo en condiciones óptimas. Documentado en bitácora "
    "de mantenimiento y actualizado en inventario de refacciones.",

    "Solución temporal implementada. Se programa revisión preventiva en 15 días para "
    "instalación de refacción definitiva solicitada al proveedor.",

    "Problema de red resuelto. IP reasignada via DHCP reservado. Se coordinó con IT central "
    "para actualizar la tabla de asignaciones. Máquina operativa.",
]

# Descripciones de incidencias
INCIDENCIAS_DATA = [
    ("Falla de suministro eléctrico zona norte", "electrica", "alta",
     "Se presentó corte de suministro eléctrico en la zona norte de la sala principal durante "
     "aproximadamente 35 minutos. Afectó 18 máquinas y el rack de comunicaciones #2. "
     "Personal de mantenimiento del edificio atendió el incidente; se identificó un breaker quemado "
     "en el tablero TF-04. Se realizó reemplazo y se restableció el servicio."),

    ("Gotera en techo sobre rack de servidores", "agua", "critica",
     "Se detectó filtración de agua desde el techo falso directamente sobre el rack principal "
     "de servidores. El incidente ocurrió tras lluvia intensa en la ciudad. Se protegió el equipo "
     "con plásticos de emergencia y se apagó el rack preventivamente. El servidor de operaciones "
     "fue migrado al rack secundario mientras se reparaba la filtración."),

    ("Falla del sistema de climatización central", "clima", "alta",
     "El chiller central del edificio presentó falla en el compresor, elevando la temperatura "
     "de la sala de máquinas a 31°C. Se activaron 4 unidades portátiles de climatización de respaldo. "
     "El proveedor Carrier fue contactado y acudió en 3 horas para diagnóstico."),

    ("Corte de enlace de internet principal", "red_externa", "media",
     "El proveedor de internet Telmex reportó corte en el enlace de fibra óptica que afecta la "
     "sede. La conectividad del sistema SAS operó en modo local durante 4 horas. "
     "Se activó el enlace de respaldo LTE mientras se reparaba la fibra."),

    ("Fisura en pared del site de servidores", "obra_civil", "baja",
     "Se detectó fisura superficial en la pared norte del cuarto de servidores, sin afectación "
     "estructural aparente pero con posible entrada de humedad. Se selló preventivamente con "
     "impermeabilizante y se programó revisión por parte del área de mantenimiento del edificio."),

    ("Elevación crítica de temperatura — Sala VIP", "clima", "critica",
     "El sensor de temperatura del área VIP registró 34°C por falla del minisplit sur. "
     "Se cerraron preventivamente 12 máquinas de alta denominación mientras se reparaba la unidad. "
     "El técnico de climatización del proveedor Daikin atendió en 90 minutos."),

    ("Pérdida de señal de red interna — Ala B", "red_externa", "media",
     "El switch del rack de sala ala B presentó falla parcial: 6 puertos quedaron sin señal. "
     "Se diagnosticó sobrecalentamiento del equipo. Se sustituyó por unidad de repuesto del almacén "
     "y se verificó conectividad en todas las máquinas afectadas."),

    ("Falla de UPS en rack principal", "electrica", "alta",
     "La UPS del rack principal entró en modo bypass por agotamiento de baterías. "
     "El equipo estuvo desprotegido ante fluctuaciones por 2 horas hasta la llegada del técnico "
     "de APC para reemplazo del banco de baterías. Se coordinó con gerencia para aprobación urgente."),

    ("Humedad excesiva detectada en sala de máquinas", "clima", "media",
     "El sensor de humedad registró 78% de HR en el piso de sala, por encima del límite recomendado "
     "de 60%. Se activaron deshumidificadores portátiles y se revisó el sellado de ventanas. "
     "La situación fue controlada en 6 horas sin afectación a equipos."),

    ("Corto circuito en tablero eléctrico secundario", "electrica", "alta",
     "Se presentó chispazo y olor a quemado en el tablero eléctrico secundario del pasillo técnico. "
     "Se desenergizó el tablero preventivamente. El electricista del edificio diagnosticó cable "
     "con aislante dañado que causó arco eléctrico. Reparado en 2 horas."),

    ("Inundación menor — trampa de grasa cocina", "agua", "media",
     "Agua proveniente de la trampa de grasa de la cocina colindante filtró hacia el corredor del "
     "área de cajas. No hubo afectación a equipos pero se requirió limpieza y sellado. "
     "Se notificó al administrador del edificio para solución permanente."),

    ("Revisión general del sistema CCTV", "otros", "baja",
     "Durante la revisión rutinaria del sistema de cámaras de seguridad se detectaron 3 cámaras "
     "con imagen degradada. Posible falla en convertidores de balun. Pendiente sustitución "
     "programada con el proveedor de seguridad electrónica."),
]

# Actividades de auditorías externas
ACTIVIDADES_AUDITORIA = [
    "Se realizó mantenimiento preventivo del sistema de aire acondicionado: limpieza de filtros, "
    "verificación de niveles de refrigerante, medición de temperaturas de operación y ajuste de termostatos.",

    "Renovación del contrato de internet y revisión del enlace de fibra óptica: pruebas de velocidad, "
    "latencia y verificación de redundancia. Se realizó failover test del enlace de respaldo.",

    "Mantenimiento del sistema UPS: sustitución de 8 baterías del banco principal, calibración del "
    "inversor y prueba de autonomía de 15 minutos bajo carga real del rack.",

    "Revisión y actualización del sistema de CCTV: actualización de firmware en 12 cámaras, "
    "verificación de almacenamiento en NVR y calibración de ángulos de cobertura.",

    "Fumigación y sanitización general de la sala: se aplicó tratamiento contra plagas "
    "en todas las áreas, incluyendo debajo de tarimas de máquinas y áreas de almacenamiento.",

    "Limpieza profunda especializada del site de servidores: uso de aspiradoras antiestáticas, "
    "limpieza de rejillas de ventilación, verificación de integridad del piso técnico.",

    "Revisión de instalación eléctrica: termografía de tableros, verificación de torques en conexiones, "
    "medición de resistencia de tierra física y documentación de carga en cada circuito.",

    "Instalación de cámaras adicionales en área de bóveda y pasillo de acceso técnico. "
    "Se verificó integración con el sistema central de monitoreo y grabación.",
]

# Colores de consola
class C:
    BOLD    = '\033[1m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    CYAN    = '\033[96m'
    RED     = '\033[91m'
    RESET   = '\033[0m'
    BLUE    = '\033[94m'
    MAGENTA = '\033[95m'


def banner(text):
    print(f"\n{C.CYAN}{C.BOLD}{'═'*62}{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}  {text}{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}{'═'*62}{C.RESET}")


def ok(text):
    print(f"  {C.GREEN}✓{C.RESET} {text}")


def info(text):
    print(f"  {C.YELLOW}→{C.RESET} {text}")


# ═════════════════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = "Siembra la BD con datos realistas, coherentes y listos para presentación."

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true',
                            help='Elimina datos del seed anterior antes de sembrar.')

    def handle(self, *args, **options):
        banner("NEXUS — SEEDING PERFECTO v2.0  [casino: pruebas]")
        info(f"Fecha base: {TODAY}  |  Rango: últimos 90 días")
        info("Modo seguro: NO se modifican datos existentes — todo va al casino 'pruebas'")

        if options.get('flush'):
            self._flush()

        with transaction.atomic():
            casino      = self._casino()

            # ── GUARDIA: abortar si el casino 'pruebas' ya fue sembrado ──
            from Maquinas.models import Maquina
            if not options.get('flush') and Maquina.objects.filter(casino=casino).exists():
                self.stdout.write(
                    f"\n{C.YELLOW}⚠  El casino 'pruebas' ya contiene datos sembrados.\n"
                    f"   Use --flush para limpiar y resembrar.{C.RESET}\n"
                )
                return
            # ────────────────────────────────────────────────────────────
            roles       = self._cargar_roles()
            denoms      = self._cargar_denominaciones()
            proveedores = self._proveedores(casino)
            modelos     = self._modelos(proveedores)
            maquinas    = self._maquinas(casino, modelos, denoms)
            usuarios    = self._usuarios(casino, roles)
            self._config_vacios(casino)
            tickets     = self._tickets(maquinas, usuarios)
            self._bitacoras(tickets, usuarios)
            self._incidencias(casino, usuarios)
            self._auditorias(casino, proveedores, usuarios)
            self._notificaciones(casino, usuarios, roles)
            self._wikis(usuarios, casino, modelos)
            self._vacios(casino, maquinas, usuarios)
            self._mantenimientos(maquinas, usuarios)
            self._relevos(casino, usuarios)
            self._tareas_especiales(casino, usuarios)
            self._inventario(casino)
            self._recompensas(casino, usuarios)
            self._evolucion_nexus(usuarios)

        self._resumen(usuarios)

    # ─────────────────────────────────────────────────────────────────────────
    # FLUSH
    # ─────────────────────────────────────────────────────────────────────────

    def _flush(self):
        banner("LIMPIEZA DE DATOS SEED ANTERIORES")
        from BitacoraTecnica.models import BitacoraTecnica
        from VaciosTickets.models import TicketVacio, ConfiguracionCasino
        from MantenimientosPreventivos.models import MantenimientoPreventivo
        from RelevosTurnos.models import RelevoTurno
        from TareasEspeciales.models import TareaEspecial
        from AuditoriasExternas.models import AuditoriaServicioExterno
        from Wiki.models import WikiTecnica
        from Gamificacion.models import CanjeRecompensa, RecompensaGamificacion
        from Tickets.models import Ticket
        from Notificaciones.models import Notificacion, NotificacionUsuario
        from IncidenciasInfraestructura.models import IncidenciaInfraestructura
        from EvolucionNexus.models import EvolucionNexus
        from InventarioSala.models import InventarioSala
        from Usuarios.models import Usuarios
        from Casinos.models import Casino
        from ModelosMaquinas.models import ModeloMaquina
        from Proveedores.models import Proveedor
        from Maquinas.models import Maquina

        seed_users = Usuarios.objects.filter(username__startswith='prueba_')
        casino_seed = Casino.objects.filter(nombre="pruebas").first()

        for m in [BitacoraTecnica, TicketVacio, MantenimientoPreventivo, RelevoTurno,
                  TareaEspecial, AuditoriaServicioExterno, WikiTecnica, CanjeRecompensa]:
            try:
                cnt = m.objects.filter(
                    **{list(m._meta.get_fields())[0].name + '__in': seed_users}
                ).delete()[0]
            except Exception:
                pass

        for u in seed_users:
            NotificacionUsuario.objects.filter(usuario=u).delete()
            Notificacion.objects.filter(usuario_destino=u).delete()
            EvolucionNexus.objects.filter(usuario=u).delete()
            Ticket.objects.filter(reportante=u).delete()
            BitacoraTecnica.objects.filter(usuario_tecnico=u).delete()
            TicketVacio.objects.filter(tecnico_creador=u).delete()
            MantenimientoPreventivo.objects.filter(tecnico_responsable=u).delete()
            RelevoTurno.objects.filter(tecnico_saliente=u).delete()
            TareaEspecial.objects.filter(creado_por_usuario=u).delete()
            AuditoriaServicioExterno.objects.filter(supervisor_interno=u).delete()
            WikiTecnica.objects.filter(autor=u).delete()

        if casino_seed:
            for m in Maquina.objects.filter(casino=casino_seed):
                m.denominaciones.clear()
            Maquina.objects.filter(casino=casino_seed).delete()
            prv = Proveedor.objects.filter(casino=casino_seed)
            ModeloMaquina.objects.filter(proveedor__in=prv).delete()
            prv.delete()
            IncidenciaInfraestructura.objects.filter(casino=casino_seed).delete()
            ConfiguracionCasino.objects.filter(casino=casino_seed).delete()
            InventarioSala.objects.filter(casino=casino_seed).delete()
            RecompensaGamificacion.objects.filter(casino=casino_seed).delete()
            Notificacion.objects.filter(casino_destino=casino_seed).delete()
            casino_seed.delete()

        seed_users.delete()
        ok("Limpieza completa")

    # ─────────────────────────────────────────────────────────────────────────
    # CASINO
    # ─────────────────────────────────────────────────────────────────────────

    def _casino(self):
        banner("PASO 1 — Casino de Pruebas")
        from Casinos.models import Casino
        casino, created = Casino.objects.get_or_create(
            nombre="pruebas",
            defaults={
                'identificador': 'PRB-001',
                'direccion': 'Entorno de Pruebas — Sin Dirección Real',
                'ciudad': 'Pruebas, México',
                'telefono': '000-000-0000',
                'encargado': 'Sistema NEXUS — Datos de Prueba',
                'horario_apertura': '00:00',
                'horario_cierre': '23:59',
                'grid_width': 50,
                'grid_height': 50,
            }
        )
        ok(f"Casino '{casino.nombre}' — {'Creado' if created else 'Ya existía'}")
        return casino

    # ─────────────────────────────────────────────────────────────────────────
    # ROLES (usa los existentes)
    # ─────────────────────────────────────────────────────────────────────────

    def _cargar_roles(self):
        banner("PASO 2 — Roles (leyendo existentes)")
        from Roles.models import Rol
        roles = {r.nombre: r for r in Rol.objects.all()}
        for nombre in roles:
            ok(f"Rol cargado: '{nombre}' (nivel {roles[nombre].nivel_jerarquia})")
        return roles

    # ─────────────────────────────────────────────────────────────────────────
    # DENOMINACIONES (usa las existentes)
    # ─────────────────────────────────────────────────────────────────────────

    def _cargar_denominaciones(self):
        banner("PASO 3 — Denominaciones (leyendo existentes)")
        from Denominaciones.models import Denominacion
        denoms = list(Denominacion.objects.all())
        ok(f"{len(denoms)} denominaciones disponibles")
        return denoms

    # ─────────────────────────────────────────────────────────────────────────
    # PROVEEDORES
    # ─────────────────────────────────────────────────────────────────────────

    def _proveedores(self, casino):
        banner("PASO 4 — Proveedores de Equipos")
        from Proveedores.models import Proveedor

        datos = [
            ("IGT de México S. de R.L.",           "IGT180429HG3", "soporte@igt-mexico.com.mx",
             "800-IGT-SOPORTE", "soporte-tecnico@igt-mexico.com.mx", "Ing. Carlos Vidal Montes",
             "igt_ccm", "Igt@2026"),
            ("Aristocrat Technologies México",       "ATM210630MX1", "atencion@aristocrat.mx",
             "55-5555-1234", "soporte@aristocrat.mx", "Ing. Luis Barrera Solis",
             "aristocrat_ccm", "Aris@2026"),
            ("Scientific Games Corp. S.A. de C.V.", "SGC200115NX8", "soporte@sgaming.mx",
             "55-4444-5678", "tech@sgaming.mx", "Ing. Sandra Palomino Ríos",
             "sgames_ccm", "ScGam@2026"),
            ("Novomatic de México",                  "NOM190820AB4", "soporte@novomatic.mx",
             "443-100-2200", "mantenimiento@novomatic.mx", "Ing. Roberto Fonseca Díaz",
             "novomatic_ccm", "Novo@2026"),
            ("Konami Gaming México",                 "KGM210930KZ3", "servicio@konami-gaming.mx",
             "55-3333-9900", "tech@konami-gaming.mx", "Ing. Patricia Soria Leal",
             "konami_ccm", "Kon@2026"),
            ("Everi Holdings de México",             "EHM220101EV1", "soporte@everi.mx",
             "81-8888-7700", "field.service@everi.mx", "Ing. Jorge Salinas Peña",
             "everi_ccm", "Everi@2026"),
            ("AGS Systems México",                   "ASM211010AG5", "contacto@agsmex.com",
             "33-9999-4400", "soporte@agsmex.com", "Ing. Fernanda Zavala Cruz",
             "ags_ccm", "Ags@2026"),
            ("Ainsworth Technology México",          "ATM200720AI2", "soporte@ainsworth.mx",
             "55-6666-3300", "tech@ainsworth.mx", "Ing. Héctor Ibarra Vega",
             "ainsworth_ccm", "AinsW@2026"),
            ("Bally Technologies S.A. de C.V.",     "BTS181205BL7", "atencion@bally.mx",
             "33-7777-5500", "servicio@bally.mx", "Ing. Mónica Garza Núñez",
             "bally_ccm", "Bally@2026"),
            ("WMS Industries México",               "WIM190901WM9", "soporte@wms-mx.com",
             "55-2222-8800", "tech@wms-mx.com", "Ing. Eduardo Acosta Vidal",
             "wms_ccm", "WMS@2026"),
        ]

        proveedores = []
        for (nombre, rfc, email_corp, tel, email_sop, contacto, user, pwd) in datos:
            p, created = Proveedor.objects.get_or_create(
                casino=casino, nombre=nombre,
                defaults={
                    'rfc': rfc[:13],
                    'email_corporativo': email_corp,
                    'telefono_soporte': tel,
                    'email_soporte': email_sop,
                    'nombre_contacto_tecnico': contacto,
                    'username': user,
                    'password': pwd,
                }
            )
            proveedores.append(p)
            ok(f"Proveedor: {nombre}")
        return proveedores

    # ─────────────────────────────────────────────────────────────────────────
    # MODELOS DE MÁQUINAS
    # ─────────────────────────────────────────────────────────────────────────

    def _modelos(self, proveedores):
        banner("PASO 5 — Modelos de Máquinas")
        from ModelosMaquinas.models import ModeloMaquina

        catalogo = {
            "IGT de México S. de R.L.": [
                ("AVP Elite",    "Game King Multi-Denom",
                 "Gabinete vertical con monitor LCD 22\". Soporta multi-denominación y modo TITO."),
                ("Crystal Dual", "Crystal Dual Slant",
                 "Gabinete inclinado con doble pantalla 19\". Ideal para salas de alta denominación."),
                ("Crystal Slant","Crystal Slant Cabinet",
                 "Gabinete inclinado con pantalla única 21\". Diseño compacto para zonas de alta rotación."),
            ],
            "Aristocrat Technologies México": [
                ("MK6",    "Mark VI Upright",
                 "Gabinete clásico con pantalla CRT de 19\". Compatible con juegos de tercera generación."),
                ("Helix+", "Helix Plus Cabinet",
                 "Gabinete moderno con pantalla LCD 27\". Canopy LED integrado y sistema de sonido envolvente."),
                ("Arc",    "Arc Cabinet",
                 "Diseño curvo con doble pantalla. Pantalla secundaria de 14\" para bonos y jackpots."),
            ],
            "Scientific Games Corp. S.A. de C.V.": [
                ("Blade Compact",  "Blade Cabinet",
                 "Gabinete de perfil delgado con pantalla 22\". Optimize espacio en sala sin sacrificar calidad."),
                ("Dune Compact",   "Dune System",
                 "Plataforma multi-juego con pantalla curva 28\". Soporta contenido en streaming."),
                ("Pro Wave",       "Pro Wave Upright",
                 "Gabinete tipo wave con pantalla 32\" ultra ancha. Diseñado para juegos de video póker y slots."),
            ],
            "Novomatic de México": [
                ("Gaminator 40",  "Gaminator MultiLine",
                 "Plataforma estándar de 5 carretes con 40 líneas. Alta confiabilidad y bajo mantenimiento."),
                ("Coolfire II",   "Coolfire Cabinet",
                 "Diseño moderno con LCD 22\" y sistema de audio Dolby. Compatible con jackpots enlazados."),
                ("Dominator",     "Dominator Station",
                 "Gabinete de alta gama con doble monitor 24\". Sistema de sonido perimetral 360°."),
            ],
            "Konami Gaming México": [
                ("Podium 49",   "Podium Cabinet 49\"",
                 "Monitor curvo de 49\" para experiencia inmersiva. Sistema de bonificación SYNKROS."),
                ("Dimension 27","Dimension Cabinet",
                 "Gabinete con pantalla plana 27\" y control táctil. Compatible con sistema Synkros."),
                ("Concerto",    "Concerto Cabinet",
                 "Diseño de consola con asiento integrado. Ideal para salas premium y VIP."),
            ],
            "Everi Holdings de México": [
                ("TwinStar J43","TwinStar Cabinet",
                 "Pantalla dual de 43\". El panel superior sirve como pantalla de bonificación independiente."),
                ("Empire",      "Empire MX",
                 "Gabinete de tamaño estándar con pantalla 22\" y canopy personalizable."),
                ("Texan",       "Texan Station",
                 "Diseño compacto orientado a zonas de alto tráfico. Bajo consumo energético."),
            ],
            "AGS Systems México": [
                ("Orion Rise",  "Orion Rise Cabinet",
                 "Pantalla principal 43\" con pantalla del tótem superior. Sistema de jackpots enlazados."),
                ("Pax Slim",    "Pax S Slim",
                 "Gabinete ultra delgado ideal para salas con restricciones de espacio."),
                ("Alora",       "Alora Cabinet",
                 "Diseño redondeado con pantalla 27\" y sistema de retroiluminación LED RGB."),
            ],
            "Ainsworth Technology México": [
                ("A640",  "A640 Upright",
                 "Plataforma estándar de Ainsworth con pantalla 22\". Amplia biblioteca de juegos."),
                ("A680",  "A680 Cabinet",
                 "Versión mejorada del A640 con pantalla 27\" y sistema de bonos enlazados MLink."),
                ("A780",  "A780 Premium",
                 "Gabinete premium con pantalla dual 32\". Reservado para zonas VIP."),
            ],
            "Bally Technologies S.A. de C.V.": [
                ("Pro V32",     "Pro V32 Upright",
                 "Gabinete vertical con pantalla 32\" full HD. Soporta contenido en alta definición."),
                ("Alpha Pro",   "Alpha Pro V22",
                 "Versión compacta con pantalla 22\". Diseñado para zonas de alta densidad."),
                ("CineVision",  "CineVision Cabinet",
                 "Pantalla curva de alta resolución inspirada en cines IMAX. Experiencia visual premium."),
            ],
            "WMS Industries México": [
                ("Blade Server","Blade Server Cabinet",
                 "Plataforma servidor con hasta 4 estaciones de juego compartiendo hardware central."),
                ("CPU NXT3",   "CPU NXT3 Upright",
                 "Gabinete de tercera generación con pantalla 22\" y procesador Intel de alta velocidad."),
                ("Colossal",   "Colossal Reels Cabinet",
                 "Diseño especial para juegos de carretes colosales. Monitor vertical de 60\"."),
            ],
        }

        todos_modelos = []
        for prov in proveedores:
            for nombre_m, nombre_p, desc in catalogo.get(prov.nombre, []):
                m, created = ModeloMaquina.objects.get_or_create(
                    proveedor=prov, nombre_modelo=nombre_m,
                    defaults={'nombre_producto': nombre_p, 'descripcion': desc}
                )
                todos_modelos.append(m)
                ok(f"Modelo '{nombre_m}' — {prov.nombre}")
        return todos_modelos

    # ─────────────────────────────────────────────────────────────────────────
    # MÁQUINAS  (REGLA 2: piso PISO_1, sala ZONA_FUMADORES / ZONA_NO_FUMADORES,
    #            coordenadas únicas garantizadas por grid-set)
    # ─────────────────────────────────────────────────────────────────────────

    def _maquinas(self, casino, modelos, denoms):
        banner("PASO 6 — Máquinas (10 por modelo, coordenadas únicas)")
        from Maquinas.models import Maquina

        # Cargar coordenadas, IPs, series y UIDs ya usados en este casino
        qs_existentes = Maquina.objects.filter(casino=casino)
        # unicidad: (sala, piso, x, y) según la validación del modelo
        coord_set = {
            (m.ubicacion_sala, m.ubicacion_piso, m.coordenada_x, m.coordenada_y)
            for m in qs_existentes
        }
        ip_set    = set(Maquina.objects.values_list('ip_maquina', flat=True))
        serie_set = set(Maquina.objects.values_list('numero_serie', flat=True))
        uid_set   = set(qs_existentes.values_list('uid_sala', flat=True))
        maquinas  = []
        counter   = 1

        # Generar grilla dentro del mapa real del casino (leemos de BD)
        MAX_X = casino.grid_width
        MAX_Y = casino.grid_height

        def next_coord(sala, piso):
            for _ in range(50000):
                x = random.randint(0, MAX_X)
                y = random.randint(0, MAX_Y)
                key = (sala, piso, x, y)
                if key not in coord_set:
                    coord_set.add(key)
                    return x, y
            raise RuntimeError("Grid lleno — no hay celdas libres disponibles")

        DENOMINACIONES_COMUNES = [d for d in denoms if d.valor <= Decimal('5.00')]
        DENOMINACIONES_ALTAS   = [d for d in denoms if d.valor >= Decimal('1.00')]

        for modelo in modelos:
            for i in range(1, 11):
                # UID único
                uid = f"{modelo.nombre_modelo[:3].upper().replace(' ','')}{counter:04d}"
                while uid in uid_set:
                    counter += 1
                    uid = f"{modelo.nombre_modelo[:3].upper().replace(' ','')}{counter:04d}"
                uid_set.add(uid)

                ip    = ip_unica(ip_set)
                serie = serie_unica(serie_set, prefijo=modelo.proveedor.nombre[:3].upper())

                juego = random.choice(JUEGOS_SLOTS)
                sala  = random.choice(['ZONA_FUMADORES', 'ZONA_NO_FUMADORES'])
                cx, cy = next_coord(sala, 'PISO_1')

                # Estado mayoritariamente operativo (para coherencia)
                estado = random.choices(
                    ['OPERATIVA', 'DAÑADA_OPERATIVA', 'DAÑADA', 'MANTENIMIENTO', 'OBSERVACION', 'PRUEBAS'],
                    weights=[65, 15, 5, 8, 5, 2],
                    k=1
                )[0]

                maq = Maquina.objects.create(
                    modelo=modelo,
                    casino=casino,
                    uid_sala=uid,
                    numero_serie=serie,
                    ip_maquina=ip,
                    juego=juego,
                    ubicacion_piso='PISO_1',
                    ubicacion_sala=sala,
                    coordenada_x=cx,
                    coordenada_y=cy,
                    estado_actual=estado,
                    contador_fallas=random.randint(0, 15),
                    ultimo_mantenimiento=rand_date(
                        TODAY - timedelta(days=180), TODAY - timedelta(days=2)
                    ),
                    fecha_vencimiento_licencia=rand_date(
                        TODAY + timedelta(days=60), TODAY + timedelta(days=730)
                    ),
                )
                # Denominaciones coherentes con el tipo de área
                den_pool = DENOMINACIONES_ALTAS if sala == 'ZONA_FUMADORES' else DENOMINACIONES_COMUNES
                maq.denominaciones.set(random.sample(den_pool, k=min(3, len(den_pool))))
                maquinas.append(maq)
                counter += 1

        ok(f"{len(maquinas)} máquinas creadas  |  coords únicas garantizadas  |  Piso 1 exclusivo")
        return maquinas

    # ─────────────────────────────────────────────────────────────────────────
    # USUARIOS  (REGLA 3: puntos actuales == histórico desde día 1)
    # ─────────────────────────────────────────────────────────────────────────

    def _usuarios(self, casino, roles):
        banner("PASO 7 — Usuarios (contraseña: 123)")
        from Usuarios.models import Usuarios

        # Nombres específicos para el casino (realistas, no aleatorios)
        # Usernames prefijados con 'prueba_' para NO colisionar con usuarios reales
        perfiles = [
            # (nombres, ap_pat, ap_mat, username, email, rol_key, puntos)
            ("Carlos Eduardo",  "Mendoza",   "Ríos",      "prueba_cmendoza",    "TECNICO",        3200),
            ("Ana Gabriela",    "Torres",    "Vega",      "prueba_atorres",     "TECNICO",        2800),
            ("Roberto",         "Sánchez",   "Leal",      "prueba_rsanchez",    "TECNICO",        1500),
            ("Diana Paola",     "Flores",    "Medina",    "prueba_dflores",     "TECNICO",         850),
            ("Javier",          "Gutiérrez", "Campos",    "prueba_jgutierrez",  "TECNICO",         300),
            ("Ing. Marco A.",   "Romero",    "Castillo",  "prueba_mromero",     "SUP SISTEMAS",   4100),
            ("Lic. Sofía",      "Delgado",   "Navarro",   "prueba_sdelgado",    "SUP SISTEMAS",   2600),
            ("Lic. Eduardo",    "Villanueva","Mora",      "prueba_evillanueva", "ADMINISTRADOR",   500),
            ("Lic. Patricia",   "Guzmán",    "Estrada",   "prueba_pguzman",     "GERENCIA",        200),
            ("Ing. Alberto",    "Reyes",     "Fuentes",   "prueba_areyes",      "PROVEEDOR",        50),
            ("C. Ricardo",      "Morales",   "Jiménez",   "prueba_rmorales",    "OBSERVADOR",       80),
        ]

        usuarios_por_rol = {}
        for (nombres, ap_pat, ap_mat, username, rol_key, puntos) in [
            (p[0], p[1], p[2], p[3], p[4], p[5]) for p in perfiles
        ]:
            rol = roles.get(rol_key)
            if rol is None:
                info(f"  ⚠ Rol '{rol_key}' no encontrado, saltando usuario '{username}'")
                continue

            email = f"{username}@nexus.local"
            if Usuarios.objects.filter(username=username).exists():
                u = Usuarios.objects.get(username=username)
                info(f"  Usuario '{username}' ya existe, se reutiliza")
            else:
                # REGLA 3: crear con puntos_gamificacion = puntos
                # El override de save() sincronizará el histórico automáticamente
                u = Usuarios.objects.create_user(
                    username=username,
                    email=email,
                    password='123',
                    nombres=nombres,
                    apellido_paterno=ap_pat,
                    apellido_materno=ap_mat,
                    casino=casino,
                    rol=rol,
                    puntos_gamificacion=puntos,
                    EULAAceptada=True,
                )
                # Forzar que el histórico sea idéntico (congruencia matemática día 1)
                Usuarios.objects.filter(pk=u.pk).update(
                    puntos_gamificacion_historico=puntos
                )
                u.refresh_from_db()
                ok(f"  {username:<15} {rol_key:<18} {puntos:>5} pts")

            usuarios_por_rol.setdefault(rol_key, []).append(u)

        return usuarios_por_rol

    # ─────────────────────────────────────────────────────────────────────────
    # CONFIGURACIÓN VACÍOS
    # ─────────────────────────────────────────────────────────────────────────

    def _config_vacios(self, casino):
        from VaciosTickets.models import ConfiguracionCasino
        ConfiguracionCasino.objects.get_or_create(
            casino=casino,
            defaults={
                'umbral_autorizacion': Decimal('500.00'),
                'siempre_requiere_autorizacion': False,
            }
        )
        ok("Configuración de vacíos: umbral $500.00 MXN")

    # ─────────────────────────────────────────────────────────────────────────
    # TICKETS  (REGLA 4: estado_maquina_reportado coherente con estado_actual)
    # ─────────────────────────────────────────────────────────────────────────

    def _tickets(self, maquinas, usuarios_por_rol):
        banner("PASO 8 — 300 Tickets realistas")
        from Tickets.models import Ticket
        from Maquinas.models import Maquina

        tecnicos    = usuarios_por_rol.get('TECNICO', [])
        supervisores = usuarios_por_rol.get('SUP SISTEMAS', [])
        todos_reportantes = tecnicos + supervisores

        if not todos_reportantes:
            info("No hay usuarios reportantes disponibles")
            return []

        # Mapa estado máquina → estado del ticket coherente
        ESTADO_MAQ_A_TICKET = {
            'OPERATIVA':       ['cerrado', 'cerrado', 'cerrado'],
            'DAÑADA_OPERATIVA':['proceso', 'abierto', 'reabierto'],
            'DAÑADA':          ['abierto', 'abierto', 'proceso'],
            'MANTENIMIENTO':   ['proceso', 'espera'],
            'OBSERVACION':     ['proceso', 'espera'],
            'PRUEBAS':         ['espera', 'proceso'],
        }

        PRIORIDAD_POR_ESTADO = {
            'OPERATIVA':       ['baja', 'media'],
            'DAÑADA_OPERATIVA':['media', 'alta', 'alta'],
            'DAÑADA':          ['alta', 'critica', 'emergencia'],
            'MANTENIMIENTO':   ['media', 'alta'],
            'OBSERVACION':     ['baja', 'media'],
            'PRUEBAS':         ['baja', 'media'],
        }

        # Reservar folio base para no colisionar
        existing_count = Ticket.objects.count()
        tickets = []
        folio_counter = existing_count + 1

        for i in range(300):
            maquina   = random.choice(maquinas)
            estado_maq = maquina.estado_actual
            estado_tic = random.choice(ESTADO_MAQ_A_TICKET.get(estado_maq, ['abierto']))
            prioridad  = random.choice(PRIORIDAD_POR_ESTADO.get(estado_maq, ['media']))
            categoria  = random.choice(list(TICKET_SUBCATS.keys()))
            subcat     = random.choice(TICKET_SUBCATS[categoria])
            descripcion = random.choice(DESCRIPCIONES_TICKET.get(categoria, ["Problema reportado en máquina."]))
            reportante = random.choice(todos_reportantes)
            tecnico    = random.choice(tecnicos) if tecnicos else reportante
            fecha_tic  = rand_dt()

            folio = f"TKP-{fecha_tic.year}-{folio_counter:05d}"
            folio_counter += 1

            t = Ticket(
                maquina=maquina,
                reportante=reportante,
                tecnico_asignado=tecnico,
                folio=folio,
                categoria=categoria,
                subcategoria=subcat,
                prioridad=prioridad,
                descripcion_problema=descripcion,
                estado_maquina_reportado=estado_maq,
                estado_ciclo=estado_tic,
                notas_seguimiento=(
                    f"Revisado por {tecnico.nombres} el {rand_date()}" 
                    if random.random() > 0.3 else None
                ),
                explicacion_cierre=(
                    random.choice(EXPLICACIONES_CIERRE) if estado_tic == 'cerrado' else None
                ),
                contador_reaperturas=random.randint(1, 2) if estado_tic == 'reabierto' else 0,
            )
            t.save()
            Ticket.objects.filter(pk=t.pk).update(creado_en=fecha_tic)
            tickets.append(t)

        ok(f"300 tickets creados con estado coherente al estado de cada máquina")
        return tickets

    # ─────────────────────────────────────────────────────────────────────────
    # BITÁCORAS (Colaboración multi-técnico, 5 tickets estrés con 20 notas)
    # ─────────────────────────────────────────────────────────────────────────

    def _bitacoras(self, tickets, usuarios_por_rol):
        banner("PASO 9 — Bitácoras Técnicas (colaboración real)")
        from BitacoraTecnica.models import BitacoraTecnica

        tecnicos    = usuarios_por_rol.get('TECNICO', [])
        supervisores = usuarios_por_rol.get('SUP SISTEMAS', [])
        todos        = tecnicos + supervisores
        if not todos:
            info("Sin usuarios técnicos para bitácoras")
            return

        TIPOS     = ['correctiva', 'ajuste', 'instalacion', 'actualización', 'diagnostico']
        RESULTADOS = ['exitosa', 'parcial', 'fallida', 'espera_refaccion']
        ESTADOS_R  = ['operativa', 'dañada_operativa', 'dañada', 'mantenimiento']

        stress_tickets = random.sample(tickets, min(5, len(tickets)))
        total = 0

        for t in tickets:
            es_stress = t in stress_tickets
            n_notas   = 20 if es_stress else random.randint(1, 4)

            fecha_base = t.creado_en
            usuarios_del_ticket = random.sample(todos, min(3, len(todos)))

            for k in range(n_notas):
                es_ultima  = k == n_notas - 1
                autor      = usuarios_del_ticket[k % len(usuarios_del_ticket)]
                fecha_bit  = rand_dt(start=fecha_base,
                                     end=fecha_base + timedelta(hours=96))

                bita = BitacoraTecnica.objects.create(
                    ticket=t,
                    usuario_tecnico=autor,
                    tipo_intervencion=random.choice(TIPOS),
                    descripcion_trabajo=random.choice(BITACORA_TRABAJOS),
                    resultado_intervencion=random.choices(
                        RESULTADOS, weights=[55, 25, 10, 10], k=1
                    )[0],
                    estado_maquina_resultante=random.choice(ESTADOS_R),
                    finaliza_ticket=es_ultima and (t.estado_ciclo == 'cerrado'),
                )
                BitacoraTecnica.objects.filter(pk=bita.pk).update(creado_en=fecha_bit)
                total += 1

        ok(f"{total} entradas de bitácora creadas")
        ok(f"5 tickets de estrés con 20 anotaciones de diferentes técnicos")

    # ─────────────────────────────────────────────────────────────────────────
    # INCIDENCIAS DE INFRAESTRUCTURA
    # ─────────────────────────────────────────────────────────────────────────

    def _incidencias(self, casino, usuarios_por_rol):
        banner("PASO 10 — Incidencias de Infraestructura (12)")
        from IncidenciasInfraestructura.models import IncidenciaInfraestructura

        incidencias = []
        for (titulo, categ, severidad, desc) in INCIDENCIAS_DATA:
            hora_inicio = rand_dt()
            hora_fin    = (hora_inicio + timedelta(hours=random.randint(1, 8))
                           if severidad != 'critica' or random.random() > 0.3
                           else None)

            inc = IncidenciaInfraestructura.objects.create(
                casino=casino,
                titulo=titulo,
                categoria=categ,
                descripcion=desc,
                severidad=severidad,
                afecta_operacion=severidad in ('alta', 'critica'),
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
            )
            incidencias.append(inc)
            ok(f"  Incidencia: {titulo[:55]}")
        return incidencias

    # ─────────────────────────────────────────────────────────────────────────
    # AUDITORÍAS EXTERNAS
    # ─────────────────────────────────────────────────────────────────────────

    def _auditorias(self, casino, proveedores, usuarios_por_rol):
        banner("PASO 11 — Auditorías de Servicios Externos (8)")
        from AuditoriasExternas.models import AuditoriaServicioExterno

        supervisores = usuarios_por_rol.get('SUP SISTEMAS', [])
        if not supervisores:
            info("Sin supervisores para auditorías")
            return

        AREAS = ['site_servidores', 'racks_sala', 'area_maquinas',
                 'oficinas_tecnicas', 'jv', 'cajas']
        TIPOS = ['internet_enlaces', 'climatizacion', 'energia_ups',
                 'seguridad_cctv', 'limpieza_profunda', 'mantenimiento_equipo',
                 'fumigacion', 'obra_civil']

        tecnicos_externos = [
            ("Ing. Carlos Vidal Montes",      proveedores[0]),
            ("Ing. Luis Barrera Solis",       proveedores[1]),
            ("Ing. Sandra Palomino Ríos",     proveedores[2]),
            ("Ing. Roberto Fonseca Díaz",     proveedores[3]),
            ("Ing. Patricia Soria Leal",      proveedores[4]),
            ("Ing. Jorge Salinas Peña",       proveedores[5]),
            ("Ing. Fernanda Zavala Cruz",     proveedores[6]),
            ("Ing. Héctor Ibarra Vega",       proveedores[7]),
        ]

        for k, (nombre_ext, prov) in enumerate(tecnicos_externos):
            hora_entrada = rand_dt()
            hora_salida  = hora_entrada + timedelta(hours=random.randint(2, 7))

            AuditoriaServicioExterno.objects.create(
                casino=casino,
                empresa_proveedora=prov,
                nombre_tecnico_externo=nombre_ext,
                supervisor_interno=supervisores[k % len(supervisores)],
                area_acceso=random.choice(AREAS),
                tipo_servicio=TIPOS[k % len(TIPOS)],
                descripcion_actividad=ACTIVIDADES_AUDITORIA[k % len(ACTIVIDADES_AUDITORIA)],
                hora_entrada=hora_entrada,
                hora_salida=hora_salida,
            )
            ok(f"  Auditoría: {nombre_ext} — {prov.nombre[:30]}")

    # ─────────────────────────────────────────────────────────────────────────
    # NOTIFICACIONES
    # ─────────────────────────────────────────────────────────────────────────

    def _notificaciones(self, casino, usuarios_por_rol, roles):
        banner("PASO 12 — Notificaciones")
        from Notificaciones.models import Notificacion

        globales = [
            ("Sistema actualizado a v2.6",
             "Se actualizó la plataforma NEXUS. Nuevas funciones: Mapa de Sala mejorado, "
             "exportación PDF en bitácoras, y Salón de la Fama público. Revise las notas de versión.",
             'informativa', 'sistema'),
            ("Mantenimiento nocturno programado — Domingo 4:00 AM",
             "El servidor central estará fuera de servicio para mantenimiento preventivo el próximo "
             "domingo de 04:00 a 06:00 AM. Guarde su trabajo con anticipación.",
             'alerta', 'sistema'),
            ("Recordatorio: Nueva política de contraseñas activa",
             "A partir del 1 de abril, todas las contraseñas deberán tener mínimo 8 caracteres, "
             "una mayúscula y un número. Por favor actualice su contraseña en Perfil.",
             'informativa', 'sistema'),
            ("Alerta: Temperatura crítica en site de servidores",
             "Los sensores detectaron temperatura de 30°C en el site. Se activaron ventiladores "
             "de respaldo. Un técnico ya atiende el incidente. Monitorear la situación.",
             'urgente', 'infraestructura'),
            ("Backup nocturno completado exitosamente",
             "El respaldo automático de la base de datos del 6 de marzo se completó sin errores. "
             "Los datos están seguros en el servidor de respaldo remoto.",
             'informativa', 'sistema'),
            ("Auditoría regulatoria programada para el 20 de marzo",
             "La SEGOB realizará una auditoría de sistemas el día 20 de marzo. Por favor "
             "asegúrese de que toda la documentación técnica esté actualizada en el sistema.",
             'alerta', 'sistema'),
        ]

        for titulo, contenido, nivel, tipo in globales:
            Notificacion.objects.create(
                titulo=titulo, contenido=contenido,
                nivel=nivel, tipo=tipo,
                es_global=True, casino_destino=casino,
            )

        # Para técnicos
        rol_tec = roles.get('TECNICO')
        notifs_tecnicos = [
            ("Recordatorio: Mantenimiento preventivo mensual",
             "Esta semana corresponde el mantenimiento preventivo mensual de las máquinas de la "
             "fila H. Por favor completen el registro en el sistema antes del viernes.",
             'alerta', 'sistema'),
            ("Nueva guía en Wiki: Diagnóstico SAS para IGT AVP",
             "Se publicó una nueva guía técnica en la Wiki con el procedimiento paso a paso para "
             "diagnosticar y resolver errores de comunicación SAS en el modelo IGT AVP Elite.",
             'informativa', 'wiki'),
            ("Recordatorio: Actualización de inventario de refacciones",
             "El inventario de refacciones debe ser actualizado al final de cada turno. "
             "Por favor ingrese los consumibles utilizados en el módulo de Inventario de Sala.",
             'informativa', 'sistema'),
        ]
        for titulo, contenido, nivel, tipo in notifs_tecnicos:
            Notificacion.objects.create(
                titulo=titulo, contenido=contenido,
                nivel=nivel, tipo=tipo,
                casino_destino=casino,
                rol_destino=rol_tec,
            )

        # Personales para supervisores
        supervisores = usuarios_por_rol.get('SUP SISTEMAS', [])
        msgs_sup = [
            ("Reporte semanal pendiente de revisión",
             "Hay 3 tickets cerrados esta semana que requieren su firma de supervisión en el sistema "
             "antes del cierre del periodo. Por favor revíselos en la sección de Tickets."),
            ("Nuevo técnico asignado a su turno",
             "El técnico Carlos Mendoza ha sido reasignado al turno vespertino a partir del lunes. "
             "Por favor actualice el rol en el calendario y coordine el relevo."),
        ]
        for i, sup in enumerate(supervisores):
            if i < len(msgs_sup):
                titulo, contenido = msgs_sup[i]
                Notificacion.objects.create(
                    titulo=titulo, contenido=contenido,
                    nivel='alerta', tipo='sistema',
                    usuario_destino=sup,
                )

        ok(f"Notificaciones creadas: {6} globales + {len(notifs_tecnicos)} para técnicos + {len(supervisores)} personales")

    # ─────────────────────────────────────────────────────────────────────────
    # WIKI TÉCNICA
    # ─────────────────────────────────────────────────────────────────────────

    def _wikis(self, usuarios_por_rol, casino, modelos):
        banner("PASO 13 — Wiki Técnica (10 guías)")
        from Wiki.models import WikiTecnica

        tecnicos   = usuarios_por_rol.get('TECNICO', [])
        admins     = (usuarios_por_rol.get('ADMINISTRADOR', []) +
                      usuarios_por_rol.get('SUP SISTEMAS', []))

        guias = [
            ("Resolución de error E-032 en billetero JCM WBA",        "error_code",    "publicada",  200),
            ("Procedimiento de limpieza profunda del bill validator",  "limpieza",      "publicada",  100),
            ("Configuración de parámetros TITO en plataforma IGT",     "configuracion", "publicada",  150),
            ("Instalación y actualización de firmware — Novomatic",    "configuracion", "aprobada",   100),
            ("Diagnóstico de falla de comunicación SAS paso a paso",   "reparacion",    "publicada",  200),
            ("Calibración de pantalla táctil en gabinetes Ainsworth",  "configuracion", "publicada",  100),
            ("Guía de mantenimiento preventivo semanal estándar",      "limpieza",      "publicada",   50),
            ("Diccionario de códigos de error Aristocrat Helix+",      "error_code",    "aprobada",   150),
            ("Configuración de red SAS y DHCP reservado en sala",      "configuracion", "pendiente_revision", 0),
            ("Protocolo de entrega de turno sin errores",              "reparacion",    "publicada",   50),
        ]

        wikis = []
        for k, (titulo, categ, estado, puntos) in enumerate(guias):
            autor   = tecnicos[k % len(tecnicos)] if tecnicos else None
            revisor = admins[k % len(admins)] if admins and estado in ('aprobada', 'publicada', 'rechazada') else None
            modelo  = modelos[k % len(modelos)]

            if autor is None:
                continue

            # Usar el PDF real del directorio media si existe, sino generar bytes mínimos
            pdf_name = f"guia_{k+1:03d}.pdf"
            pdf_real = Path(settings.MEDIA_ROOT) / "wiki_tecnica" / "pdfs" / pdf_name
            if pdf_real.exists():
                pdf_content = pdf_real.read_bytes()
            else:
                pdf_content = fake_pdf_bytes()

            w = WikiTecnica(
                autor=autor,
                casino_origen=casino,
                modelo_relacionado=modelo,
                titulo_guia=titulo,
                categoria=categ,
                estado=estado,
                puntos_reconocimiento=puntos,
                revisada_por=revisor,
                fecha_revision=rand_dt() if revisor else None,
                nota_revision=(
                    "Excelente documentación. Aprobada para publicación general." if revisor else None
                ),
            )
            w.archivo_pdf.save(pdf_name,
                               ContentFile(pdf_content, name=pdf_name),
                               save=False)
            w.save()
            wikis.append(w)
            ok(f"  Wiki: {titulo[:55]}")
        return wikis

    # ─────────────────────────────────────────────────────────────────────────
    # VACÍOS
    # ─────────────────────────────────────────────────────────────────────────

    def _vacios(self, casino, maquinas, usuarios_por_rol):
        banner("PASO 14 — Tickets de Vacíos (30 registros)")
        from VaciosTickets.models import TicketVacio

        tecnicos = usuarios_por_rol.get('TECNICO', [])
        gerentes = usuarios_por_rol.get('GERENCIA', [])
        admins   = usuarios_por_rol.get('ADMINISTRADOR', [])
        auditores = gerentes + admins
        if not tecnicos:
            info("Sin técnicos para crear vacíos")
            return

        MOTIVOS = [c[0] for c in TicketVacio.MOTIVO_FALLA_CHOICES]

        clientes = [
            "Juan Pablo Morales Vega", "Rosa Elena Castillo Díaz", "Pedro Ramírez Torres",
            "Claudia Hernández Ramos", "Miguel Ángel Cruz Soto", "Laura Beatriz Juárez Peña",
            "Arturo Mendoza Fuentes", "Verónica Salinas López", "Ernesto Gutiérrez Medina",
            "Alejandra Vargas Nava", "Félix Domínguez Ríos", "Norma Estela Cortés Ruiz",
            "Gabriel Ortega Campos", "Irma Susana Molina Cruz", "Raúl Antonio Patiño Leal",
            "Carmen Angélica Serrano García", "José Luis Aguilar Navarro", "Silvia Rodríguez Vidal",
            "Manuel de Jesús Tapia Mora", "Leticia Sandoval Espinoza", "Hugo César Ríos Alvarado",
            "Teresa de Jesús Sáenz López", "Edmundo Bravo Guerrero", "Cristina Montes Rivera",
            "Álvaro Espinosa Cárdenas", "Yolanda Peña Solís", "Bernardo Lozano Pacheco",
            "Adriana Cabrera Jiménez", "Francisco Trujillo Delgado", "Martha Elena Vázquez Torres",
        ]

        explicaciones = [
            "El cliente cargó $200 MXN en efectivo al billetero. El sistema registró la transacción "
            "pero la máquina reinició inesperadamente por error de red y el crédito no apareció en pantalla. "
            "Se verificó el log del servidor y confirmamos la transacción sin acreditación.",
            "Durante una falla del enlace SAS, el sistema de gestión perdió la transacción de carga. "
            "El cliente tiene comprobante de su depósito con hora y folio. Se procedió a verificar "
            "el historial de la UPS y confirmar la causa raíz.",
            "Error de doble cobro detectado: el billetero realizó dos lecturas del mismo billete "
            "de $500. El segundo cargo no fue acreditado al cliente. El ticket impreso del billetero "
            "muestra ambas transacciones con diferencia de 12 segundos.",
            "La máquina se desconectó bruscamente del servidor durante la carga. Al reconectarse, "
            "el crédito del cliente (100 fichas de $5) no estaba disponible en la máquina. "
            "El servidor registra la carga como pendiente de confirmación.",
        ]

        # Recolectar PNGs reales del directorio de evidencias
        _ev_dir = Path(settings.MEDIA_ROOT) / "vacios" / "evidencias"
        _png_files = sorted(_ev_dir.glob("*.png")) if _ev_dir.exists() else []

        def _png_content(idx):
            """Devuelve bytes de un PNG real (cíclico) o el PNG mínimo de fallback."""
            if _png_files:
                return _png_files[idx % len(_png_files)].read_bytes()
            return fake_png_bytes()

        for i, cliente in enumerate(clientes):
            monto  = Decimal(str(round(random.uniform(50.0, 750.0), 2)))
            tec    = random.choice(tecnicos)
            motivo = random.choice(MOTIVOS)
            expl   = random.choice(explicaciones)

            tv = TicketVacio(
                casino=casino,
                maquina=random.choice(maquinas),
                cliente_nombre=cliente,
                monto_extraviado=monto,
                tecnico_creador=tec,
                motivo_falla=motivo,
                explicacion_detallada=expl,
            )
            for j, fn in enumerate(['foto_ultimas_operaciones', 'foto_carga_sistema',
                                       'foto_seguimiento_slot', 'foto_recarga_error']):
                png_bytes = _png_content(i * 4 + j)
                getattr(tv, fn).save(f"{fn}_{i+1}.png",
                                     ContentFile(png_bytes, name=f"{fn}_{i+1}.png"),
                                     save=False)
            tv.save()

            # ~60% ya auditados con veredicto
            if auditores and random.random() > 0.4:
                estado_aud = random.choices(
                    ['auditado_aprobado', 'rechazado_investigacion'],
                    weights=[75, 25], k=1
                )[0]
                TicketVacio.objects.filter(pk=tv.pk).update(
                    gerente_auditor=random.choice(auditores),
                    estado_auditoria=estado_aud,
                    fecha_auditoria=rand_dt(),
                )

        auditados = TicketVacio.objects.exclude(estado_auditoria='pendiente_revision').count()
        ok(f"30 tickets de vacíos creados | {auditados} ya auditados")

    # ─────────────────────────────────────────────────────────────────────────
    # MANTENIMIENTOS PREVENTIVOS
    # ─────────────────────────────────────────────────────────────────────────

    def _mantenimientos(self, maquinas, usuarios_por_rol):
        banner("PASO 15 — Mantenimientos Preventivos (1 por máquina muestra)")
        from MantenimientosPreventivos.models import MantenimientoPreventivo

        tecnicos = usuarios_por_rol.get('TECNICO', [])
        if not tecnicos:
            info("Sin técnicos para mantenimientos")
            return

        ESTADOS = ['operativa', 'dañada_operativa', 'dañada', 'observacion']
        obs_textos = [
            "Limpieza general completada. Filtros de ventilación limpios, pasta térmica renovada, "
            "cables internos revisados sin daño aparente.",
            "Se detectó desgaste moderado en los rodillos del billetero. Se lubricaron y se dejó en "
            "observación para revisión en el siguiente turno.",
            "Mantenimiento preventivo completado sin anomalías. Equipo en condiciones óptimas. "
            "Siguiente preventivo programado en 30 días.",
            "Se encontró acumulación de polvo en el ventilador de la PSU. Limpieza profunda realizada. "
            "Se recomienda aumentar la frecuencia de limpieza en esta zona de la sala.",
            "Revisión de conectores de video: se detectó conector HDMI con desgaste leve. "
            "Se ajustó y aseguró. Pendiente solicitud de refacción como preventivo.",
        ]

        sample = random.sample(maquinas, min(80, len(maquinas)))
        for maq in sample:
            tec   = random.choice(tecnicos)
            fecha = rand_date(TODAY - timedelta(days=89), TODAY - timedelta(days=1))
            obs   = random.choice(obs_textos)
            MantenimientoPreventivo.objects.create(
                maquina=maq,
                tecnico_responsable=tec,
                fecha_mantenimiento=fecha,
                estado_final_maquina=random.choices(ESTADOS, weights=[70, 15, 5, 10], k=1)[0],
                observaciones=obs,
            )

        ok(f"{min(80, len(maquinas))} mantenimientos preventivos registrados")

    # ─────────────────────────────────────────────────────────────────────────
    # RELEVOS DE TURNO
    # ─────────────────────────────────────────────────────────────────────────

    def _relevos(self, casino, usuarios_por_rol):
        banner("PASO 16 — Relevos de Turno (30 registros)")
        from RelevosTurnos.models import RelevoTurno

        tecnicos = usuarios_por_rol.get('TECNICO', [])
        if len(tecnicos) < 2:
            info("Se necesitan al menos 2 técnicos para relevos")
            return

        ESTADOS = ['limpia', 'con_pendientes', 'critica']
        pendientes_opciones = [
            "Máquina {uid} quedó en observación por fallo de billetero. Requiere revisión al inicio "
            "del siguiente turno antes de reactivar.",
            "Ticket TKP-2026 abierto en máquina del área VIP. Espera confirmación de proveedor "
            "para piezas de repuesto.",
            "Switch del rack 2 muestra LED ámbar en el puerto 14. Pendiente diagnóstico de red.",
            "3 máquinas de la fila D requieren limpieza de billetero. Programar durante horas pico bajo.",
            None,
        ]
        novedades_opciones = [
            "Turno sin incidencias mayores. Todas las máquinas operativas al momento del relevo.",
            "Se atendieron 2 quejas de clientes por máquinas lentas en zona fumadores. "
            "Ambas cases cerradas satisfactoriamente.",
            "Visita del supervisor regional durante el turno. Se dio recorrido completo por la sala.",
            "Mantenimiento del sistema de CCTV realizado por proveedor externo durante el turno.",
            "Corte de luz de 20 minutos afectó la zona norte. Todas las máquinas reiniciadas y verificadas.",
        ]

        for _ in range(30):
            saliente, entrante = random.sample(tecnicos, 2)
            estado = random.choices(ESTADOS, weights=[55, 35, 10], k=1)[0]
            uid_muestra = random.choice(["A0012", "B0034", "C0021", "D0055"])
            pendiente = random.choice(pendientes_opciones)
            if pendiente and '{uid}' in pendiente:
                pendiente = pendiente.format(uid=uid_muestra)

            RelevoTurno.objects.create(
                casino=casino,
                tecnico_saliente=saliente,
                tecnico_entrante=entrante,
                hora_salida_real=rand_dt(),
                estado_entrega=estado,
                pendientes_detallados=pendiente,
                novedades_generales=random.choice(novedades_opciones),
            )

        ok("30 relevos de turno generados con notas realistas")

    # ─────────────────────────────────────────────────────────────────────────
    # TAREAS ESPECIALES
    # ─────────────────────────────────────────────────────────────────────────

    def _tareas_especiales(self, casino, usuarios_por_rol):
        banner("PASO 17 — Tareas Especiales (15 registros)")
        from TareasEspeciales.models import TareaEspecial

        tecnicos  = usuarios_por_rol.get('TECNICO', [])
        gerentes  = usuarios_por_rol.get('GERENCIA', [])
        admins    = usuarios_por_rol.get('ADMINISTRADOR', [])
        sups      = usuarios_por_rol.get('SUP SISTEMAS', [])
        creadores = gerentes + admins + sups
        if not creadores or not tecnicos:
            info("Sin usuarios necesarios para tareas especiales")
            return

        tareas_data = [
            ("Actualizar firmware de 10 máquinas IGT AVP",
             "El proveedor IGT liberó la versión de firmware 4.3.1 que corrige el error E-032 del "
             "billetero. Actualizar las máquinas listadas via USB autorizado antes del viernes.",
             'alta', 'en_curso'),
            ("Realizar inventario mensual de refacciones",
             "Inventario físico del almacén técnico de refacciones. Contar, registrar en el sistema "
             "y solicitar reposición de los consumibles que estén por debajo del mínimo operativo.",
             'media', 'pendiente'),
            ("Etiquetar rack de servidores nuevo",
             "El rack secundario fue instalado esta semana. Etiquetar todos los cables, parches y "
             "equipos con la nomenclatura estándar del casino. Documentar topología.",
             'baja', 'completada'),
            ("Documentar topología de red completa de la sala",
             "No existe documentación actualizada de la red de máquinas. Mapear todos los switches, "
             "acceso points, IPs y VLANs de la sala y registrar en el sistema.",
             'alta', 'en_curso'),
            ("Verificar fechas de licencias próximas a vencer",
             "Revisar en el sistema las máquinas cuyo campo 'fecha_vencimiento_licencia' venza en "
             "los próximos 60 días y generar reporte para que gerencia gestione renovaciones.",
             'media', 'pendiente'),
            ("Instalación de cámara adicional en área de bóveda",
             "El departamento de seguridad solicitó un punto de cámara adicional en el acceso lateral "
             "de la bóveda. Coordinar con proveedor de CCTV para instalación.",
             'alta', 'pendiente'),
            ("Preparer informe mensual de fallas de máquinas",
             "Generar y presentar a gerencia el informe mensual de fallas: máquinas con más tickets, "
             "tiempos de resolución promedio, y análisis de causas raíz.",
             'media', 'completada'),
            ("Limpieza profunda del site de servidores",
             "Programar con el proveedor de limpieza especializada la limpieza del site. "
             "Incluye aspirado antiestático, limpieza de rejillas y verificación del piso técnico.",
             'media', 'completada'),
            ("Actualizar credenciales de acceso a sistemas de proveedores",
             "Las contraseñas de acceso a los portales de soporte de proveedores no han sido "
             "actualizadas en 12 meses. Actualizar en todos los sistemas y registrar en el gestor.",
             'alta', 'en_curso'),
            ("Reemplazar UPS del site norte",
             "La UPS del rack norte presenta batería degradada al 60% de su capacidad nominal. "
             "Solicitar cotización y coordinar sustitución en horario de baja operatividad.",
             'critica', 'pendiente'),
            ("Configurar nuevo Access Point WiFi en la sala",
             "El AP de la zona sur presenta interferencia y desconexiones frecuentes. "
             "Reemplazar con el equipo que está en almacén y configurar con los parámetros de la red.",
             'media', 'completada'),
            ("Auditoría de accesos físicos a sala técnica",
             "Revisar quién tiene acceso al cuarto técnico y al site de servidores. "
             "Actualizar las listas de acceso, desactivar credenciales de personal que ya no labora.",
             'alta', 'en_curso'),
            ("Revisar cableado estructura completo sala B",
             "Existen quejas de desconexiones intermitentes en la sala B. Realizar inspección visual "
             "completa del cableado, identificar puntos de daño y corregir.",
             'alta', 'completada'),
            ("Capacitación de nuevo técnico en procedimientos NEXUS",
             "El técnico de nuevo ingreso requiere capacitación en el uso del sistema NEXUS: "
             "apertura de tickets, bitácoras, relevos y wiki técnica.",
             'media', 'completada'),
            ("Presentación de KPIs técnicos a gerencia — Q1 2026",
             "Preparar presentación ejecutiva de indicadores del primer trimestre: tiempo promedio "
             "de resolución, disponibilidad de sala, incidencias por categoría.",
             'alta', 'pendiente'),
        ]

        for k, (titulo, desc, prioridad, estado) in enumerate(tareas_data):
            apertura = rand_dt(end=NOW - timedelta(days=1))
            fin      = apertura + timedelta(days=random.randint(1, 10)) if estado == 'completada' else None
            resultado = (
                "Tarea completada satisfactoriamente. Documentada y verificada por supervisor."
                if estado == 'completada' else None
            )
            TareaEspecial.objects.create(
                titulo=titulo,
                descripcion=desc,
                casino=casino,
                creado_por_usuario=random.choice(creadores),
                asignado_a=random.choice(tecnicos) if estado != 'pendiente' else None,
                prioridad=prioridad,
                estatus=estado,
                fecha_apertura=apertura,
                fecha_finalizacion=fin,
                resultado_final=resultado,
            )
            ok(f"  Tarea: {titulo[:55]}")

    # ─────────────────────────────────────────────────────────────────────────
    # INVENTARIO DE SALA
    # ─────────────────────────────────────────────────────────────────────────

    def _inventario(self, casino):
        banner("PASO 18 — Inventario de Sala")
        from InventarioSala.models import InventarioSala

        herramientas = [
            ("Cautín de punta fina HAKKO 936",            4),
            ("Multímetro digital Fluke 117",              3),
            ("Desarmador de estrella #2 — Wiha",          8),
            ("Desarmador plano 4mm — Wiha",               8),
            ("Pinzas de punta fina antiestáticas",        4),
            ("Pelacables automático Jokari T20",          2),
            ("Pistola de calor variable 300–500°C",       2),
            ("Llave ajustable 10\"",                      3),
            ("Cortadora de cable coaxial",                2),
            ("Kit de puntas de precisión 32 piezas",      2),
            ("Osciloscopio portátil DSO112A",             1),
            ("Crimpeadora RJ45/RJ11",                     3),
        ]
        consumibles = [
            ("Pasta soldadora Kester 44",               15),
            ("Conectores RJ45 Cat6 (bolsa 50 piezas)",   8),
            ("Cable UTP Cat6 (rollo 100m)",               3),
            ("Cinta aislante 3M 1600 (rollo)",           20),
            ("Alcohol isopropílico 99% (litro)",         10),
            ("Esponja antiestática de limpieza",         25),
            ("Tornillos M3×6 (cajita 100 piezas)",       12),
            ("Tornillos M4×8 (cajita 100 piezas)",       10),
            ("Fusibles 5A cristal (caja 10 piezas)",     18),
            ("Fusibles 10A cristal (caja 10 piezas)",    15),
            ("Spray limpia contactos QD Electronic",     12),
            ("Grasa dieléctrica Molykote (tubo 150g)",    6),
            ("Cable SATA III 50cm (paquete 5 piezas)",    8),
            ("Bridas plásticas negras 20cm (bolsa 100)", 30),
            ("Papel secante antiestático (rollo)",        5),
            ("Termofit 20cm variado colores (bolsa)",    20),
            ("Resistencias variadas 1/4W (set 600pzs)",   4),
            ("Condensadores electrolíticos variados",     8),
        ]

        for nombre, qty in herramientas:
            InventarioSala.objects.get_or_create(
                casino=casino, nombre=nombre,
                defaults={'tipo': 'herramienta', 'cantidad': qty}
            )
        for nombre, qty in consumibles:
            InventarioSala.objects.get_or_create(
                casino=casino, nombre=nombre,
                defaults={'tipo': 'consumible', 'cantidad': qty}
            )

        ok(f"{len(herramientas)} herramientas + {len(consumibles)} consumibles en inventario")

    # ─────────────────────────────────────────────────────────────────────────
    # GAMIFICACIÓN: RECOMPENSAS Y CANJES
    # ─────────────────────────────────────────────────────────────────────────

    def _recompensas(self, casino, usuarios_por_rol):
        banner("PASO 19 — Gamificación: Recompensas y Canjes")
        from Gamificacion.models import RecompensaGamificacion, CanjeRecompensa

        tecnicos = usuarios_por_rol.get('TECNICO', [])
        sups     = usuarios_por_rol.get('SUP SISTEMAS', [])

        tienda = [
            ("Día libre adicional",
             "Un día libre sin descuento de vacaciones, a elegir en coordinación con el supervisor. "
             "Válido dentro del mes siguiente al canje.",
             500, 5),
            ("Bono de alimentación $200 MXN",
             "Vale canjeable en el comedor del casino o en la cafetería del edificio. "
             "Válido por 30 días a partir de la fecha de entrega.",
             300, 10),
            ("Reconocimiento Técnico del Mes",
             "Publicación en el tablero de honor de la sala, mención en la reunión mensual "
             "y diploma firmado por gerencia. Aplica para el mes en curso.",
             150, 999),
            ("Playera NEXUS Edición Especial 2026",
             "Playera oficial con logo NEXUS bordado en el pecho y nombre del técnico. "
             "Talla a elección. Disponibilidad sujeta a stock.",
             200, 8),
            ("Gift Card Liverpool $500 MXN",
             "Tarjeta de regalo electrónica para tiendas Liverpool. Se envía al correo "
             "registrado en el sistema dentro de 2 días hábiles.",
             800, 4),
            ("Medio día libre",
             "Salida anticipada o entrada retrasada de 4 horas en el turno de su elección. "
             "Requiere autorización del supervisor con 48 horas de anticipación.",
             250, 15),
            ("Certificación técnica pagada",
             "Costo de un curso de certificación técnica cubierto al 100% por el casino. "
             "Aplica para certificaciones listadas en el catálogo aprobado por gerencia.",
             1200, 2),
        ]

        recompensas = []
        for titulo, desc, costo, stock in tienda:
            r, _ = RecompensaGamificacion.objects.get_or_create(
                casino=casino, titulo=titulo,
                defaults={
                    'descripcion': desc,
                    'costo_puntos': costo,
                    'activo': True,
                    'stock': stock,
                }
            )
            recompensas.append(r)

        ok(f"{len(recompensas)} recompensas en tienda")

        # Canjes de técnicos con suficientes puntos
        for u in tecnicos + sups:
            candidatas = [r for r in recompensas if r.costo_puntos <= u.puntos_gamificacion]
            if candidatas and random.random() > 0.4:
                r = random.choice(candidatas)
                CanjeRecompensa.objects.create(
                    usuario=u,
                    recompensa=r,
                    puntos_descontados=r.costo_puntos,
                    estado=random.choices(['pendiente', 'entregado', 'cancelado'],
                                          weights=[20, 70, 10], k=1)[0],
                    nota_gerencia=random.choice([
                        "Entregado personalmente al técnico. Firma de recibo archivada.",
                        "Entrega programada para el viernes en reunión de equipo.",
                        None,
                    ]),
                )

        ok(f"Canjes registrados para técnicos y supervisores elegibles")

    # ─────────────────────────────────────────────────────────────────────────
    # EVOLUCIÓN NEXUS
    # ─────────────────────────────────────────────────────────────────────────

    def _evolucion_nexus(self, usuarios_por_rol):
        banner("PASO 20 — Evolución NEXUS (reportes de mejora)")
        from EvolucionNexus.models import EvolucionNexus

        todos = []
        for lista in usuarios_por_rol.values():
            todos.extend(lista)

        reportes = [
            ("Error al exportar bitácora a PDF en Safari",          "ERROR",
             "PRUEBAS",
             {'modulo_afectado': 'BitacoraTecnica', 'pasos_reproducir':
              "1. Abrir cualquier bitácora. 2. Click en Exportar PDF. 3. El modal se cierra sin generar el archivo. Solo ocurre en Safari 17+."}),
            ("Agregar filtro por proveedor en listado de máquinas",  "FUNCIONALIDAD",
             "DESARROLLO",
             {'beneficio': "Actualmente tarda mucho buscar máquinas de un proveedor específico. Un filtro rápido por proveedor agilizaría el soporte técnico."}),
            ("Botón Nuevo Ticket no visible en móvil — Tickets.vue", "VISUAL",
             "COMPLETADO",
             {'situacion_actual': "En pantallas de 375px el botón queda detrás del buscador.",
              'cambio_propuesto': "Mover el botón a la parte inferior de la pantalla como FAB en móvil."}),
            ("Mejorar velocidad de carga del Mapa de Sala",          "COMPORTAMIENTO",
             "DESARROLLO",
             {'situacion_actual': "Con 300 máquinas el mapa tarda 4–6 segundos en renderizar.",
              'cambio_propuesto': "Usar renderización por canvas en lugar de divs DOM."}),
            ("Módulo de control de acceso a sala técnica",           "CREAR",
             "ANALIZANDO",
             {'beneficio': "Llevar un registro digital de quién entra y sale del site de servidores, integrando con el lector de huella ya instalado."}),
            ("Error en relevo de turno — fecha se guarda en UTC",    "ERROR",
             "COMPLETADO",
             {'modulo_afectado': 'RelevosTurnos', 'pasos_reproducir':
              "1. Crear relevo. 2. La hora mostrada en la lista difiere +6h del horario real del casino."}),
            ("Dashboard: agregar gráfica de disponibilidad de sala", "FUNCIONALIDAD",
             "ADQUISICION",
             {'beneficio': "Gerencia necesita ver en tiempo real qué % de las máquinas están operativas vs en mantenimiento."}),
            ("Calendar de mantenimientos preventivos",               "CREAR",
             "POR_REVISAR",
             {'beneficio': "Un calendario visual (FullCalendar o PrimeVue Scheduler) para programar y confirmar los mantenimientos preventivos del mes."}),
        ]

        for (titulo, cat, estado, datos) in reportes:
            EvolucionNexus.objects.create(
                usuario=random.choice(todos),
                categoria=cat,
                estado=estado,
                titulo=titulo,
                descripcion=(
                    datos.get('beneficio') or
                    datos.get('pasos_reproducir') or
                    datos.get('situacion_actual') or
                    titulo
                ),
                datos_extra=datos,
            )
            ok(f"  Evolución: [{cat}] {titulo[:50]}")

    # ─────────────────────────────────────────────────────────────────────────
    # RESUMEN FINAL
    # ─────────────────────────────────────────────────────────────────────────

    def _resumen(self, usuarios_por_rol):
        from Tickets.models import Ticket
        from BitacoraTecnica.models import BitacoraTecnica
        from IncidenciasInfraestructura.models import IncidenciaInfraestructura
        from AuditoriasExternas.models import AuditoriaServicioExterno
        from Notificaciones.models import Notificacion
        from Wiki.models import WikiTecnica
        from VaciosTickets.models import TicketVacio
        from Maquinas.models import Maquina
        from Proveedores.models import Proveedor
        from ModelosMaquinas.models import ModeloMaquina
        from MantenimientosPreventivos.models import MantenimientoPreventivo
        from RelevosTurnos.models import RelevoTurno
        from TareasEspeciales.models import TareaEspecial
        from Gamificacion.models import RecompensaGamificacion
        from InventarioSala.models import InventarioSala

        banner("RESUMEN FINAL — SEEDING COMPLETADO")

        filas = [
            ("Proveedores",              Proveedor.objects.count()),
            ("Modelos de Máquinas",      ModeloMaquina.objects.count()),
            ("Máquinas",                 Maquina.objects.count()),
            ("Tickets",                  Ticket.objects.count()),
            ("Entradas de Bitácora",     BitacoraTecnica.objects.count()),
            ("Incidencias Infra.",        IncidenciaInfraestructura.objects.count()),
            ("Auditorías Externas",      AuditoriaServicioExterno.objects.count()),
            ("Notificaciones",           Notificacion.objects.count()),
            ("Guías Wiki",               WikiTecnica.objects.count()),
            ("Tickets de Vacíos",        TicketVacio.objects.count()),
            ("Mantenimientos Prev.",     MantenimientoPreventivo.objects.count()),
            ("Relevos de Turno",         RelevoTurno.objects.count()),
            ("Tareas Especiales",        TareaEspecial.objects.count()),
            ("Recompensas (tienda)",     RecompensaGamificacion.objects.count()),
            ("Artículos Inventario",     InventarioSala.objects.count()),
        ]

        print(f"\n  {C.BOLD}{'Entidad':<32} {'Registros':>10}{C.RESET}")
        print(f"  {'─'*44}")
        for label, count in filas:
            print(f"  {label:<32} {C.GREEN}{count:>10}{C.RESET}")

        banner("USUARIOS GENERADOS — contraseña: 123")
        print(f"\n  {C.BOLD}{'Username':<16} {'Nombre Completo':<28} {'Rol':<22} {'XP':>6}{C.RESET}")
        print(f"  {'─'*78}")

        orden = ['TECNICO', 'SUP SISTEMAS', 'ADMINISTRADOR', 'GERENCIA', 'PROVEEDOR', 'OBSERVADOR']
        for rol_key in orden:
            for u in usuarios_por_rol.get(rol_key, []):
                nombre = f"{u.nombres} {u.apellido_paterno}"
                print(
                    f"  {C.GREEN}{u.username:<16}{C.RESET}"
                    f" {nombre:<28}"
                    f" {C.YELLOW}{rol_key:<22}{C.RESET}"
                    f" {C.CYAN}{u.puntos_gamificacion:>6}{C.RESET}"
                )

        print(f"\n  {C.BOLD}{C.GREEN}✅  NEXUS seeding perfecto completado exitosamente.{C.RESET}\n")
