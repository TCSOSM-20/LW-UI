from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from projecthandler.models import Project
from authosm.models import OsmUser


@login_required
def home(request):
    user = OsmUser.objects.get(id=request.user.id)

    projects = Project.objects.filter(owner=user).select_subclasses()
    result = {
        'projects': len(projects) if projects else 0,
    }
    return redirect('projects:open_project', project_id='admin')
    #return render(request, 'home.html', result)


def forbidden(request):
    return render(request, 'forbidden.html')



