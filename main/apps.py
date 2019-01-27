import socket


from django.apps import AppConfig
from .ssh_modules import check_socket_openned
from ui_cli.settings import RQ_QUEUES

class MainConfig(AppConfig):
    name = 'main'
    verbose_name = 'Основное'
    verbose_name_plural = 'Основное'

    def ready(self):
        import main.signals
        # check queues hosts connection
        for queue in RQ_QUEUES.values():
            if not check_socket_openned(queue['HOST'], int(queue['PORT']), 3):
                raise TimeoutError('Can not connect to {} port {}. '
                                   'Check settings.py RQ_QUEUES section'.format(queue['HOST'], queue['PORT']))