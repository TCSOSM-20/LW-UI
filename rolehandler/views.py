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
       'name'
    }
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
    try:
        client = Client()
        payload = {}
        if request.POST.get('name') and request.POST.get('name') is not '':
            payload["name"] = request.POST.get('name')
        update_res = client.role_update(user.get_token(), role_id, payload)
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
