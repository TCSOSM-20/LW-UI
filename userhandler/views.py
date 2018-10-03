from django.shortcuts import render, redirect
from sf_t3d.decorators import login_required
from django.http import HttpResponse
import json
import logging
import authosm.utils as osmutils
from lib.osm.osmclient.clientv2 import Client

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


@login_required
def user_list(request):
    user = osmutils.get_user(request)
    client = Client()
    result = client.user_list(user.get_token())
    result = {
        'users': result['data'] if result and result['error'] is False else []
    }
    return __response_handler(request, result, 'user_list.html')


@login_required
def create(request):
    user = osmutils.get_user(request)
    client = Client()
    user_data ={
        "username": request.POST['username'],
        "password": request.POST['password'],
        "projects": request.POST.getlist('projects')
    }

    result = client.user_create(user.get_token(), user_data)

    return __response_handler(request, result, 'users:list', to_redirect=True)


@login_required
def delete(request, user_id=None):
    user = osmutils.get_user(request)
    try:
        client = Client()
        del_res = client.user_delete(user.get_token(), user_id)
    except Exception as e:
        log.exception(e)
    return __response_handler(request, {}, 'users:list', to_redirect=True, )

@login_required
def update(request, user_id=None):
    user = osmutils.get_user(request)
    try:
        client = Client()
        projects_old = request.POST.get('projects_old').split(',')
        projects_new = request.POST.getlist('projects')
        default_project = request.POST.get('default_project')
        projects_new.append(default_project)
        projects_to_add = list(set(projects_new) - set(projects_old))
        projects_to_remove = list(set(projects_old) - set(projects_new))

        payload = {}

        for p in projects_to_remove:
            payload["$"+str(p)] = None
        for p in projects_to_add:
            if p not in projects_old:
                payload["$+"+str(p)] = str(p)
        payload["$" + default_project] = None
        payload["$+[0]"] = default_project

        update_res = client.user_update(user.get_token(), user_id, {"projects": payload})
    except Exception as e:
        log.exception(e)
    return __response_handler(request, {}, 'users:list', to_redirect=True, )


def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types or url is None:
        return HttpResponse(json.dumps(data_res), content_type="application/json", *args, **kwargs)
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)
