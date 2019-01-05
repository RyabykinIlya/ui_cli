import json

from . import models
from .classes_override import WebsocketConsumerCustom, AsyncWebsocketConsumerCustom
from .ssh_modules import ssh_execute_command_for_server
from .help import get_user
from .ssh_modules import SshCommandExecuter
from .models import Server
from asgiref.sync import sync_to_async, async_to_sync
import asyncio

'''
class CommandsConsumer(WebsocketConsumerCustom):

    def get_command_for_server(self, server_pk, command_pk):
        #
        #Function for command validation, saves from executing command that does not exist for the chosen server
        #or not available for current user
        #
        # should pass permission__user here for safer execution with permissions
        # user can not execute command with no permissions for it
        server_command = models.ServerCommand.cobjects. \
            get(permission__user=get_user(self), server=models.Server.objects.get(pk=server_pk), pk=command_pk)
        if not server_command:
            raise KeyError('Command with pk {} does not exist for this server.'.format(command_pk))

        return server_command

    def connect(self):
        # create connection to server once
        self.server_pk = self.get_websocket_kwargs(self, 'pk')
        self.server = Server.objects.get(pk=self.server_pk)
        self.executer = SshCommandExecuter(self.server.ip_address, self.server.user,
                                           self.server.password, self.server.ssh_port)
        print('connected {}'.format(self.executer.client._ident))
        self.accept()

    def disconnect(self, close_code='0'):
        self.executer.disconnect()
        print('Web-socket connection closed with code {}'.format(close_code))
        # pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        #print(text_data_json['command_pk'])
        ##if hasattr(self, 'executer'):
        ##    self.executer.client.close()
        #print(self.executer.client._ident)
        print('executing with {}'.format(text_data))
        if text_data_json.get('disconnect') != None:
            self.disconnect()
            return
        command_obj = self.get_command_for_server(self.server_pk, text_data_json['command_pk'])
        self.executer.execute(command_obj.command)
        for message in self.executer.gen:
            self.send(text_data=json.dumps({
                'message': str(message)
            }))
            # self.disconnect()
'''

class CommandsConsumer(AsyncWebsocketConsumerCustom):
    def get_command_for_server(self, server_pk, command_pk):
        '''
        Function for command validation, saves from executing command that does not exist for the chosen server
        or not available for current user
        '''
        # should pass permission__user here for safer execution with permissions
        # user can not execute command with no permissions for it
        server_command = sync_to_async(models.ServerCommand.cobjects. \
            get(permission__user=get_user(self), server=models.Server.objects.get(pk=server_pk), pk=command_pk))
        if not server_command:
            raise KeyError('Command with pk {} does not exist for this server.'.format(command_pk))

        return server_command

    async def connect(self):
        # create connection to server once
        self.server_pk = self.get_websocket_kwargs(self, 'pk')
        self.server = Server.objects.get(pk=self.server_pk)
        self.executer = sync_to_async(SshCommandExecuter(self.server.ip_address, self.server.user,
                                           self.server.password, self.server.ssh_port))
        await self.accept()

    async def disconnect(self, close_code='0'):
        #sync_to_async(self.executer.disconnect())
        print('Web-socket connection closed with code {}'.format(close_code))
        # pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if 'command' in text_data_json:
            self.executer.func.execute(text_data_json['command'])
        else:
            command_obj = self.get_command_for_server(self.server_pk, text_data_json['command_pk'])
            self.executer.func.execute(command_obj.func.command)
        async for message in self.executer.func.gen:
            await self.send(text_data=json.dumps({
                'message': str(message)
            }))