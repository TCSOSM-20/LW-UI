from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from projecthandler.models import Project
from authosm.models import OsmUser


@login_required
def home(request):
    return redirect('projects:open_project')


def forbidden(request):
    return render(request, 'forbidden.html')



