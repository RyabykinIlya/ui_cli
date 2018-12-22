from django.shortcuts import render

import socket
import paramiko

from .models import Server


def check_socket_opened(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    if result == 0: return 0


def ssh_connect(host, user, password, port):
    if check_socket_opened(host, port) != 0: return 1
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ls -l')
    data = stdout.read() + stderr.read()
    print(data)
    client.close()


def main_view(request):
    return render(request, 'main.html')


def servers_list_view(request):
    def check_connection():
        servers_info = []
        for server in servers:
            servers_info.append([server.name, server.ip_address])
            if check_socket_opened(server.ip_address, server.ssh_port) == 0:
                servers_info[-1].append('online')
            else:
                servers_info[-1].append('offline')
        return servers_info

    servers = Server.objects.all()
    servers_info = check_connection()
    return render(request, 'servers_list.html', context={'servers': servers_info})
