from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.utils.safestring import mark_safe

import json

from .models import Server, ServerCommand, Contour, CSCU
from .ssh_modules import check_socket_openned
from .help import get_user


def main_view(request):
    return render(request, 'main/main.html')


class ServerDetail(DetailView):
    model = Server

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['commands'] = ServerCommand.cobjects.filter(server=self.object).get_restricted(user=get_user(self))
        context['server_id_json'] = mark_safe(json.dumps(self.object.id))
        return context


class ServersListView(ListView):
    paginate_by = 100
    template_name = 'main/server_list.html'

    def check_server_status(self, context):
        for contour in context['object_list']:
            for server in contour.servers:
                # for server in context['server_list']:
                if check_socket_openned(server.ip_address, server.ssh_port):
                    server.status = 'online'
                else:
                    server.status = 'offline'

    def get_queryset(self):
        contour_servers = Contour.cobjects.all().get_restricted(user=get_user(self)).order_by('-order_by')
        for contour in contour_servers:
            contour.servers = Server.cobjects.filter(contour=contour).get_restricted(user=get_user(self))
        return contour_servers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.check_server_status(context)
        return context


class CSCUListView(ListView):
    model = CSCU
    template_name = 'main/cscu_list.html'
    paginate_by = 100

    def get_queryset(self):
        return super().get_queryset().order_by('-start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
