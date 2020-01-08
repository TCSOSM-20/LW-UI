# Copyright 2019 EveryUP 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM ubuntu:16.04

WORKDIR /usr/share/osm-lightui
COPY . /usr/share/osm-lightui

RUN apt-get update && apt-get install -y npm git python-pip nginx supervisor curl software-properties-common libmysqlclient-dev mysql-client
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN npm install
RUN mv node_modules ./static
RUN pip install -r requirements.txt
RUN pip install uwsgi

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY nginx-app.conf /etc/nginx/sites-available/default
COPY supervisor-app.conf /etc/supervisor/conf.d/

# delete the copy of the database inside the container (if exists)
RUN rm -f db.sqlite3

ENV DJANGO_ENV=prod
ENV OSM_SERVER=nbi
# ENV OSMUI_SQL_DATABASE_URI=mysql://root:secret@mysql:3306/lwui
RUN python manage.py collectstatic --noinput

EXPOSE 80

CMD ["/usr/share/osm-lightui/entrypoint.sh"]