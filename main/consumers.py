import json

from . import models
from .classes_override import WebsocketConsumerCustom
from .ssh_modules import ssh_execute_command_for_server
from .help import get_user
from .ssh_modules import SshCommandExecuter


class CommandsConsumer(WebsocketConsumerCustom):
    def get_command_for_server(self, server_pk, command_pk):
        '''
        Function for command validation, saves from executing command that does not exist for the chosen server
        or not available for current user
        '''
        # should pass permission__user here for safer execution with permissions
        # user can not execute command with no permissions for it
        server_command = models.ServerCommand.cobjects. \
            get(permission__user=get_user(self), server=models.Server.objects.get(pk=server_pk), pk=command_pk)
        if not server_command:
            raise KeyError('Command with pk {} does not exist for this server.'.format(command_pk))

        return server_command

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        try:
            server_pk = self.get_websocket_kwargs(self, 'pk')
            command_obj = self.get_command_for_server(server_pk, text_data_json['command_pk'])
            '''for message in SshCommandExecuter('127.0.0.1','root','root',50022,'tail -f anaconda-ks.cfg').execute():
                self.send(text_data=json.dumps({
                    'message': str(message)
                }))
            '''
            message = ssh_execute_command_for_server(server_pk, command_obj.command)
        except (KeyError, TimeoutError) as e:
            message = 'Error has occured during command execution:\n{}'.format(str(e))

        self.send(text_data=json.dumps({
            'message': str(message)
        }))
