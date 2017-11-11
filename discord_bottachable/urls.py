"""discord_bottachable URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

import discord_bottachable.views

urlpatterns = [
    url(r'^$', discord_bottachable.views.index, name='index'),
    url(
        r'^(?P<server_id>[0-9]+)/$', 
        discord_bottachable.views.server,
        name='server'
    ),
    url(
        r'^(?P<server_id>[0-9]+)/tags/$',
        discord_bottachable.views.server,
        name='server'
    ),
    url(
        r'^(?P<server_id>[0-9]+)/tags/(?P<tags>(\w(-)*)+(,(\w(-)*)+)*)$',
        discord_bottachable.views.server,
        name='server'
    ),
    url(
        r'^(?P<server_id>[0-9]+)/search/$',
        discord_bottachable.views.server,
        name='server'
    ),
    url(
        r'^(?P<server_id>[0-9]+)/search/(?P<keywords>(\w(-)*( )*)+(,(\w(-)*( )*)+)*)/$',
        discord_bottachable.views.server,
        name='server'
    ),
    url(
        r'^(?P<server_id>[0-9]+)/search/(?P<keywords>(\w(-)*( )*)+(,(\w(-)*( )*)+)*)/tags/$',
        discord_bottachable.views.server,
        name='server'
    ),
    url(
        r'^(?P<server_id>[0-9]+)/search/(?P<keywords>(\w(-)*( )*)+(,(\w(-)*( )*)+)*)/tags/(?P<tags>(\w(-)*)+(,(\w(-)*)+)*)$',
        discord_bottachable.views.server,
        name='server'
    ),
]
