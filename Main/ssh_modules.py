import socket
import paramiko

from .models import Server


def check_socket_openned(host, port, timeout=0.5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    if result == 0: return 0


def ssh_execute_command(host, user, password, port, command):
    if check_socket_openned(host, port) != 0:
        raise TimeoutError('Can not connect to server.')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read().decode("utf-8") + stderr.read().decode("utf-8")
    client.close()
    return data


def ssh_execute_command_for_server(server_pk, command):
    server = Server.objects.get(pk=server_pk)
    return ssh_execute_command(server.ip_address, server.user, server.password, server.ssh_port, command)
