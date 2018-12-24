import socket
import paramiko


def check_socket_openned(host, port, timeout=0.5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    if result == 0: return 0


def ssh_execute_command(host, user, password, port, command):
    if check_socket_openned(host, port) != 0: return 'Connection refused'
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    return data
