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
log = logging.getLogger('k8sclusterhandler/view.py')


@login_required
def list(request):
    user = osmutils.get_user(request)
    project_id = user.project_id
    result = {'project_id': project_id}
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' not in raw_content_types:
        return __response_handler(request, result, 'k8scluster_list.html')
    client = Client()
    result_client = client.k8sc_list(user.get_token())

    result['k8sc'] = result_client['data'] if result_client and result_client['error'] is False else []

    return __response_handler(request, result, 'k8scluster_list.html')


@login_required
def create(request):
    user = osmutils.get_user(request)
    project_id = user.project_id
    result = {'project_id': project_id}
    client = Client()
    try:

        new_k8sc = {
            "name": request.POST.get('name'),
            "credentials": yaml.load(request.POST.get('credentials')),
            "vim_account": request.POST.get('vim_account'),
            "k8s_version": request.POST.get('k8s_version'),
            "nets": yaml.load(request.POST.get('nets')),
        }

        # new_k8sc['vim_account'] = get_vim_account_id(new_k8sc['vim_account'])

    except Exception as e:
        return __response_handler(request, {'status': 400, 'code': 'BAD_REQUEST', 'detail': e.message}, url=None, status=400)
    result = client.k8sc_create(user.get_token(), new_k8sc)
    if result['error']:
        return __response_handler(request, result['data'], url=None, status=result['data']['status'] if 'status' in result['data'] else 500)
    else:
        return __response_handler(request, result, 'k8sc:list', to_redirect=True)


@login_required
def update(request, k8sc_id=None):
    user = osmutils.get_user(request)
    try:
        update_k8sc_dict = request.POST.dict()
        client = Client()
        res = client.k8sc_update(user.get_token(), k8sc_id, update_k8sc_dict)
    except Exception as e:
        log.exception(e)
    return __response_handler(request, res, 'k8sc:list', to_redirect=True)


@login_required
def show(request, k8sc_id=None):
    user = osmutils.get_user(request)
    project_id = user.project_id
    client = Client()
    result_client = client.k8sc_get(user.get_token(), k8sc_id)

    return __response_handler(request, result_client)


@login_required
def delete(request, k8sc_id=None):
    user = osmutils.get_user(request)
    try:
        client = Client()
        del_res = client.k8sc_delete(user.get_token(), k8sc_id)
    except Exception as e:
        log.exception(e)
    return __response_handler(request, del_res, 'k8sc:list', to_redirect=True)


def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types or url is None:
        return HttpResponse(json.dumps(data_res), content_type="application/json", *args, **kwargs)
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)
