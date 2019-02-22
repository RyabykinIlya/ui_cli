import json
from datetime import datetime

from asgiref.sync import sync_to_async, async_to_sync
from paramiko.ssh_exception import SSHException
# from channels.generic.websocket import WebsocketConsumer
from itertools import groupby
import django_rq

from . import models
from .classes_override import WebsocketConsumerCustom  # , AsyncWebsocketConsumerCustom
from .helpers import get_user, get_command_for_server, unpack_list, HistoryLogger
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
            self.send_msg('message', 'Can not connect to this server.')
            self.disconnect()

    def disconnect(self, close_code='0'):
        if hasattr(self, 'executer'):
            self.executer.disconnect()
        self.send_msg('message', 'Connection lost, reload this page to continue.')
        print('Web-socket connection closed with code {}'.format(close_code))
        self.close()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if 'command' in text_data_json:
            self.executer.execute(text_data_json['command'])
        else:
            command_text = get_command_for_server(get_user(self).pk, self.server_pk, text_data_json['command_pk'])
            self.executer.execute(command_text)
        # TODO for manual command ?
        # self.cscu_hist = HistoryLogger(self.server, command_obj, get_user(self), datetime.now())

        # TODO Если выполнять команды по очереди быстро, то генератор не успевает завершить выполнение
        # из-за этого команды которые хочу выполнить выполняются со второго раза

        for message in self.executer.gen:
            self.send_msg('message', str(message))
        else:
            self.cscu_hist.unlock_command(datetime.now())

    def get_websocket_kwargs(self, socket, key):
        # Custom method for getting kwargs key using one function.

        value = socket.scope['url_route']['kwargs'].get(key, -1)
        if value == -1:
            raise KeyError('Key {} does not exist in '
                           'socket->scope(dict)->url_route(dict)->kwargs(dict) you passed from JS '
                           'web-socket initialization'.format(key))
        else:
            return value


class SyncCommandServerConsumer(WebsocketConsumerCustom):
    def connect(self):
        # create connection to server once
        async_to_sync(self.channel_layer.group_add)('commands', self.channel_name)
        self.accept()

    def disconnect(self, close_code='0'):
        self.close()

    def manage_locks(self, message):
        self.send_msg('lock', json.dumps(message['object']))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if text_data_json.get('execute'):
            self.execute_command(text_data_json['parameters'])
        else:
            self.send_servers_for_command(text_data_json['command_pk'])

    def execute_command(self, params):

        params = unpack_list(params)

        if params.get('command') and params.get('server'):
            user_pk = get_user(self).pk

            if True:
                # TODO решить что делать с этим, как вызывать? обрабатывать в exec_cmd?
                exec_cmd(
                    user_pk,
                    params['server']['pk'],
                    params['command']['pk'],
                    params.get('additionalInfo')
                )

                print(params)

                self.send_msg(
                    'info', 'Команда {} добавлена в очередь для серверов: {}'
                            '<br> Информация на странице <a href="/commands/history">История выполнений</a>.'.format(
                        params['command']['value'],
                        ', '.join(params['server']['value']) if isinstance(params['server']['value'], list)
                                                              else params['server']['value']
                    )
                )
        else:
            self.send_msg('error', 'Для выполнения команды нужно выбрать команду и один или несколько серверов.')

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

        self.send_msg('servers', json.dumps(grouped_sorted_servers))


class SyncCSCUConsumer(WebsocketConsumerCustom):
    def connect(self):
        # create connection to server once
        async_to_sync(self.channel_layer.group_add)('cscus', self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        self.close()

    def manage_cscu(self, message):
        self.send_msg('message', message)


''' not used
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
'''
