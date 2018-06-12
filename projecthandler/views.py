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

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from lib.util import Util
from projecthandler.osm_model import OsmProject
from lib.osm.osmclient.client import Client




@login_required
def home(request):
    return render(request, 'home.html', {})


@login_required
def create_new_project(request):
    return render(request, 'home.html', {})


@login_required
def user_projects(request):
    csrf_token_value = get_token(request)
    user = request.user
    projects = user.get_projects()

    return render(request, 'projectlist.html', {
        'projects': list(projects),
        'csrf_token': csrf_token_value
    })


@login_required
def open_project(request, project_id=None):
    try:
        user = request.user
        client = Client()
        nsd = client.nsd_list()
        vnfd = client.vnfd_list()
        ns = client.ns_list()
        vnf = client.vnf_list()
        project_overview = {
            'owner': user.username,
            'name': project_id,
            'updated_date': '-',
            'created_date': '-',
            'info': '-',
            'type': 'osm',
            'nsd': len(nsd) if nsd else 0,
            'vnfd': len(vnfd) if vnfd else 0,
            'ns': len(ns) if ns else 0,
            'vnf': len(vnf) if vnf else 0,
        }
        return render(request, 'osm/osm_project_details.html',
                      {'project_overview': project_overview, 'project_id': project_id})

    except Exception as e:
        print e
        return render(request, 'error.html', {'error_msg': 'Error open project! Please retry.'})


@login_required
def delete_project(request, project_id=None):
    if request.method == 'POST':

        try:
            ##TODO delete project
            return redirect('projects:projects_list')
        except Exception as e:
            print e
            return render(request, 'error.html', {'error_msg': 'Error deleting Project.'})

    elif request.method == 'GET':
        try:
            return render(request, 'osm/osm_project_delete.html',
                          {'project_id': project_id, 'project_name': project_id})

        except Exception as e:
            print e
            return render(request, 'error.html', {'error_msg': 'Project not found.'})


@login_required
def show_descriptors(request, project_id=None, descriptor_type=None):
    csrf_token_value = get_token(request)

    client = Client()
    try:
        if descriptor_type == 'nsd':
            descriptors = client.nsd_list()

        elif descriptor_type == 'vnfd':
            descriptors = client.vnfd_list()
    except Exception as e:
        descriptors = []

    url = 'osm/osm_project_descriptors.html'
    return __response_handler(request, {
        'descriptors': descriptors,
        'project_id': project_id,
        'project_type': 'osm',
        "csrf_token_value": csrf_token_value,
        'descriptor_type': descriptor_type
    },url)


@login_required
def delete_descriptor(request, project_id=None, descriptor_type=None, descriptor_id=None):
    csrf_token_value = get_token(request)

    try:
        client = Client()
        if descriptor_type == 'nsd':
            result = client.nsd_delete(descriptor_id)
        elif descriptor_type == 'vnfd':
            result = client.vnfd_delete(descriptor_id)

        else:
            return False

    except Exception as e:
        result = False
    project_overview = OsmProject.get_overview_data()
    prj_token = project_overview['type']
    page = prj_token + '/' + prj_token + '_project_descriptors.html'

    return render(request, page, {
        'descriptors': OsmProject.get_descriptors(descriptor_type),
        'project_id': project_id,
        'project_overview_data': project_overview,
        "csrf_token_value": csrf_token_value,
        'descriptor_type': descriptor_type,
        #'alert_message': {
        #    'success': result,
        #    'message': "Delete succeeded!" if result else 'Error in delete'}
    })


@login_required
def new_descriptor(request, project_id=None, descriptor_type=None):

    project_overview = OsmProject.get_overview_data()
    prj_token = project_overview['type']
    page = prj_token + '/descriptor/descriptor_new.html'
    if request.method == 'GET':
        request_id = request.GET.get('id', '')
        return render(request, page, {
            'project_id': project_id,
            'descriptor_type': descriptor_type,
            'descriptor_id': request_id,
            'project_overview_data': project_overview
        })
    elif request.method == 'POST':
        csrf_token_value = get_token(request)
        data_type = request.POST.get('type')
        print "TYPE", data_type
        if data_type == "file":
            file_uploaded = request.FILES['file']
            text = file_uploaded.read()
            data_type = file_uploaded.name.split(".")[-1]
            desc_name = file_uploaded.name.split(".")[0]
            result = OsmProject.create_descriptor(desc_name, descriptor_type, text, data_type, file_uploaded)
        else:
            text = request.POST.get('text')
            desc_name = request.POST.get('id')
            result = OsmProject.create_descriptor(desc_name, descriptor_type, text, data_type)


        response_data = {
            'project_id': project_id,
            'descriptor_type': descriptor_type,
            'project_overview_data':OsmProject.get_overview_data(),
            'descriptor_id': result,
            'alert_message': {
                'success': True if result != False else False,
                'message': "Descriptor created" if result else 'Error in creation'}
        }
        status_code = 200 if result != False else 500
        response = HttpResponse(json.dumps(response_data), content_type="application/json", status=status_code)
        response["Access-Control-Allow-Origin"] = "*"
        return response


@login_required
def edit_descriptor(request, project_id=None, descriptor_id=None, descriptor_type=None):
    if request.method == 'POST':
        print "edit_descriptor"
        result = OsmProject.edit_descriptor(descriptor_type, descriptor_id, request.POST.get('text'),
                                             request.POST.get('type'))
        response_data = {
            'project_id': project_id,
            'descriptor_type': descriptor_type,
            #'project_overview_data': projects[0].get_overview_data(),
            'alert_message': {
                'success':  True if result else False,
                'message': "Descriptor modified." if result else 'Error during descriptor editing.'}
        }
        status_code = 200 if result else 500
        response = HttpResponse(json.dumps(response_data), content_type="application/json", status=status_code)
        response["Access-Control-Allow-Origin"] = "*"
        return response

    elif request.method == 'GET':
        csrf_token_value = get_token(request)
        project_overview = OsmProject.get_overview_data()
        print project_overview
        prj_token = project_overview['type']
        page = prj_token + '/descriptor/descriptor_view.html'

        descriptor = OsmProject.get_descriptor(descriptor_id, descriptor_type)

        descriptor_string_json = json.dumps(descriptor)
        descriptor_string_yaml = Util.json2yaml(descriptor)
        # print descriptor
        return render(request, page, {
            'project_id': project_id,
            'descriptor_id': descriptor_id,
            'project_overview_data': OsmProject.get_overview_data(),
            'descriptor_type': descriptor_type,
            'descriptor_strings': {'descriptor_string_yaml': descriptor_string_yaml,
                                   'descriptor_string_json': descriptor_string_json}})


# OSM specific method #
def get_package_files_list(request, project_id, project, descriptor_id, descriptor_type):
    files_list = []
    try:
        files_list = project.get_package_files_list(descriptor_type, descriptor_id)
        result = {'files': files_list}
    except Exception as e:
        print e
        url = 'error.html'
        result = {'error_msg': 'Unknown error.'}
    return __response_handler(request, result)


def download_pkg(request, project_id, descriptor_id, descriptor_type):
    tar_pkg = OsmProject.download_pkg(descriptor_id, descriptor_type)

    response = HttpResponse(content_type="application/tgz")
    response["Content-Disposition"] = "attachment; filename=osm_export.tar.gz"
    response.write(tar_pkg.getvalue())
    return response


def create_ns(request, project_id, project, descriptor_id, descriptor_type):
    files_list = []
    try:
        ns_data={
          "nsName": request.POST.get('nsName', 'WithoutName'),
          "nsDescription": request.POST.get('nsDescription', ''),
          "nsdId": request.POST.get('nsdId', ''),
          "vimAccountId": request.POST.get('vimAccountId', ''),
          "ssh-authorized-key": [
            {
              request.POST.get('key-pair-ref', ''): request.POST.get('keyValue', '')
            }
          ]
        }
        #result = project.create_ns(descriptor_type, descriptor_id, ns_data)

    except Exception as e:
        print e
        url = 'error.html'
        result = {'error_msg': 'Unknown error.'}
    return __response_handler(request, result)

# end OSM specific method #

@login_required
def custom_action(request, project_id=None, descriptor_id=None, descriptor_type=None, action_name=None):
    if request.method == 'GET':
        print "Custom action: " + action_name
        return globals()[action_name](request, project_id, descriptor_id, descriptor_type)


def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types:
        return JsonResponse(data_res)
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)
