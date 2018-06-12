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
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from lib.osm.osmclient.client import Client
import uuid


class OsmUserManager(BaseUserManager):
    """Custom manager for OsmUser."""

    def _create_user(self, username, password, is_staff, is_superuser, **extra_fields):
        """Create and save a CustomUser with the given username and password. """
        now = timezone.now()

        if not username:
            raise ValueError('The given username must be set')

        is_active = extra_fields.pop("is_active", True)
        user = self.model(username=username, is_staff=is_staff, is_active=is_active,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    """Create and save an OsmUser with the given username and password."""
    def create_superuser(self, username, password, **extra_fields):
        return self._create_user(username, password, True, True, is_admin=True,
                                 **extra_fields)


class AbstractOsmUser(AbstractBaseUser, PermissionsMixin):
    """Abstract User with the same behaviour as Django's default User.


    Inherits from both the AbstractBaseUser and PermissionMixin.

    The following attributes are inherited from the superclasses:
        * password
        * last_login
        * is_superuser

    """
    username = models.CharField(_('username'), max_length=255, unique=True, db_index=True)
    current_project = models.CharField(_('project_id'), max_length=255)
    token_project = models.CharField(_('token'), max_length=36)
    is_admin = models.BooleanField(_('admin status'), default=False)
    is_basic_user = models.BooleanField(_('basic_user status'), default=False)

    objects = OsmUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('custom user')
        verbose_name_plural = _('custom users')
        abstract = True



class OsmUser(AbstractOsmUser):
    """
        Concrete class of AbstractCustomUser.

        Use this if you don't need to extend CustomUser.

        """

    class Meta(AbstractOsmUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def get_projects(self):
        client = Client()
        return []
