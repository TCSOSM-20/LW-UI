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

from django.conf.urls import url
from userhandler import views

urlpatterns = [
    url(r'^list$', views.list, name='list'),
    url(r'^create$', views.create, name='create'),
    url(r'^(?P<user_id>[0-9a-zA-Z]+)', views.update, name='update'),
    url(r'^(?P<user_id>[0-9a-zA-Z]+)/delete$', views.delete, name='delete')

]