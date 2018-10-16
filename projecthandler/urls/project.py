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

from django.conf.urls import url, include
from projecthandler import views

urlpatterns = [
    url(r'^$', views.open_project, name='open_project'),
    url(r'^list/', views.user_projects, name='projects_list'),
    url(r'^new/', views.create_new_project, name='new_project'),
    url(r'^(?P<project_id>[\w ]+)/delete$', views.delete_project, name='delete_project'),
    url(r'^(?P<project_id>[\w ]+)/switch', views.switch_project, name='switch_project'),
    url(r'^(?P<project_id>[\w ]+)/edit', views.edit_project, name='edit_project'),
    url(r'^descriptors/(?P<descriptor_type>\w+)/list$', views.show_descriptors, name='list_descriptors'),
    url(r'^descriptors/(?P<descriptor_type>\w+)/(?P<descriptor_id>[-\w]+)(/$)',
        views.edit_descriptor, name='edit_descriptor'),
    url(r'^descriptors/(?P<descriptor_type>\w+)/(?P<descriptor_id>[-\w]+)/delete$',
        views.delete_descriptor,
        name='delete_descriptor'),
    url(r'^descriptors/(?P<descriptor_type>\w+)/(?P<descriptor_id>[-\w]+)/clone',
        views.clone_descriptor,
        name='clone_descriptor'),
    url(r'^descriptors/(?P<descriptor_type>\w+)/(?P<descriptor_id>[-\w]+)/action/(?P<action_name>[-\w]+)',
        views.custom_action,
        name='custom_action'),
    url(r'^descriptors/(?P<descriptor_type>\w+)/new$', views.new_descriptor,
        name='new_descriptor'),
    url(r'^composer$', views.open_composer, name='open_composer'),
    url(r'^availablenodes', views.get_available_nodes, name='get_available_nodes'),


]