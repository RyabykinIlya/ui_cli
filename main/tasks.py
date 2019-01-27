from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.result import AsyncResult
from ui_cli.celery import app

from .ssh_modules import ssh_execute_command_for_server
from .helpers import create_cscu_finish

@shared_task(bind=True)
def exec_cmd_task(self, user_pk, server_pk, command_pk, cscu_pk):
    #return 'server: {}, command: {}, output: {}'.\
    #        format(server_pk, command_pk, ssh_execute_command_for_server(server_pk, command_pk, user_pk))
    try:
        cmd_output, cmd_err = ssh_execute_command_for_server(server_pk, command_pk, user_pk)
    except TimeoutError as e:
        return {'cscu_pk': cscu_pk,
                'error': e}

    return {'cscu_pk': cscu_pk,
            'cmd_output': cmd_output,
            'cmd_err': cmd_err}

@app.task
def error_handler(uuid):
    result = AsyncResult(uuid)
    exc = result.get(propagate=False)
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(
          uuid, exc, result.traceback))

@shared_task
def finish_cmd_task(kargs):
    # TOTO make finish time to get from prev command logs
    '''
    * - required
    kargs content:
     * kargs['cscu_pk'] - cscu_pk
     * kargs['cmd_output'] or args['cmd_err'] - command output result
       error - error before command execution
    '''

    if 'cmd_err' in kargs or 'cmd_output' in kargs:
        if kargs['cmd_err']:
            output = kargs['cmd_err']
            is_success = False
        elif kargs['cmd_output']:
            output = kargs['cmd_output']
            is_success = True
        else:
            # if command has no output
            output = ''
            is_success = True
    elif 'error' in kargs:
        output = kargs['error']
        is_success = False
    else:
        # should not occur
        output = 'Unknown result, contact with coder. File tasks.py in main'
        is_success = False

    create_cscu_finish(kargs['cscu_pk'], output, is_success)
    return 'CSCU with pk {0} marked as finished with status {2} and output: {1}'\
        .format(kargs['cscu_pk'], output, is_success)

