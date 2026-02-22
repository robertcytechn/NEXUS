from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    name = 'Usuarios'

    def ready(self):
        import Usuarios.signals  # noqa: F401
