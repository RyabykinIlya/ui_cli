from main.tasks import exec_cmd_task, finish_cmd_task, error_handler
from .helpers import create_cscu_start

from .ssh_modules import ssh_execute_command_for_server

def exec_cmd(user_pk, servers_pk, command_pk):
    # TODO on error if can not connect to the server etc.
    for server_pk in servers_pk.split(', '):
        cscu_pk = create_cscu_start(user_pk, server_pk, command_pk)
        exec_cmd_task.apply_async((user_pk, server_pk, command_pk, cscu_pk)
                                  #,link_error=error_handler.s()
                                  , link=finish_cmd_task.s()
                                  )