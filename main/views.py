from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.utils.safestring import mark_safe
# from django.contrib.auth.models import User

import json
from itertools import groupby

from .models import Server, ServerCommand, Contour, CSCU
from .ssh_modules import check_socket_openned
from .helpers import get_user, get_command_additional_parameters


def main_view(request):
    return render(request, 'main/main.html')


class ServerDetail(DetailView):
    model = Server

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['commands'] = ServerCommand.cobjects.filter(server=self.object).get_restricted(user=get_user(self))
        context['server_id_json'] = mark_safe(json.dumps(self.object.id))
        return context


class ServerListView(ListView):
    paginate_by = 100
    template_name = 'main/server_list.html'

    def check_server_status(self, context):
        for dict in context['object_list']:
            for servers in dict.values():
                for server in servers:
                    if check_socket_openned(server.ip_address, server.ssh_port):
                        server.status = 'online'
                    else:
                        server.status = 'offline'

    def get_queryset(self):
        servers_dict = Server.cobjects.all().prefetch_related('contour').get_restricted(user=get_user(self)).order_by('contour')

        # creates list of dicts with structure
        # [{contour.name: <Server object>, <Server object>}, {..}, {..}]
        grouped_sorted_servers = [{group[0]: list(group[1])} for group in
                                  groupby(sorted(sorted(servers_dict,
                                                        key=lambda server: server.contour.name),
                                                 key=lambda server: server.contour.order_by)
                                          , lambda server: server.contour.name)]
        return grouped_sorted_servers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.check_server_status(context)
        return context

class CSCUListView(ListView):
    model = CSCU
    template_name = 'main/cscu_list.html'
    paginate_by = 50

    # def get_queryset(self):
    #    return super().get_queryset().order_by('-start_time')

    def get_context_data(self, **kwargs):
        object_list = CSCU.objects.all().prefetch_related('user', 'contour', 'server', 'servercommand').order_by('-start_time')
        context = super().get_context_data(
            object_list=object_list.filter(locked_status=False)
                , **kwargs)
        context['cscu_in_progress'] = object_list.filter(locked_status=True)

        return context


class ServerCommandListView(ListView):
    model = ServerCommand
    template_name = 'main/servercommand_list.html'
    paginate_by = 100

    def get_queryset(self):
        server_commands = ServerCommand.cobjects.all().get_restricted(user=get_user(self)).order_by('name')
        return server_commands

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get locked status for each command

        locked_commands = CSCU.objects.filter(locked_status=True)
        for command in context['object_list']:
            if command.with_parameters:
                command.ad_params = get_command_additional_parameters(command_text=command.command)

            if command.lock_enable:
                if any(cmd.servercommand.id == command.id for cmd in locked_commands):
                    command.locked_on = ', '.join(
                        set(
                            [x.server.name for x in locked_commands if x.servercommand.id == command.id]
                        )
                    )
            if not hasattr(command, 'locked_on'):
                command.locked_on = ''

        return context
