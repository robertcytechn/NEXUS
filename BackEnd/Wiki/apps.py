from django.apps import AppConfig


class WikiConfig(AppConfig):
    name = 'Wiki'

    def ready(self):
        import Wiki.signals  # noqa: F401
