#
#   Copyright 2019 EveryUP Srl
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
import yaml
import json
import logging
import authosm.utils as osmutils
from lib.osm.osmclient.clientv2 import Client

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


@login_required
def role_list(request):
    user = osmutils.get_user(request)
    client = Client()
    result = client.role_list(user.get_token())
    result = {
        'roles': result['data'] if result and result['error'] is False else []
    }
    return __response_handler(request, result, 'role_list.html')


@login_required
def create(request):
    user = osmutils.get_user(request)
    client = Client()
    role_data ={
       'name': request.POST['name'],
    }
    try:
        if 'permissions' in request.POST and request.POST.get('permissions') != '':
            role_permissions = yaml.load(request.POST.get('permissions'))

            if not isinstance(role_permissions, dict):
                    raise ValueError('Role permissions should be provided in a key-value fashion')
            for key, value in role_permissions.items():
                if not isinstance(value, bool):
                    raise ValueError("Value of '{}' in a role permissionss should be boolean".format(key))
                role_data[key] = value
    except Exception as e:
        return __response_handler(request, {'status': 400, 'code': 'BAD_REQUEST', 'detail': e.message} , url=None, status=400)
    result = client.role_create(user.get_token(), role_data)
    if result['error']:
        return __response_handler(request, result['data'], url=None,
                                  status=result['data']['status'] if 'status' in result['data'] else 500)
    else:
        return __response_handler(request, {}, url=None, status=200)


@login_required
def delete(request, role_id=None):
    user = osmutils.get_user(request)
    try:
        client = Client()
        result = client.role_delete(user.get_token(), role_id)
    except Exception as e:
        log.exception(e)
        result = {'error': True, 'data': str(e)}
    if result['error']:
        return __response_handler(request, result['data'], url=None,
                                  status=result['data']['status'] if 'status' in result['data'] else 500)
    else:
        return __response_handler(request, {}, url=None, status=200)

@login_required
def update(request, role_id=None):
    user = osmutils.get_user(request)
    client = Client()
    payload = {
        'name': request.POST['name'],
    }
    try:
        if 'permissions' in request.POST and request.POST.get('permissions') != '':
            role_permissions = yaml.load(request.POST.get('permissions'))

            if not isinstance(role_permissions, dict):
                    raise ValueError('Role permissions should be provided in a key-value fashion')
            for key, value in role_permissions.items():
                if not isinstance(value, bool):
                    raise ValueError('Value in a role permissions should be boolean')
                payload[key] = value
    except Exception as e:
        return __response_handler(request, {'status': 400, 'code': 'BAD_REQUEST', 'detail': e.message} , url=None, status=400)
    result = client.role_update(user.get_token(), role_id, payload)
    if result['error']:
        return __response_handler(request, result['data'], url=None,
                                  status=result['data']['status'] if 'status' in result['data'] else 500)
    else:
        return __response_handler(request, {}, url=None, status=200)

@login_required
def get(request, role_id=None):
    user = osmutils.get_user(request)
    try:
        client = Client()
        get_res = client.role_get(user.get_token(), role_id)
    except Exception as e:
        log.exception(e)
        get_res = {'error': True, 'data': str(e)}
    if get_res['error']:
        return __response_handler(request, get_res['data'], url=None,
                                  status=get_res['data']['status'] if 'status' in get_res['data'] else 500)
    else:
        role = get_res['data']
        result = {
            '_id': role['_id'],
            'name': role['name'],
            'permissions': { key:value for key, value in role['permissions'].items() if key not in ['_id', 'name', 'root', '_admin'] }
        }
        return __response_handler(request, result, url=None, status=200)


def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types or url is None:
        return HttpResponse(json.dumps(data_res), content_type="application/json", *args, **kwargs)
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)
