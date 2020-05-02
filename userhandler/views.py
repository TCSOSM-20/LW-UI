#
#   Copyright 2018 EveryUP Srl
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an  BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

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

    new_user_dict = request.POST.dict()
    keys = ["username", "password", "domain_name"]
    user_data = dict(filter(lambda i: i[0] in keys and len(i[1]) > 0, new_user_dict.items()))
    result = client.user_create(user.get_token(), user_data)
    if result['error']:
        return __response_handler(request, result['data'], url=None,
                                  status=result['data']['status'] if 'status' in result['data'] else 500)
    else:
        return __response_handler(request, {}, url=None, status=200)


@login_required
def delete(request, user_id=None):
    user = osmutils.get_user(request)
    try:
        client = Client()
        result = client.user_delete(user.get_token(), user_id)
    except Exception as e:
        log.exception(e)
        result = {'error': True, 'data': str(e)}
    if result['error']:
        return __response_handler(request, result['data'], url=None,
                                  status=result['data']['status'] if 'status' in result['data'] else 500)
    else:
        return __response_handler(request, {}, url=None, status=200)


@login_required
def user_info(request, user_id=None):
    user = osmutils.get_user(request)
    try:
        client = Client()

        info_res = client.get_user_info(user.get_token(), user_id)
    except Exception as e:
        log.exception(e)
        info_res = {'error': True, 'data': str(e)}
    if info_res['error']:
        return __response_handler(request, info_res['data'], url=None,
                                  status=info_res['data']['status'] if 'status' in info_res['data'] else 500)
    else:
        return __response_handler(request, info_res['data'], url=None, status=200)


@login_required
def update(request, user_id=None):
    user = osmutils.get_user(request)
    try:
        client = Client()
        payload = {}

        if request.POST.get('password') and request.POST.get('password') is not '':
            payload["password"] = request.POST.get('password')

        if request.POST.getlist('map_project_name') and request.POST.getlist('map_role_name'):
            project_param_name = request.POST.getlist('map_project_name')
            role_param_ip = request.POST.getlist('map_role_name')
            payload["project_role_mappings"] = []
            for i, project in enumerate(project_param_name):
                payload["project_role_mappings"].append({
                    'project': project,
                    'role': role_param_ip[i],
                })

        update_res = client.user_update(user.get_token(), user_id, payload)
    except Exception as e:
        log.exception(e)
        update_res = {'error': True, 'data': str(e)}
    if update_res['error']:
        return __response_handler(request, update_res['data'], url=None,
                                  status=update_res['data']['status'] if 'status' in update_res['data'] else 500)
    else:
        return __response_handler(request, {}, url=None, status=200)


def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types or url is None:
        return HttpResponse(json.dumps(data_res), content_type="application/json", *args, **kwargs)
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)
