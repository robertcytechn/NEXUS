from django.apps import AppConfig

class AuditoriaglobalConfig(AppConfig):
    name = 'AuditoriaGlobal'

    def ready(self):
        import AuditoriaGlobal.signals
