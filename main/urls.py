"""ui_cli URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from . import views
from .consumers import \
    SyncCommandsConsumer, AsyncCommandsConsumer, SyncCommandServerConsumer

urlpatterns = [
    path('', views.main_view, name='main'),
    path('servers/', views.ServerListView.as_view(), name='servers-list'),
    path('server/<int:pk>/', views.ServerDetail.as_view(), name='server-detail'),
    path('commands/history/', views.CSCUListView.as_view(), name='cscu-list'),
    path('commands/', views.ServerCommandListView.as_view(), name='servercommand-list'),
]

urlpatterns += [
    path('django-rq/', include('django_rq.urls'))
]

websocket_urlpatterns = [
    path('ws/server/<int:pk>/', SyncCommandsConsumer),
    path('ws/commands/', SyncCommandServerConsumer),
]
