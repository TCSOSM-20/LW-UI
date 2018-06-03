#
#   Copyright 2018 CNIT - Consorzio Nazionale Interuniversitario per le Telecomunicazioni
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
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from lib.osm.osmclient.client import Client
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('view.py')


@login_required
def list(request, project_id):
    client = Client()
    result = client.sdn_list()

    result = {
        'project_id': project_id,
        'sdns': result
    }
    return __response_handler(request, result, 'sdn_list.html')


@login_required
def create(request, project_id):
    result = {'project_id': project_id}
    if request.method == 'GET':
        return __response_handler(request, result, 'sdn_create.html')
    else:
        new_sdn_dict = request.POST.dict()
        client = Client()
        keys = ["name",
                "type",
                "version",
                "dpid",
                "ip",
                "port",
                "user",
                "password"]
        sdn_data = dict(filter(lambda i: i[0] in keys and len(i[1]) > 0, new_sdn_dict.items()))
        sdn_data['port'] = int(sdn_data['port'])

        result = client.sdn_create(sdn_data)

        return __response_handler(request, result, 'projects:sdns:list', to_redirect=True, project_id=project_id)


@login_required
def delete(request, project_id, sdn_id=None):
    try:
        client = Client()
        del_res = client.sdn_delete(sdn_id)
    except Exception as e:
        log.exception(e)
    return __response_handler(request, {}, 'projects:sdns:list', to_redirect=True, project_id=project_id)


@login_required
def show(request, project_id, sdn_id=None):
    client = Client()
    datacenter = client.sdn_get(sdn_id)
    return __response_handler(request, {
        "sdn": datacenter
    }, project_id=project_id)


def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types:
        return JsonResponse(data_res)
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)