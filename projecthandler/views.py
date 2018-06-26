#
#   Copyright 2017 CNIT - Consorzio Nazionale Interuniversitario per le Telecomunicazioni
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

import json
import logging

import yaml
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from lib.util import Util
from projecthandler.osm_model import OsmProject
from lib.osm.osmclient.clientv2 import Client


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('projecthandler/view.py')


@login_required
def home(request):
    return render(request, 'home.html', {})


@login_required
def create_new_project(request):
    if request.method == 'POST':
        client = Client()
        new_project_dict = request.POST.dict()
        keys = ["name"]
        project_data = dict(filter(lambda i: i[0] in keys and len(i[1]) > 0, new_project_dict.items()))
        result = client.project_create(request.session['token'], project_data)
        if isinstance(result, dict) and 'error' in result and result['error']:
            print result
            return __response_handler(request, result['data'], url=None,
                                      status=result['data']['status'] if 'status' in result['data'] else 500)
        else:
            return __response_handler(request, {}, url=None, status=200)


@login_required
def user_projects(request):
    client = Client()
    result = client.project_list(request.session['token'])
    return render(request, 'projectlist.html', {
        'projects': result['data'] if result and result['error'] is False else [],
    })


@login_required
def open_project(request, project_id=None):
    try:
        user = request.user
        client = Client()
        ##TODO change with adhoc api call
        nsd = client.nsd_list(request.session['token'])
        vnfd = client.vnfd_list(request.session['token'])
        ns = client.ns_list(request.session['token'])
        vnf = client.vnf_list(request.session['token'])
        project_overview = {
            'owner': user.username,
            'name': project_id,
            'updated_date': '-',
            'created_date': '-',
            'info': '-',
            'type': 'osm',
            'nsd': len(nsd['data']) if nsd and nsd['error'] is False else 0,
            'vnfd': len(vnfd['data']) if vnfd and vnfd['error'] is False else 0,
            'ns': len(ns['data']) if ns and ns['error'] is False else 0,
            'vnf': len(vnf['data']) if vnf and vnf['error'] is False else 0,
        }
        return render(request, 'osm/osm_project_details.html',
                      {'project_overview': project_overview, 'project_id': project_id})

    except Exception as e:
        print e
        return render(request, 'error.html', {'error_msg': 'Error open project! Please retry.'})


@login_required
def delete_project(request, project_id=None):
    client = Client()
    result = client.project_delete(request.session['token'], project_id)
    if isinstance(result, dict) and 'error' in result and result['error']:
        print result
        return __response_handler(request, result['data'], url=None,
                                  status=result['data']['status'] if 'status' in result['data'] else 500)
    else:
        return __response_handler(request, {}, url=None, status=200)


@login_required
def show_descriptors(request, project_id=None, descriptor_type=None):
    client = Client()
    print request.GET.dict()
    try:
        if descriptor_type == 'nsd':
            descriptors = client.nsd_list(request.session['token'])
        elif descriptor_type == 'vnfd':
            descriptors = client.vnfd_list(request.session['token'])
    except Exception as e:
        log.exception(e)
        descriptors = []

    url = 'osm/osm_project_descriptors.html'
    return __response_handler(request, {
        'descriptors': descriptors['data'] if descriptors and descriptors['error'] is False else [],
        'project_id': project_id,
        'project_type': 'osm',
        'descriptor_type': descriptor_type
    },url)


@login_required
def delete_descriptor(request, project_id=None, descriptor_type=None, descriptor_id=None):

    try:
        client = Client()
        if descriptor_type == 'nsd':
            result = client.nsd_delete(request.session['token'], descriptor_id)
        elif descriptor_type == 'vnfd':
            result = client.vnfd_delete(request.session['token'], descriptor_id)
    except Exception as e:
        log.exception(e)
        result = {'error': True, 'data': str(e)}

    url = 'osm/osm_project_descriptors.html'
    descriptors = {}
    try:
        if descriptor_type == 'nsd':
            descriptors = client.nsd_list(request.session['token'])
        elif descriptor_type == 'vnfd':
            descriptors = client.vnfd_list(request.session['token'])
    except Exception as e:
        log.exception(e)

    return __response_handler(request, {
        'descriptors': descriptors['data'] if descriptors and descriptors['error'] is False else [],
        'project_id': project_id,
        'project_type': 'osm',
        'descriptor_type': descriptor_type,
        'alert_message': {
            'success': False if result['error'] is True else True,
            'message': 'An error occurred while processing your request.' if result and result['error'] is True else "Record deleted successfully"}
    }, url)



@login_required
def new_descriptor(request, project_id=None, descriptor_type=None):

    page = 'osm/descriptor/descriptor_new.html'
    if request.method == 'GET':
        request_id = request.GET.get('id', '')

        return __response_handler(request,  {
            'project_id': project_id,
            'descriptor_type': descriptor_type,
            'descriptor_id': request_id,
        }, page)
    elif request.method == 'POST':
        data_type = request.POST.get('type')
        print "TYPE", data_type
        if data_type == "file":
            file_uploaded = request.FILES['file']

            try:
                client = Client()
                if descriptor_type == 'nsd':
                    result = client.nsd_onboard(request.session['token'], file_uploaded)
                elif descriptor_type == 'vnfd':
                    result = client.vnfd_onboard(request.session['token'], file_uploaded)
                else:
                    log.debug('Create descriptor: Unknown data type')
                    result = {'error': True, 'data': 'Create descriptor: Unknown data type'}

            except Exception as e:
                log.exception(e)
                result = {'error': True, 'data': str(e)}
        else:
            result = {'error': True, 'data': 'Create descriptor: Unknown data type'}

        if result['error']:
            print result
            return __response_handler(request, result['data'], url=None, status=result['data']['status'] if 'status' in result['data'] else 500)
        else:
            return __response_handler(request, {}, url=None, status=200)


@login_required
def edit_descriptor(request, project_id=None, descriptor_id=None, descriptor_type=None):
    if request.method == 'POST':
        print "edit_descriptor"
        new_data = request.POST.get('text'),
        data_type = request.POST.get('type')
        #print new_data
        try:
            client = Client()
            if descriptor_type == 'nsd':
                if data_type == 'yaml':
                    new_data = yaml.load(request.POST.get('text'))
                elif data_type == 'json':
                    new_data = json.loads(request.POST.get('text'))
                print new_data
                result = client.nsd_update(request.session['token'], descriptor_id, new_data)
            elif descriptor_type == 'vnfd':
                if data_type == 'yaml':
                    new_data = yaml.load(request.POST.get('text'))
                elif data_type == 'json':
                    new_data = json.loads(request.POST.get('text'))
                print new_data
                result = client.vnfd_update(request.session['token'], descriptor_id, new_data)

            else:
                log.debug('Update descriptor: Unknown data type')
                result = {'error': True, 'data': 'Update descriptor: Unknown data type'}
        except Exception as e:
            log.exception(e)
            result = {'error': True, 'data': str(e)}
        print result
        if result['error'] == True:
            return __response_handler(request, result['data'], url=None, status=result['data']['status'] if 'status' in result['data'] else 500)

        else:
            return __response_handler(request, {}, url=None, status=200)

    elif request.method == 'GET':

        page = 'osm/descriptor/descriptor_view.html'
        try:
            client = Client()
            if descriptor_type == 'nsd':
                result = client.nsd_get(request.session['token'], descriptor_id)
                print result
            elif descriptor_type == 'vnfd':
                result = client.vnfd_get(request.session['token'], descriptor_id)

                print result
        except Exception as e:
            log.exception(e)
            result = {'error': True, 'data': str(e)}

        if isinstance(result, dict) and 'error' in result and result['error']:
            return render(request, 'error.html')

        descriptor_string_json = json.dumps(result, indent=2)
        descriptor_string_yaml = Util.json2yaml(result)
        # print descriptor
        return render(request, page, {
            'project_id': project_id,
            'descriptor_id': descriptor_id,
            'descriptor_type': descriptor_type,
            'descriptor_strings': {'descriptor_string_yaml': descriptor_string_yaml,
                                   'descriptor_string_json': descriptor_string_json}})


@login_required
def get_package_files_list(request, project_id, descriptor_id, descriptor_type):
    files_list = []
    try:
        client = Client()
        if descriptor_type == 'nsd':
            artifacts_res = client.nsd_artifacts(request.session['token'], descriptor_id)
        elif descriptor_type == 'vnfd':
            artifacts_res = client.vnf_packages_artifacts(request.session['token'], descriptor_id)
        else:
            return False

        files_list = yaml.load(artifacts_res['data'] if artifacts_res and artifacts_res['error'] is False else [])
        result = {'files': files_list}
    except Exception as e:
        log.exception(e)
        url = 'error.html'
        result = {'error_msg': 'Unknown error.'}
    return __response_handler(request, result)

@login_required
def download_pkg(request, project_id, descriptor_id, descriptor_type):
    file_name = "osm_export.tar.gz"
    tar_pkg = None
    try:
        client = Client()
        if descriptor_type == 'nsd':
            tar_pkg = client.get_nsd_pkg(request.session['token'], descriptor_id)
        elif descriptor_type == 'vnfd':
            tar_pkg = client.get_vnfd_pkg(request.session['token'], descriptor_id)

    except Exception as e:
        log.exception(e)

    response = HttpResponse(content_type="application/tgz")
    response["Content-Disposition"] = "attachment; filename="+ file_name
    response.write(tar_pkg.getvalue())
    return response


@login_required
def custom_action(request, project_id=None, descriptor_id=None, descriptor_type=None, action_name=None):
    if request.method == 'GET':
        print "Custom action: " + action_name
        return globals()[action_name](request, project_id, descriptor_id, descriptor_type)


def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types or url is None:
        return HttpResponse(json.dumps(data_res), content_type="application/json", *args, **kwargs)
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)
