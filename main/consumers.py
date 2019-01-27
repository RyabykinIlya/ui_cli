import json
from datetime import datetime

from asgiref.sync import sync_to_async, async_to_sync
from paramiko.ssh_exception import SSHException
from itertools import groupby
import django_rq

from . import models
from .classes_override import WebsocketConsumerCustom, AsyncWebsocketConsumerCustom
from .helpers import get_user, get_command_for_server, HistoryLogger
from .ssh_modules import SshCommandExecuter
from .models import Server, CSCU, Contour
from .pretasks import exec_cmd


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
            command_obj = get_command_for_server(get_user(self).pk, self.server_pk, text_data_json['command_pk'])
            self.executer.execute(command_obj.command)
        # TODO for manual command ?
        self.cscu_hist = HistoryLogger(self.server, command_obj, get_user(self), datetime.now())
        for message in self.executer.gen:
            self.send(text_data=json.dumps({
                # 'std': self.executer.std,
                'message': str(message)
            }))
        else:
            self.cscu_hist.unlock_command(datetime.now())


class SyncCommandServerConsumer(WebsocketConsumerCustom):
    def connect(self):
        # create connection to server once

        async_to_sync(self.channel_layer.group_add)('commands', self.channel_name)
        self.accept()

    def disconnect(self, close_code='0'):
        self.close()

    def manage_locks(self, message):
        self.send_msg('lock', message['text'])

    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if text_data_json.get('execute'):
            self.execute_command(text_data_json['parameters'])
        else:
            self.send_servers_for_command(text_data_json['command_pk'])

    def send_msg(self, type, msg):
        '''
        type - info or error
        msg - any string
        '''
        self.send(text_data=json.dumps({
            str(type): str(msg)
        }))

    def execute_command(self, params):
        if params.get('command') and params.get('server'):
            # TODO решить что делать с этим, как вызывать? обрабатывать в exec_cmd?
            exec_cmd(get_user(self).pk, params['server']['pk'], params['command']['pk'])
            self.send_msg(
                'info', 'Команда {} добавлена в очередь для серверов: {}<br> Информация на странице <a>.'.format(
                    params['command']['value'], params['server']['value']))
        else:
            self.send_msg('error', 'Для выполнения команды нужно выбрать команду и один или несколько серверов.')

        print(params)

    def send_servers_for_command(self, command_pk):
        # get available servers for this command related to permissions
        available_servers = Server.cobjects.filter(
            commands__pk=command_pk).get_restricted(user=get_user(self))

        # struct dictionary with data
        servers_dict = [{'contour_name': srvr.contour.name,
                         'contour_order': srvr.contour.order_by,
                         'server_name': srvr.name,
                         'server_pk': srvr.pk}
                        for srvr in available_servers]

        # create list of grouped and sorted Contour:Servers dicts
        grouped_sorted_servers = [{el[0]: list(el[1])} for el in
                                  groupby(sorted(sorted(servers_dict,
                                                        key=lambda x: x['contour_name']),
                                                 key=lambda x: x['contour_order'])
                                          , lambda x: x['contour_name'])]

        self.send(text_data=json.dumps({
            'servers': json.dumps(grouped_sorted_servers)
        }))


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
            command_obj = get_command_for_server(get_user(self).pk, self.server_pk, text_data_json['command_pk'])
            self.executer.func.execute(command_obj.command)
        self.cscu_hist = HistoryLogger(self.server, command_obj, get_user(self), datetime.now())
        django_rq.enqueue(self.cscu_hist.save)
        async for message in self.executer.func.gen:
            await self.send(text_data=json.dumps({
                # 'std': self.executer.func.std,
                'message': str(message)
            }))
        else:
            django_rq.enqueue(self.cscu_hist.unlock_command, datetime.now())
