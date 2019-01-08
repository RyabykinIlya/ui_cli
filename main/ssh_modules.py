import socket
import paramiko

# !!! Do not import any from .models here,
# because apps.py uses check_socket_openned method during initial start

def get_any_available(host, ports, timeout=0.5):
    '''
    :param host: hostname or ip of machine to check connection
    :param ports: list or tuple of port that can be available
    :param timeout:
    :return: port (int) connection with is available
    '''
    for port in ports:
        if check_socket_openned(host, port):
            return int(port)

def check_socket_openned(host, port, timeout=0.5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    if result == 0:
        return True
    else:
        return False


class SshCommandExecuter():
    def __init__(self, host, user, password, port, mode='sync'):
        # creates connection to server once
        self._mode = mode
        self.RECV_BYTES = 4024
        self.client = paramiko.Transport((host, port))
        self.client.connect(username=user, password=password)
        # self.std = self.struct_std()

    def gen_sync(self):
        while not self.session.exit_status_ready():
            yield self.session.recv(self.RECV_BYTES).decode("utf-8").strip() \
                  or self.session.recv_stderr(self.RECV_BYTES).decode("utf-8").strip()

    async def gen_async(self):
        while not self.session.exit_status_ready():
            yield self.session.recv(self.RECV_BYTES).decode("utf-8").strip() \
                  or self.session.recv_stderr(self.RECV_BYTES).decode("utf-8").strip()

    def execute(self, command):
        self.session = self.client.open_channel(kind='session')
        self.session.exec_command(command)
        if self._mode == 'sync':
            self.gen = self.gen_sync()
        else:
            self.gen = self.gen_async()

    def disconnect(self):
        self.client.close()

    def struct_std(self):
        # struct std to display in UI (ex [root@olinux ~]#)
        session = self.client.open_session()
        session.exec_command('hostname')
        hostname = session.recv(self.RECV_BYTES).decode("utf-8").strip()
        return '[{}@{} ~]#'.format(self.client.auth_handler.username, hostname)


def ssh_execute_command(host, user, password, port, command):
    if not check_socket_openned(host, port):
        raise TimeoutError('Can not connect to server.')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read().decode("utf-8") + stderr.read().decode("utf-8")
    client.close()
    return data


def ssh_execute_command_for_server(server_pk, command):
    from .models import Server
    server = Server.objects.get(pk=server_pk)
    return ssh_execute_command(server.ip_address, server.user, server.password, server.ssh_port, command)
