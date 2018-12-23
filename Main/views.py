from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .models import Server, ServerCommand
from .ssh_modules import ssh_execute_command, check_socket_openned


def main_view(request):
    return render(request, 'Main/main.html')


class ServerDetail(DetailView):
    model = Server

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['commands'] = ServerCommand.objects.filter(server=self.object)
        return context


class ServersListView(ListView):
    model = Server
    paginate_by = 100

    def create_object(self, context):
        for server in context['server_list']:
            if check_socket_openned(server.ip_address, server.ssh_port) == 0:
                server.status = 'online'
            else:
                server.status = 'offline'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.create_object(context)
        return context
