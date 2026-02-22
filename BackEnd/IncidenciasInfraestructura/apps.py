from django.apps import AppConfig


class IncidenciasinfraestructuraConfig(AppConfig):
    name = 'IncidenciasInfraestructura'

    def ready(self):
        import IncidenciasInfraestructura.signals  # noqa: F401
