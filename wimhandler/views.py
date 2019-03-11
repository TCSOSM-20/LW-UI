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

from django.shortcuts import render, redirect
from sf_t3d.decorators import login_required
from django.http import HttpResponse
import json
from lib.osm.osmclient.clientv2 import Client
import authosm.utils as osmutils
import yaml
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('wimhandler.py')


@login_required
def list(request):
    user = osmutils.get_user(request)
    project_id = user.project_id
    result = {'type': 'ns', 'project_id': project_id}
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' not in raw_content_types:
        return __response_handler(request, result, 'wim_list.html')
    client = Client()
    result_client = client.wim_list(user.get_token())
    result["datacenters"] = result_client['data'] if result_client and result_client['error'] is False else []
    return __response_handler(request, result, 'wim_list.html')

@login_required
def create(request):
    user = osmutils.get_user(request)
    project_id = user.project_id
    result = {'project_id': project_id}
    if request.method == 'GET':
        return __response_handler(request, result, 'wim_create.html')
    else:
        new_wim_dict = request.POST.dict()
        client = Client()
        keys = ["schema_version",
                "schema_type",
                "name",
                "description",
                "wim_url",
                "wim_type",
                "user",
                "password",
                "wim",
                "description"]
        wim_data = dict(filter(lambda i: i[0] in keys and len(i[1]) > 0, new_wim_dict.items()))
        wim_data['config'] = {}
        for k, v in new_wim_dict.items():
            if str(k).startswith('config_') and len(v) > 0:
                config_key = k[7:]
                wim_data['config'][config_key] = v
        if 'additional_conf' in new_wim_dict:
            try:
                additional_conf_dict = yaml.safe_load(new_wim_dict['additional_conf'])
                for k,v in additional_conf_dict.items():
                    wim_data['config'][k] = v
            except Exception as e:
                # TODO return error on json.loads exception
                print e
        result = client.wim_create(user.get_token(), wim_data)
        return __response_handler(request, result, 'wims:list', to_redirect=True, )

@login_required
def delete(request, wim_id=None):
    user = osmutils.get_user(request)
    try:
        client = Client()
        del_res = client.wim_delete(user.get_token(), wim_id)
    except Exception as e:
        log.exception(e)
    return __response_handler(request, del_res, 'wims:list', to_redirect=True, )

@login_required
def show(request, wim_id=None):
    user = osmutils.get_user(request)
    project_id = user.project_id
    client = Client()
    result = client.wim_get(user.get_token(), wim_id)
    if isinstance(result, dict) and 'error' in result and result['error']:
        return render(request, 'error.html')

    return __response_handler(request, {
        "wim": result['data'],
        "project_id": project_id
    }, 'wim_show.html')

def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types or url is None:
        return HttpResponse(json.dumps(data_res), content_type="application/json", *args, **kwargs)
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)