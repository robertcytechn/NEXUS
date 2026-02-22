from django.apps import AppConfig


class TicketsConfig(AppConfig):
    name = 'Tickets'

    def ready(self):
        import Tickets.signals  # noqa: F401
