import socket
import paramiko
import asyncio

from .models import Server


def check_socket_openned(host, port, timeout=0.5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    if result == 0: return 0

'''
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
'''
'''
client2 = paramiko.Transport(('127.0.0.1',50022)) \
    asgdf
    asdgf
'''
class SshCommandExecuter():
    def __init__(self, host, user, password, port):
        # creates connection to server once
        self.client = paramiko.Transport((host, port))
        self.client.connect(username=user, password=password)

    def execute(self, command):
        # creates channel every time for command execution
        #async def gen(self):
        async def gen(self):
            # used for stoping generator outside?
            while not self.session.exit_status_ready():
                yield self.session.recv(self.RECV_BYTES).decode("utf-8") \
                      or self.session.recv_stderr(self.RECV_BYTES).decode("utf-8")
        self.session = self.client.open_channel(kind='session')
        self.RECV_BYTES = 1024
        self.session.exec_command(command)
        self.gen = gen(self)

    def disconnect(self):
        # self.session.close()
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

