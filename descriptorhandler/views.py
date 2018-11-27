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

import json
import logging

import yaml
from sf_t3d.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect


from lib.util import Util
from lib.osm.osmclient.clientv2 import Client
from lib.osm.osm_rdcl_parser import OsmParser
from lib.osm.osm_util import OsmUtil
import authosm.utils as osmutils

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('descriptorhandler/view.py')


@login_required
def show_descriptors(request, descriptor_type=None):
    user = osmutils.get_user(request)
    project_id = user.project_id
    client = Client()
    try:
        if descriptor_type == 'nsd':
            descriptors = client.nsd_list(user.get_token())
        elif descriptor_type == 'vnfd':
            descriptors = client.vnfd_list(user.get_token())
    except Exception as e:
        log.exception(e)
        descriptors = []

    url = 'osm/osm_project_descriptors.html'
    return __response_handler(request, {
        'descriptors': descriptors['data'] if descriptors and descriptors['error'] is False else [],
        'project_id': project_id,
        'project_type': 'osm',
        'descriptor_type': descriptor_type
    }, url)


@login_required
def delete_descriptor(request, descriptor_type=None, descriptor_id=None):
    user = osmutils.get_user(request)
    project_id = user.project_id
    try:
        client = Client()
        if descriptor_type == 'nsd':
            result = client.nsd_delete(user.get_token(), descriptor_id)
        elif descriptor_type == 'vnfd':
            result = client.vnfd_delete(user.get_token(), descriptor_id)
    except Exception as e:
        log.exception(e)
        result = {'error': True, 'data': str(e)}

    url = 'osm/osm_project_descriptors.html'
    descriptors = {}
    try:
        if descriptor_type == 'nsd':
            descriptors = client.nsd_list(user.get_token())
        elif descriptor_type == 'vnfd':
            descriptors = client.vnfd_list(user.get_token())
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
def create_package_empty(request, descriptor_type=None):
    user = osmutils.get_user(request)
    pkg_name = request.POST.get('name', '')
    try:
        client = Client()
        if descriptor_type == 'nsd':
            result = client.nsd_create_pkg_base(user.get_token(), pkg_name)
        elif descriptor_type == 'vnfd':
            result = client.vnfd_create_pkg_base(user.get_token(), pkg_name)
        else:
            log.debug('Update descriptor: Unknown data type')
            result = {'error': True, 'data': 'Update descriptor: Unknown data type'}
    except Exception as e:
        log.exception(e)
        result = {'error': True, 'data': str(e)}

    if result['error'] == True:
        return __response_handler(request, result['data'], url=None,
                                  status=result['data']['status'] if 'status' in result['data'] else 500)
    else:
        result['data']['type'] = descriptor_type
        return __response_handler(request, result, url=None, status=200)


@login_required
def clone_descriptor(request, descriptor_type=None, descriptor_id=None):
    user = osmutils.get_user(request)
    project_id = user.project_id
    try:
        client = Client()
        if descriptor_type == 'nsd':
            result = client.nsd_clone(user.get_token(), descriptor_id)
        elif descriptor_type == 'vnfd':
            result = client.vnfd_clone(user.get_token(), descriptor_id)
        else:
            log.debug('Update descriptor: Unknown data type')
            result = {'error': True, 'data': 'Update descriptor: Unknown data type'}
    except Exception as e:
        log.exception(e)
        result = {'error': True, 'data': str(e)}
    if result['error'] == True:
        return __response_handler(request, result['data'], url=None,
                                  status=result['data']['status'] if 'status' in result['data'] else 500)
    else:
        return __response_handler(request, {}, url=None, status=200)

@login_required
def addElement(request, descriptor_type=None, descriptor_id=None, element_type=None):
    user = osmutils.get_user(request)
    project_id = user.project_id
    client = Client()
    if descriptor_type == 'nsd':
        descriptor_result = client.nsd_get(user.get_token(), descriptor_id)
        element_id = request.POST.get('id', '')
        util = OsmUtil()
        descriptor_updated = util.add_base_node('nsd', descriptor_result, element_type, element_id, request.POST.dict())
        result = client.nsd_update(user.get_token(), descriptor_id, descriptor_updated)
        if result['error'] == True:
            return __response_handler(request, result['data'], url=None,
                                      status=result['data']['status'] if 'status' in result['data'] else 500)
        else:
            parser = OsmParser()
            # print nsr_object
            if descriptor_type == 'nsd':
                result_graph = parser.nsd_to_graph(descriptor_updated)

        return __response_handler(request, result_graph, url=None, status=200)

    elif descriptor_type == 'vnfd':
        descriptor_result = client.vnfd_get(user.get_token(), descriptor_id)
        element_id = request.POST.get('id', '')
        util = OsmUtil()
        descriptor_updated = util.add_base_node('vnfd', descriptor_result, element_type, element_id, request.POST.dict())
        result = client.vnfd_update(user.get_token(), descriptor_id, descriptor_updated)
        if result['error'] == True:
            return __response_handler(request, result['data'], url=None,
                                      status=result['data']['status'] if 'status' in result['data'] else 500)
        else:
            parser = OsmParser()
            # print nsr_object
            if descriptor_type == 'vnfd':
                result_graph = parser.vnfd_to_graph(descriptor_updated)

        return __response_handler(request, result_graph, url=None, status=200)


@login_required
def removeElement(request, descriptor_type=None, descriptor_id=None, element_type=None):
    user = osmutils.get_user(request)
    project_id = user.project_id
    client = Client()
    if descriptor_type == 'nsd':
        descriptor_result = client.nsd_get(user.get_token(), descriptor_id)
        element_id = request.POST.get('id', '')
        util = OsmUtil()
        descriptor_updated = util.remove_node('nsd', descriptor_result, element_type, element_id, request.POST.dict())
        result = client.nsd_update(user.get_token(), descriptor_id, descriptor_updated)
        if result['error'] == True:
            return __response_handler(request, result['data'], url=None,
                                      status=result['data']['status'] if 'status' in result['data'] else 500)
        else:
            parser = OsmParser()
            # print nsr_object
            if descriptor_type == 'nsd':
                result_graph = parser.nsd_to_graph(descriptor_updated)

        return __response_handler(request, result_graph, url=None, status=200)

    elif descriptor_type == 'vnfd':
        descriptor_result = client.vnfd_get(user.get_token(), descriptor_id)
        element_id = request.POST.get('id', '')
        util = OsmUtil()
        descriptor_updated = util.remove_node('vnfd', descriptor_result, element_type, element_id, request.POST.dict())
        result = client.vnfd_update(user.get_token(), descriptor_id, descriptor_updated)
        if result['error'] == True:
            return __response_handler(request, result['data'], url=None,
                                      status=result['data']['status'] if 'status' in result['data'] else 500)
        else:
            parser = OsmParser()
            # print nsr_object
            if descriptor_type == 'vnfd':
                result_graph = parser.vnfd_to_graph(descriptor_updated)

            return __response_handler(request, result_graph, url=None, status=200)

@login_required
def updateElement(request, descriptor_type=None, descriptor_id=None, element_type=None):
    user = osmutils.get_user(request)
    project_id = user.project_id
    client = Client()
    if descriptor_type == 'nsd':
        descriptor_result = client.nsd_get(user.get_token(), descriptor_id)
        util = OsmUtil()
        payload = request.POST.dict()
        if element_type == 'graph_params':
            descriptor_updated = util.update_graph_params('nsd', descriptor_result, json.loads(payload['update']))
        else:
            descriptor_updated = util.update_node('nsd', descriptor_result, element_type, json.loads(payload['old']), json.loads(payload['update']))
        result = client.nsd_update(user.get_token(), descriptor_id, descriptor_updated)
        if result['error'] == True:
            return __response_handler(request, result['data'], url=None,
                                      status=result['data']['status'] if 'status' in result['data'] else 500)
        else:
            parser = OsmParser()
            # print nsr_object
            if descriptor_type == 'nsd':
                result_graph = parser.nsd_to_graph(descriptor_updated)
    if descriptor_type == 'vnfd':
        descriptor_result = client.vnfd_get(user.get_token(), descriptor_id)
        util = OsmUtil()
        payload = request.POST.dict()
        if element_type == 'graph_params':
            descriptor_updated = util.update_graph_params('vnfd', descriptor_result, json.loads(payload['update']))
        else:
            descriptor_updated = util.update_node('vnfd', descriptor_result, element_type, json.loads(payload['old']), json.loads(payload['update']))
        result = client.vnfd_update(user.get_token(), descriptor_id, descriptor_updated)
        if result['error'] == True:
            return __response_handler(request, result['data'], url=None,
                                      status=result['data']['status'] if 'status' in result['data'] else 500)
        else:
            parser = OsmParser()
            if descriptor_type == 'vnfd':
                result_graph = parser.vnfd_to_graph(descriptor_updated)

        return __response_handler(request, result_graph, url=None, status=200)

@login_required
def new_descriptor(request, descriptor_type=None):
    user = osmutils.get_user(request)
    project_id = user.project_id
    page = 'descriptor_new.html'
    if request.method == 'GET':
        request_id = request.GET.get('id', '')

        return __response_handler(request,  {
            'project_id': project_id,
            'descriptor_type': descriptor_type,
            'descriptor_id': request_id,
        }, page)
    elif request.method == 'POST':
        data_type = request.POST.get('type')
        if data_type == "file":
            file_uploaded = request.FILES['file']

            try:
                client = Client()
                if descriptor_type == 'nsd':
                    result = client.nsd_onboard(user.get_token(), file_uploaded)
                elif descriptor_type == 'vnfd':
                    result = client.vnfd_onboard(user.get_token(), file_uploaded)
                else:
                    log.debug('Create descriptor: Unknown data type')
                    result = {'error': True, 'data': 'Create descriptor: Unknown data type'}

            except Exception as e:
                log.exception(e)
                result = {'error': True, 'data': str(e)}
        else:
            result = {'error': True, 'data': 'Create descriptor: Unknown data type'}

        if result['error']:
            return __response_handler(request, result['data'], url=None, status=result['data']['status'] if 'status' in result['data'] else 500)
        else:
            return __response_handler(request, {}, url=None, status=200)


@login_required
def edit_descriptor(request, descriptor_id=None, descriptor_type=None):
    user = osmutils.get_user(request)
    project_id = user.project_id
    if request.method == 'POST':
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
                result = client.nsd_update(user.get_token(), descriptor_id, new_data)
            elif descriptor_type == 'vnfd':
                if data_type == 'yaml':
                    new_data = yaml.load(request.POST.get('text'))
                elif data_type == 'json':
                    new_data = json.loads(request.POST.get('text'))
                result = client.vnfd_update(user.get_token(), descriptor_id, new_data)

            else:
                log.debug('Update descriptor: Unknown data type')
                result = {'error': True, 'data': 'Update descriptor: Unknown data type'}
        except Exception as e:
            log.exception(e)
            result = {'error': True, 'data': str(e)}
        if result['error'] == True:
            return __response_handler(request, result['data'], url=None, status=result['data']['status'] if 'status' in result['data'] else 500)

        else:
            return __response_handler(request, {}, url=None, status=200)

    elif request.method == 'GET':

        page = 'descriptor_view.html'
        try:
            client = Client()
            if descriptor_type == 'nsd':
                result = client.nsd_get(user.get_token(), descriptor_id)
            elif descriptor_type == 'vnfd':
                result = client.vnfd_get(user.get_token(), descriptor_id)
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
def get_package_files_list(request, descriptor_id, descriptor_type):
    user = osmutils.get_user(request)
    try:
        client = Client()
        if descriptor_type == 'nsd':
            artifacts_res = client.nsd_artifacts(user.get_token(), descriptor_id)
        elif descriptor_type == 'vnfd':
            artifacts_res = client.vnf_packages_artifacts(user.get_token(), descriptor_id)
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
def download_pkg(request, descriptor_id, descriptor_type):
    user = osmutils.get_user(request)
    file_name = "osm_export.tar.gz"
    tar_pkg = None
    try:
        client = Client()
        if descriptor_type == 'nsd':
            tar_pkg = client.get_nsd_pkg(user.get_token(), descriptor_id)
        elif descriptor_type == 'vnfd':
            tar_pkg = client.get_vnfd_pkg(user.get_token(), descriptor_id)

    except Exception as e:
        log.exception(e)

    response = HttpResponse(content_type="application/tgz")
    response["Content-Disposition"] = "attachment; filename="+ file_name
    response.write(tar_pkg.getvalue())
    return response

@login_required
def open_composer(request):
    user = osmutils.get_user(request)
    project_id = user.project_id
    descriptor_id = request.GET.get('id')
    descriptor_type = request.GET.get('type')
    result = {}
    client = Client()
    if descriptor_id:
        raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
        if 'application/json' not in raw_content_types:
            return __response_handler(request, {'type': descriptor_type}, 'composer.html')
        try:
            if descriptor_type == 'nsd':
                descriptor_result = client.nsd_get(user.get_token(), descriptor_id)
            elif descriptor_type == 'vnfd':
                descriptor_result = client.vnfd_get(user.get_token(), descriptor_id)

        except Exception as e:
            descriptor_result = {'error': True, 'data': str(e)}

        if isinstance(descriptor_result, dict) and 'error' in descriptor_result and descriptor_result['error']:
            return render(request, 'error.html')

        test = OsmParser()
        # print nsr_object
        if descriptor_type == 'nsd':
            result = test.nsd_to_graph(descriptor_result)
        elif descriptor_type == 'vnfd':
            result = test.vnfd_to_graph(descriptor_result)
        return __response_handler(request, result, 'composer.html')

    return __response_handler(request, result, 'composer.html')


def get_available_nodes(request):
    user = osmutils.get_user(request)
    params = request.GET.dict()
    client = Client()
    result = []
    try:
        if params['layer'] == 'nsd':
            descriptors = client.vnfd_list(user.get_token())
    except Exception as e:
        log.exception(e)
        descriptors = []
    if descriptors and descriptors['error'] is False:
        for desc in descriptors['data']:
            # print desc
            result.append({'_id': desc['_id'],'id': desc['id'], 'name': desc['short-name']})

    return __response_handler(request, {'descriptors': result})


@login_required
def custom_action(request, descriptor_id=None, descriptor_type=None, action_name=None):
    if request.method == 'GET':
        return globals()[action_name](request, descriptor_id, descriptor_type)


def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types or url is None:
        return HttpResponse(json.dumps(data_res), content_type="application/json", *args, **kwargs)
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)
