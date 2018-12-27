from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.utils.safestring import mark_safe

import json

from .models import Server, ServerCommand
from .ssh_modules import check_socket_openned


def main_view(request):
    return render(request, 'main/main.html')


class ServerDetail(DetailView):
    model = Server

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['commands'] = ServerCommand.objects.filter(server=self.object)
        context['server_id_json'] = mark_safe(json.dumps(self.object.id))
        return context


class ServersListView(ListView):
    model = Server
    paginate_by = 100

    def create_object(self, context):
        for server in context['server_list']:
            if check_socket_openned(server.ip_address, server.ssh_port) == 0:
                server.status = 'online'
            else:
                server.status = 'offline'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.create_object(context)
        return context
