from datetime import datetime
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'ui_cli.settings'
django.setup()

from main.models import CSCU


class HistoryLogger():
    def __init__(self, server, command, user, start_time):
        self.cscu = CSCU.objects.create(contour=server.contour, server=server,
                                        servercommand=command, user=user,
                                        locked_status=True, start_time=start_time)

    def save(self, force_update=False):
        self.cscu.save(force_update=force_update)

    def unlock_command(self, end_time):
        self.cscu.locked_status = False
        self.cscu.end_time = end_time
        self.save(force_update=True)


def create(server, command, user):
    cscu = CSCU.objects.create(contour=server.contour, server=server,
                               servercommand=command, user=user,
                               locked_status=True, start_time=datetime.now())
    cscu.save()
