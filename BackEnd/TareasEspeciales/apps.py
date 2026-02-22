from django.apps import AppConfig


class TareasespecialesConfig(AppConfig):
    name = 'TareasEspeciales'

    def ready(self):
        import TareasEspeciales.signals  # noqa: F401
