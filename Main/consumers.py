import json

from .models import ServerCommand, Server
from .classes_override import WebsocketConsumerCustom
from .ssh_modules import ssh_execute_command_for_server


class CommandsConsumer(WebsocketConsumerCustom):
    def get_command_for_server(self, server_pk, command_pk):
        'Function for command validation, saves from executing command that does not exist for the chosen server'

        server_command = ServerCommand.objects.get(server=Server.objects.get(pk=server_pk), pk=command_pk)
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
        except KeyError as e:
            message = 'Error has occured during command execution:\n{}'.format(str(e))

        message = ssh_execute_command_for_server(server_pk, command_obj.command)

        self.send(text_data=json.dumps({
            'message': str(message)
        }))
