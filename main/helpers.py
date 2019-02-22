from datetime import datetime
import re

from django_celery_results.models import TaskResult

from main.models import CSCU, ServerCommand, Server, Contour, User


def get_user(object):
    # function returns model-referenced user-object

    def get_from_request(obj):
        # function returns user-object from request attr
        return getattr(getattr(obj, 'request'), 'user')

    if 'request' in dir(object):
        return get_from_request(object)
    elif 'view' in dir(object):
        return get_from_request(getattr(object['view']))
    elif hasattr(object, 'scope'):
        if 'user' in getattr(object, 'scope'):
            return getattr(object, 'scope').get('user')
    else:
        raise TypeError('Can not return user from object {}'.format(type(object)))


def is_superuser(user_pk):
    return User.objects.get(pk=user_pk).is_superuser


def get_contour(user_pk, server_pk):
    if is_superuser(user_pk) != True:
        contour = Contour.objects.get(server__id=server_pk, permission__user__pk=user_pk)
    else:
        contour = Contour.objects.get(server__id=server_pk)

    return contour


def get_server(user_pk, server_pk):
    #
    # Function for server validation, saves from invoking server that does not available for current user
    # returns Serverinstance

    # should pass permission__user here for safer execution with permissions
    # user can not invoke server with no permissions for it
    if is_superuser(user_pk) != True:
        server = Server.objects.get(pk=server_pk, permission__user__pk=user_pk)
    else:
        server = Server.objects.get(pk=server_pk)

    if not server:
        raise KeyError('Server with pk {} is not permitted for this user.'.format(server_pk))

    return server


def get_command_for_server(user_pk, server_pk, command_pk, add_args=None):
    #
    # Function for command validation, saves from executing command that does not exist for the chosen server
    # or not available for current user
    # returns ServerCommand instance

    # should pass permission__user here for safer execution with permissions
    # user can not execute command with no permissions for it

    def set_command_additional_parameters(command_text, add_args):
        for arg in zip(add_args['pk'], add_args['value']):
            command_text = re.sub(u'\%({})\|([\w\s]+)\%'.format(arg[0]), arg[1], command_text)

        return command_text

    if is_superuser(user_pk) != True:
        server_command = ServerCommand.cobjects. \
            get(permission__user__pk=user_pk, server=get_server(user_pk, server_pk), pk=command_pk)
    else:
        server_command = ServerCommand.objects.get(pk=command_pk)

    if not server_command:
        raise KeyError('Command with pk {} does not exist for this server.'.format(command_pk))

    if add_args:
        return set_command_additional_parameters(server_command.command, add_args)
    else:
        return server_command.command


def get_command_additional_parameters(**kwargs):
    def get_attr_name(command_text):
        return re.findall(u'\%([A-Z_]+)\|([\w\s]+)\%', command_text)

    if kwargs.get('command_pk'):
        return get_attr_name(ServerCommand.objects.get(pk=kwargs['command_pk']).command)
    elif kwargs.get('command_text'):
        return get_attr_name(kwargs['command_text'])
    else:
        return None


def create_cscu_start(user_pk, server_pk, command_pk, add_args=None):
    cscu_obj = CSCU.objects.create(contour_id=get_contour(user_pk, server_pk).pk, server_id=server_pk,
                                   servercommand_id=command_pk, parameters='\n'.join(add_args), user_id=user_pk,
                                   locked_status=True, start_time=datetime.now())
    return cscu_obj.pk


def create_cscu_finish(cscu_pk, cmd_output, is_success=True):
    # should not use update method here
    # because there no signal is sending using it
    # cscu = CSCU.objects.filter(pk=cscu_pk).update(locked_status=False, end_time=datetime.now(),
    #                                       cmd_output=cmd_output, is_success=is_success)
    cscu = CSCU.objects.get(id=cscu_pk)

    cscu.locked_status = False
    cscu.end_time = datetime.now()
    cscu.cmd_output = cmd_output
    cscu.is_success = is_success
    # cscu.celery_task_id = task_id

    cscu.save()


def unpack_list(params):
    for e in params:
        if isinstance(params[e], dict):
            if len(params[e].get('pk')) == 1:
                params[e]['pk'] = ''.join(params[e].get('pk'))
            if len(params[e].get('value')) == 1:
                params[e]['value'] = ''.join(params[e].get('value'))

    return params

class HistoryLogger():
    def __init__(self, server, command, user, start_time):
        self.cscu = CSCU.objects.create(contour=server.contour, server=server,
                                        servercommand=command, user=user,
                                        locked_status=True, start_time=start_time)

    def save(self, force_update=False):
        self.cscu.save(force_update=force_update)

    def unlock_command(self, end_time):
        self.cscu.locked_status = False
        self.cscu.end_time = end_time
        self.cscu.is_success = True
        self.save(force_update=True)
