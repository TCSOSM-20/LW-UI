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
from .models import OsmUser


class OsmBackend(object):

    def authenticate(self, **kwargs):
        '''
        kwargs will receive the python dict that may contain
        {username, password, project-id}  to authenticate
        '''
        if all(k in kwargs for k in ('username', 'password', 'project_id')):
            username = kwargs['username']
            password = kwargs['password']
            project_id = kwargs['project_id']

            print username
            print password
            print project_id

            try:

                return OsmUser.objects.get(username=username)
            except OsmUser.DoesNotExist:
                # Create a new user. There's no need to set a password
                # we will keep just some preferences
                user = OsmUser(username=username)
                user.save()
                return user

        return None

    def get_user(self, user_id):
        try:
            return OsmUser.objects.get(pk=user_id)
        except OsmUser.DoesNotExist:
            return None