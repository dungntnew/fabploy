from django.shortcuts import render
from django.http import HttpResponse
from .models import Album


def index(request):
    all_albums = Album.objects.all()
    context = {'all_albums': all_albums}
    return render(request=request, template_name='music/index.html', context=context)


def detail(request, album_id):
    return HttpResponse('<h2>Details for Album id: {0}</h2>'.format(album_id))
