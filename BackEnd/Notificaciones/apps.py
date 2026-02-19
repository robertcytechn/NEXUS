from django.apps import AppConfig


class NotificacionesConfig(AppConfig):
    name = 'Notificaciones'
    
    def ready(self):
        """
        Importa y registra los signals cuando la aplicación está lista.
        Esto asegura que todos los triggers estén activos.
        """
        import Notificaciones.signals
