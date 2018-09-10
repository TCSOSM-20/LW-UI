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
#from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
import yaml
import json
import logging
from lib.osm.osmclient.clientv2 import Client
import authosm.utils as osmutils
from sf_t3d.decorators import login_required

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('instancehandler/view.py')


@login_required
def list(request, type=None):

    user = osmutils.get_user(request)
    project_id = user.project_id
    client = Client()
    result = {'type': type, 'project_id': project_id}
    if "OSM_ERROR" in request.session:
        result['alert_error'] = request.session["OSM_ERROR"]
        del request.session["OSM_ERROR"]
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' not in raw_content_types:
        return __response_handler(request, result, 'instance_list.html')
    instance_list = None
    if type == 'ns':
        instance_list = client.ns_list(user.get_token())
    elif type == 'vnf':
        instance_list = client.vnf_list(user.get_token())

    result['instances'] = instance_list['data'] if instance_list and instance_list['error'] is False else []

    return __response_handler(request, result, 'instance_list.html')


@login_required
def create(request):
    result = {}
    try:

        ns_data = {
            "nsName": request.POST.get('nsName', 'WithoutName'),
            "nsDescription": request.POST.get('nsDescription', ''),
            "nsdId": request.POST.get('nsdId', ''),
            "vimAccountId": request.POST.get('vimAccountId', ''),
        }
        if 'ssh_key' in request.POST and request.POST.get('ssh_key') != '':
            ns_data["ssh-authorized-key"] = [request.POST.get('ssh_key')]

        if 'config' in request.POST:
            ns_config = yaml.load(request.POST.get('config'))
            if isinstance(ns_config, dict):
                if "vim-network-name" in ns_config:
                    ns_config["vld"] = ns_config.pop("vim-network-name")
                if "vld" in ns_config:
                    print ns_config
                    for vld in ns_config["vld"]:
                        if vld.get("vim-network-name"):
                            if isinstance(vld["vim-network-name"], dict):
                                vim_network_name_dict = {}
                                for vim_account, vim_net in vld["vim-network-name"].items():
                                    vim_network_name_dict[ns_data["vimAccountId"]] = vim_net
                                vld["vim-network-name"] = vim_network_name_dict
                    ns_data["vld"] = ns_config["vld"]
                if "vnf" in ns_config:
                    for vnf in ns_config["vnf"]:
                        if vnf.get("vim_account"):
                            vnf["vimAccountId"] = ns_data["vimAccountId"]

                    ns_data["vnf"] = ns_config["vnf"]
    except Exception as e:
        request.session["OSM_ERROR"] = "Error creating the NS; Invalid parameters provided."
        return __response_handler(request, {}, 'instances:list', to_redirect=True, type='ns', )

    print ns_data
    user = osmutils.get_user(request)
    client = Client()
    result = client.ns_create(user.get_token(), ns_data)
    return __response_handler(request, result, 'instances:list', to_redirect=True, type='ns',)


@login_required
def ns_operations(request, instance_id=None, type=None):
    user = osmutils.get_user(request)
    project_id = user.project_id

    result = {'type': 'ns', 'project_id': project_id, 'instance_id': instance_id}
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' not in raw_content_types:
        return __response_handler(request, result, 'instance_operations_list.html')
    client = Client()
    op_list = client.ns_op_list(user.get_token(), instance_id)
    result['operations'] = op_list['data'] if op_list and op_list['error'] is False else []

    return __response_handler(request, result, 'instance_operations_list.html')

@login_required
def ns_operation(request, op_id, instance_id=None, type=None):
    user = osmutils.get_user(request)
    client = Client()
    result = client.ns_op(user.get_token(), op_id)
    return __response_handler(request, result['data'])


@login_required
def action(request, instance_id=None, type=None):
    user = osmutils.get_user(request)
    client = Client()
    # result = client.ns_action(instance_id, action_payload)
    primitive_param_keys = request.POST.getlist('primitive_params_name')
    primitive_param_value = request.POST.getlist('primitive_params_value')
    action_payload = {
        "vnf_member_index": request.POST.get('vnf_member_index'),
        "primitive": request.POST.get('primitive'),
        "primitive_params": {k: v for k, v in zip(primitive_param_keys, primitive_param_value) if len(k) > 0}
    }

    result = client.ns_action(user.get_token(), instance_id, action_payload)
    print result
    if result['error']:
        return __response_handler(request, result['data'], url=None,
                                  status=result['data']['status'] if 'status' in result['data'] else 500)

    else:
        return __response_handler(request, {}, url=None, status=200)


@login_required
def delete(request, instance_id=None, type=None):
    force = bool(request.GET.get('force', False))
    result = {}
    user = osmutils.get_user(request)
    client = Client()
    result = client.ns_delete(user.get_token(), instance_id, force)
    print result
    return __response_handler(request, result, 'instances:list', to_redirect=True, type='ns')


def show_topology(request, instance_id=None, type=None):
    user = osmutils.get_user(request)
    project_id = user.project_id
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types:
        result = {'vertices': [
            {"info": {"type": "vnf", "property": {"custom_label": ""},
                      "group": []}, "id": "ping"},
            {"info": {"type": "vnf", "property": {"custom_label": ""},
                      "group": []}, "id": "pong"},
            {"info": {"type": "vdu", "property": {"custom_label": ""},
                      "group": ['pong']}, "id": "pong/ubuntu"},
            {"info": {"type": "vdu", "property": {"custom_label": ""},
                      "group": ['ping']}, "id": "ping/ubuntu"},
            {"info": {"type": "cp", "property": {"custom_label": ""},
                      "group": ['ping']}, "id": "ping/cp0"},
            {"info": {"type": "cp", "property": {"custom_label": ""},
                      "group": ['ping']}, "id": "ping/cp1"},
            {"info": {"type": "cp", "property": {"custom_label": ""},
                      "group": ['pong']}, "id": "pong/cp0"},
            {"info": {"type": "cp", "property": {"custom_label": ""},
                      "group": ['pong']}, "id": "pong/cp1"},
            {"info": {"type": "ns_vl", "property": {"custom_label": ""},
                      "group": []}, "id": "mgmt_vl"},
        ],
            'edges': [
                # {"source": "ping", "group": [], "target": "ping/cp0", "view": "Data"},
                {"source": "pong/ubuntu", "group": ['pong'], "target": "pong/cp0", "view": "vnf"},
                {"source": "ping/ubuntu", "group": ['ping'], "target": "ping/cp0", "view": "vnf"},
                {"source": "pong/ubuntu", "group": ['pong'], "target": "pong/cp1", "view": "vnf"},
                {"source": "ping/ubuntu", "group": ['ping'], "target": "ping/cp1", "view": "vnf"},
                {"source": "pong", "group": [], "target": "mgmt_vl", "view": "ns"},
                {"source": "ping", "group": [], "target": "mgmt_vl", "view": "ns"},
            ], 'graph_parameters': [],
            'model': {
                "layer": {

                    "ns": {
                        "nodes": {
                            "vnf": {
                                "addable": {
                                    "callback": "addNode"
                                },
                                "removable": {
                                    "callback": "removeNode"
                                },
                                "expands": "vnf"
                            },
                            "ns_vl": {
                                "addable": {
                                    "callback": "addNode"
                                },
                                "removable": {
                                    "callback": "removeNode"
                                }
                            },

                        },
                        "allowed_edges": {
                            "ns_vl": {
                                "destination": {
                                    "vnf": {
                                        "callback": "addLink",
                                        "direct_edge": False,
                                        "removable": {
                                            "callback": "removeLink"
                                        }
                                    }
                                }
                            },
                            "vnf": {
                                "destination": {
                                    "ns_vl": {
                                        "callback": "addLink",
                                        "direct_edge": False,
                                        "removable": {
                                            "callback": "removeLink"
                                        }
                                    },

                                }
                            }

                        }
                    },
                    "vnf": {
                        "nodes": {
                            "vdu": {
                                "addable": {
                                    "callback": "addNode"
                                },
                                "removable": {
                                    "callback": "removeNode"
                                }
                            },
                            "cp": {
                                "addable": {
                                    "callback": "addNode"
                                },
                                "removable": {
                                    "callback": "removeNode"
                                }
                            },

                        },
                        "allowed_edges": {
                            "vdu": {
                                "destination": {
                                    "cp": {
                                        "callback": "addLink",
                                        "direct_edge": False,
                                        "removable": {
                                            "callback": "removeLink"
                                        }
                                    }
                                }
                            },
                            "cp": {
                                "destination": {
                                    "vdu": {
                                        "callback": "addLink",
                                        "direct_edge": False,
                                        "removable": {
                                            "callback": "removeLink"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "name": "OSM",
                    "version": 1,
                    "nodes": {
                        "vnf": {
                            "label": "vnf"
                        },
                        "ns_vl": {
                            "label": "vl"
                        },
                        "cp": {
                            "label": "cp"
                        },
                        "vdu": {
                            "label": "vdu"
                        }
                    },
                    "description": "osm"
                }
            }}
        return __response_handler(request, result)
    else:
        result = {'type': type, 'project_id': project_id, 'instance_id': instance_id}
        return __response_handler(request, result, 'instance_topology_view.html')


@login_required
def show(request, instance_id=None, type=None):
    # result = {}
    user = osmutils.get_user(request)
    project_id = user.project_id
    client = Client()
    if type == 'ns':
        result = client.ns_get(user.get_token(), instance_id)
    elif type == 'vnf':
        result = client.vnf_get(user.get_token(), instance_id)
    print result
    return __response_handler(request, result)


@login_required
def export_metric(request, instance_id=None, type=None):
    metric_data = request.POST.dict()
    user = osmutils.get_user(request)
    project_id = user.project_id
    client = Client()
    keys = ["collection_period",
            "vnf_member_index",
            "metric_name",
            "correlation_id",
            "vdu_name",
            "collection_unit"]
    metric_data = dict(filter(lambda i: i[0] in keys and len(i[1]) > 0, metric_data.items()))

    result = client.ns_metric_export(user.get_token(), instance_id, metric_data)

    if result['error']:
        print result
        return __response_handler(request, result['data'], url=None,
                                  status=result['data']['status'] if 'status' in result['data'] else 500)
    else:
        return __response_handler(request, {}, url=None, status=200)


@login_required
def create_alarm(request, instance_id=None, type=None):
    metric_data = request.POST.dict()
    print metric_data
    user = osmutils.get_user(request)
    project_id = user.project_id
    client = Client()

    keys = ["threshold_value",
            "vnf_member_index",
            "metric_name",
            "vdu_name",
            "alarm_name",
            "correlation_id",
            "statistic",
            "operation",
            "severity"]
    metric_data = dict(filter(lambda i: i[0] in keys and len(i[1]) > 0, metric_data.items()))

    result = client.ns_alarm_create(user.get_token(), instance_id, metric_data)
    if result['error']:
        print result
        return __response_handler(request, result['data'], url=None,
                                  status=result['data']['status'] if 'status' in result['data'] else 500)
    else:
        return __response_handler(request, {}, url=None, status=200)


def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types or url is None:
        return HttpResponse(json.dumps(data_res), content_type="application/json")
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)
