import json

from . import models
from .classes_override import WebsocketConsumerCustom
from .ssh_modules import ssh_execute_command_for_server


class CommandsConsumer(WebsocketConsumerCustom):
    def get_command_for_server(self, server_pk, command_pk):
        'Function for command validation, saves from executing command that does not exist for the chosen server'

        server_command = models.ServerCommand.objects.\
            get(server=models.Server.objects.get(pk=server_pk), pk=command_pk)
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
            message = ssh_execute_command_for_server(server_pk, command_obj.command)
        except (KeyError, TimeoutError) as e:
            message = 'Error has occured during command execution:\n{}'.format(str(e))

        self.send(text_data=json.dumps({
            'message': str(message)
        }))
