from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from discord_bottachable.models import Server, Link

import logging

# Create an instance of logger
logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    return render(request, 'index.html', {'servers': Server.objects.all()})


def server(request, server_id, tags):
    s = get_object_or_404(Server, discord_id=server_id)
    all_links = Link.objects.filter(server_id=s)

    current_tags = ""
    tags_array = tags_to_array(tags)
    current_tags = ",".join(tags_array)
    all_links = filterByTags(all_links, tags_array)

    paginator = Paginator(all_links, 10)

    page = request.GET.get('page')
    try:
        links = paginator.page(page)
    except PageNotAnInteger:
        links = paginator.page(1)
    except EmptyPage:
        links = paginator.page(paginator.num_pages)

    return render(request, 'server.html', {
        'links': links,
        'server_id': server_id,
        'server_name': s.name,
        'tags': tags_array,
        'current_tags': current_tags 
    })

def filterByTags(all_links, tags_array):
    for tag in tags_array: 
        all_links = all_links.filter(tags__name=tag)

    return all_links

def tags_to_array(tags):
    try:
        # Because splitting an empty string still returns an array containing
        # an empty string
        if len(tags) > 0:
            tags_array = tags.split(',')
            # Remove duplicates
            tags_array = list(set(tags_array))
        else:
            tags_array = []
    except Exception as e:
        tags_array = []
    return tags_array