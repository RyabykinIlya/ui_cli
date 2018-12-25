import json

from .models import ServerCommand, Server
from .classes_override import WebsocketConsumerCustom


class CommandsConsumer(WebsocketConsumerCustom):
    def get_command_for_server(self, server_pk, command_pk):
        'Function for command validation, saves from executing command that does not exist for the chosen server'

        server_command = ServerCommand.objects.filter(server=Server.objects.get(pk=server_pk), pk=command_pk)
        if not server_command:
            raise KeyError('Command with pk {} does not exist for this server.'.format(command_pk))

        return server_command

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        command = self.get_command_for_server(self.get_websocket_kwargs(self, 'pk'), text_data_json['message'])

        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))
