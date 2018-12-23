from django.shortcuts import render
from django.views.generic import DetailView

from .models import Server
from .ssh_modules import ssh_execute_command, check_socket_openned


def main_view(request):
    return render(request, 'Main/main.html')


class ServerDetail(DetailView):
    model = Server


def servers_list_view(request):
    def check_connection():
        servers_info = []
        for server in servers:
            servers_info.append([server.name, server.ip_address])
            if check_socket_openned(server.ip_address, server.ssh_port) == 0:
                servers_info[-1].append('online')
            else:
                servers_info[-1].append('offline')
        return servers_info

    servers = Server.objects.all()
    servers_info = check_connection()
    return render(request, 'Main/servers_list.html', context={'servers': servers_info})
