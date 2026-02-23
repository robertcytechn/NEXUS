from django.apps import AppConfig


class GamificacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Gamificacion'
    verbose_name = 'Gamificación y Recompensas'

    def ready(self):
        import Gamificacion.signals_gamificacion  # noqa: F401
