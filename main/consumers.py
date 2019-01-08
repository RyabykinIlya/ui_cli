import json
from datetime import datetime

from asgiref.sync import sync_to_async, async_to_sync
from paramiko.ssh_exception import SSHException
import django_rq

from . import models
from .classes_override import WebsocketConsumerCustom, AsyncWebsocketConsumerCustom
from .help import get_user
from .ssh_modules import SshCommandExecuter
from .models import Server, CSCU
from .tasks import HistoryLogger, create


def get_command_for_server(socket, server_pk, command_pk):
    #
    # Function for command validation, saves from executing command that does not exist for the chosen server
    # or not available for current user
    #
    # should pass permission__user here for safer execution with permissions
    # user can not execute command with no permissions for it
    server_command = models.ServerCommand.cobjects. \
        get(permission__user=get_user(socket), server=models.Server.objects.get(pk=server_pk), pk=command_pk)
    if not server_command:
        raise KeyError('Command with pk {} does not exist for this server.'.format(command_pk))

    return server_command


class SyncCommandsConsumer(WebsocketConsumerCustom):
    def connect(self):
        # create connection to server once
        self.accept()
        self.server_pk = self.get_websocket_kwargs(self, 'pk')
        self.server = Server.objects.get(pk=self.server_pk)
        try:
            self.executer = SshCommandExecuter(self.server.ip_address, self.server.user,
                                               self.server.password, self.server.ssh_port)
        except SSHException:
            self.send(text_data=json.dumps({
                'message': str('Can not connect to this server.')
            }))
            self.disconnect()

    def disconnect(self, close_code='0'):
        if hasattr(self, 'executer'):
            self.executer.disconnect()
        self.send(text_data=json.dumps({
            'message': str('Connection lost, reload this page to continue.')
        }))
        print('Web-socket connection closed with code {}'.format(close_code))
        self.close()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if 'command' in text_data_json:
            self.executer.execute(text_data_json['command'])
        else:
            command_obj = get_command_for_server(self, self.server_pk, text_data_json['command_pk'])
            self.executer.execute(command_obj.command)
        self.cscu_hist = HistoryLogger(self.server, command_obj, get_user(self), datetime.now())
        django_rq.enqueue(self.cscu_hist.save)
        # django_rq.enqueue(create, self.server, command_obj, get_user(self))
        # django_rq.
        for message in self.executer.gen:
            self.send(text_data=json.dumps({
                # 'std': self.executer.std,
                'message': str(message)
            }))
        else:
            # pass
            django_rq.enqueue(self.cscu_hist.unlock_command, datetime.now())


class AsyncCommandsConsumer(AsyncWebsocketConsumerCustom):
    async def connect(self):
        # create connection to server once
        self.server_pk = self.get_websocket_kwargs(self, 'pk')
        self.server = Server.objects.get(pk=self.server_pk)
        self.executer = sync_to_async(SshCommandExecuter(self.server.ip_address, self.server.user,
                                                         self.server.password, self.server.ssh_port, 'async'))
        await self.accept()

    async def disconnect(self, close_code='0'):
        sync_to_async(self.executer.func.disconnect())
        print('Web-socket connection closed with code {}'.format(close_code))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if 'command' in text_data_json:
            self.executer.func.execute(text_data_json['command'])
        else:
            command_obj = get_command_for_server(self, self.server_pk, text_data_json['command_pk'])
            self.executer.func.execute(command_obj.command)
        async for message in self.executer.func.gen:
            await self.send(text_data=json.dumps({
                # 'std': self.executer.func.std,
                'message': str(message)
            }))
