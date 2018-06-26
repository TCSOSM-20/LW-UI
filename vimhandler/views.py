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
from django.http import HttpResponse
import json
#from lib.osm.osmclient.client import Client
from lib.osm.osmclient.clientv2 import Client
import yaml
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('view.py')


@login_required
def list(request, project_id):
    client = Client()
    result = client.vim_list(request.session['token'])
    print result
    result = {
        "project_id": project_id,
        "datacenters": result['data'] if result and result['error'] is False else []
    }
    return __response_handler(request, result, 'vim_list.html')


@login_required
def create(request, project_id):
    result = {'project_id': project_id}
    if request.method == 'GET':
        return __response_handler(request, result, 'vim_create.html')
    else:
        new_vim_dict = request.POST.dict()
        client = Client()
        keys = ["schema_version",
                "schema_type",
                "name",
                "vim_url",
                "vim_type",
                "vim_user",
                "vim_password",
                "vim_tenant_name",
                "description"]
        vim_data = dict(filter(lambda i: i[0] in keys and len(i[1]) > 0, new_vim_dict.items()))
        vim_data['config'] = {}
        for k, v in new_vim_dict.items():
            if str(k).startswith('config_') and len(v) > 0:
                config_key = k[7:]
                vim_data['config'][config_key] = v
        if 'additional_conf' in new_vim_dict:
            try:
                additional_conf_dict = yaml.safe_load(new_vim_dict['additional_conf'])
                for k,v in additional_conf_dict.items():
                    vim_data['config'][k] = v
            except Exception as e:
                # TODO return error on json.loads exception
                print e
        result = client.vim_create(request.session['token'], vim_data)
        # TODO  'vim:show', to_redirect=True, vim_id=vim_id
        return __response_handler(request, result, 'projects:vims:list', to_redirect=True, project_id=project_id)

@login_required
def delete(request, project_id, vim_id=None):
    try:
        client = Client()
        del_res = client.vim_delete(request.session['token'], vim_id)
    except Exception as e:
        log.exception(e)
    return __response_handler(request, {}, 'projects:vims:list', to_redirect=True, project_id=project_id)

@login_required
def show(request, project_id, vim_id=None):
    client = Client()
    result = client.vim_get(request.session['token'], vim_id)
    print result
    if isinstance(result, dict) and 'error' in result and result['error']:
        return render(request, 'error.html')

    return __response_handler(request, {
        "datacenter": result['data'],
        "project_id": project_id
    }, 'vim_show.html')


def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types or url is None:
        return HttpResponse(json.dumps(data_res), content_type="application/json", *args, **kwargs)
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)
