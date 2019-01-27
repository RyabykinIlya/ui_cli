from datetime import datetime

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


def get_command_for_server(user_pk, server_pk, command_pk):
    #
    # Function for command validation, saves from executing command that does not exist for the chosen server
    # or not available for current user
    # returns ServerCommand instance

    # should pass permission__user here for safer execution with permissions
    # user can not execute command with no permissions for it
    if is_superuser(user_pk) != True:
        server_command = ServerCommand.cobjects. \
            get(permission__user__pk=user_pk, server=get_server(user_pk, server_pk), pk=command_pk)
    else:
        server_command = ServerCommand.objects.get(pk=command_pk)
    if not server_command:
        raise KeyError('Command with pk {} does not exist for this server.'.format(command_pk))

    return server_command

def create_cscu_start(user_pk, server_pk, command_pk):
    cscu_obj = CSCU.objects.create(contour_id=get_contour(user_pk, server_pk).pk, server_id=server_pk,
                        servercommand_id=command_pk, user_id=user_pk,
                        locked_status=True, start_time=datetime.now())
    return cscu_obj.pk

def create_cscu_finish(cscu_pk, cmd_output, is_success=True):
    # should not use update method here
    # because there no signal is sending using it
    #cscu = CSCU.objects.filter(pk=cscu_pk).update(locked_status=False, end_time=datetime.now(),
    #                                       cmd_output=cmd_output, is_success=is_success)
    cscu = CSCU.objects.get(id=cscu_pk)

    cscu.locked_status = False
    cscu.end_time = datetime.now()
    cscu.cmd_output = cmd_output
    cscu.is_success = is_success

    cscu.save()

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
