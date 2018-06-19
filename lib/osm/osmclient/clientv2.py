import requests
import logging
import json
import tarfile
import yaml
import pyaml
import StringIO
from lib.util import Util
import hashlib
import os

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('helper.py')


class Client(object):
    def __init__(self):
        self._token_endpoint = 'admin/v1/tokens'
        self._user_endpoint = 'admin/v1/users'
        self._host = os.getenv('OSM_SERVER', "192.168.1.73")
        self._so_port = 9999
        self._base_path = "https://{0}:{1}/osm".format(self._host, self._so_port)

    def auth(self, args):
        result = {'error': True, 'data': ''}
        token_url = "{0}/{1}".format(self._base_path, self._token_endpoint)
        headers = {"Content-Type": "application/yaml", "accept": "application/json"}
        try:
            r = requests.post(token_url, json=args, verify=False, headers=headers)
        except Exception as e:
            print "saltata"
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = Util.json_loads_byteified(r.text)

        return result

