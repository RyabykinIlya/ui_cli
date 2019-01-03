import socket
import paramiko

from .models import Server


def check_socket_openned(host, port, timeout=0.5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    if result == 0: return 0


class SshCommandExecuter():
    def __init__(self, host, user, password, port, command):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=host, username=user, password=password, port=port)
        self.stdin, self.stdout, self.stderr = self.client.exec_command(command)

    # def connect(self, host, user, password, port):


    def execute(self):
        line_buf = ""
        while not self.stdout.channel.exit_status_ready():
            line_buf += self.stdout.read(1).decode("utf-8")
            if line_buf.endswith('\n'):
                yield line_buf
                line_buf = ''
        else:
            self.disconnect()

    def disconnect(self):
        self.client.close()


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

