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
        self._host = os.getenv('OSM_SERVER', "localhost")
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

    def nsd_list(self, token):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}

        _url = "{0}/nsd/v1/ns_descriptors_content".format(self._base_path)
        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)

        return result

    def vnfd_list(self, token):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}

        _url = "{0}/vnfpkgm/v1/vnf_packages_content".format(self._base_path)
        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)

        return result

    def ns_list(self, token):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}
        _url = "{0}/nslcm/v1/ns_instances_content".format(self._base_path)
        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)

        return result

    def vnf_list(self, token):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}
        _url = "{0}/nslcm/v1/vnfrs".format(self._base_path)
        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)

        return result

    def nsd_delete(self, token, id):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}

        _url = "{0}/nsd/v1/ns_descriptors_content/{1}".format(self._base_path, id)
        try:
            r = requests.delete(_url, params=None, verify=False,headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)
        return result

    def vnfd_delete(self, token, id):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}

        _url = "{0}/vnfpkgm/v1/vnf_packages_content/{1}".format(self._base_path, id)
        try:
            r = requests.delete(_url, params=None, verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)
        return result

    def nsd_onboard(self, token, package):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/gzip", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}
        with open('/tmp/'+package.name, 'wb+') as destination:
            for chunk in package.chunks():
                destination.write(chunk)
        headers['Content-File-MD5'] = self.md5(open('/tmp/'+package.name, 'rb'))
        _url = "{0}/nsd/v1/ns_descriptors_content/".format(self._base_path)
        try:
            r = requests.post(_url, data=open('/tmp/'+package.name, 'rb'), verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)
        return result

    def vnfd_onboard(self, token, package):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/gzip", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}
        with open('/tmp/'+package.name, 'wb+') as destination:
            for chunk in package.chunks():
                destination.write(chunk)
        headers['Content-File-MD5'] = self.md5(open('/tmp/'+package.name, 'rb'))
        _url = "{0}/vnfpkgm/v1/vnf_packages_content".format(self._base_path)
        try:
            r = requests.post(_url, data=open('/tmp/'+package.name, 'rb'), verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)
        return result

    def nsd_update(self, token, id, data):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/gzip", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}

        # get the package onboarded
        tar_pkg = self.get_nsd_pkg(token, id)
        tarf = tarfile.open(fileobj=tar_pkg)

        tarf = self._descriptor_update(tarf, data)
        headers['Content-File-MD5'] = self.md5(open('/tmp/' + tarf.getnames()[0] + ".tar.gz", 'rb'))

        _url = "{0}/nsd/v1/ns_descriptors/{1}/nsd_content".format(self._base_path, id)

        try:
            r = requests.put(_url, data=open('/tmp/' + tarf.getnames()[0] + ".tar.gz", 'rb'), verify=False,
                             headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        return result

    def vnfd_update(self, token, id, data):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/gzip", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}

        # get the package onboarded
        tar_pkg = self.get_vnfd_pkg(token, id)
        tarf = tarfile.open(fileobj=tar_pkg)

        tarf = self._descriptor_update(tarf, data)
        headers['Content-File-MD5'] = self.md5(open('/tmp/' + tarf.getnames()[0] + ".tar.gz", 'rb'))

        _url = "{0}/vnfpkgm/v1/vnf_packages/{1}/package_content".format(self._base_path, id)

        try:
            r = requests.put(_url, data=open('/tmp/' + tarf.getnames()[0] + ".tar.gz", 'rb'), verify=False,
                             headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        return result

    def get_nsd_pkg(self, token, id):
        result = {'error': True, 'data': ''}
        headers = { "accept": "application/zip",
                   'Authorization': 'Bearer {}'.format(token['id'])}

        _url = "{0}/nsd/v1/ns_descriptors/{1}/nsd_content".format(self._base_path, id)
        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
            tarf = StringIO.StringIO(r.content)
            return tarf
        return result

    def get_vnfd_pkg(self, token, id):
        result = {'error': True, 'data': ''}
        headers = {"accept": "application/zip",
                   'Authorization': 'Bearer {}'.format(token['id'])}
        _url = "{0}/vnfpkgm/v1/vnf_packages/{1}/package_content".format(self._base_path, id)
        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
            print r.status_code
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
            tarf = StringIO.StringIO(r.content)
            return tarf
        return result

    def _descriptor_update(self, tarf, data):
        print tarf.getnames()
        # extract the package on a tmp directory
        tarf.extractall('/tmp')

        for name in tarf.getnames():
            if name.endswith(".yaml") or name.endswith(".yml"):
                with open('/tmp/' + name, 'w') as outfile:
                    yaml.safe_dump(data, outfile, default_flow_style=False)
                break

        tarf_temp = tarfile.open('/tmp/' + tarf.getnames()[0] + ".tar.gz", "w:gz")
        # tarf_temp = tarfile.open("pippo.tar.gz", "w:gz")
        print tarf_temp.getnames()
        # tarf_temp.add('/tmp/'+tarf.getnames()[0])
        for tarinfo in tarf:
            # if tarinfo.name.startswith(tarf.getnames()[0]):
            #    new_name = tarinfo.name[len(tarf.getnames()[0]):]
            tarf_temp.add('/tmp/' + tarinfo.name, tarinfo.name, recursive=False)
        print tarf_temp.getnames()
        tarf_temp.close()
        return tarf

    def nsd_get(self, token, id):
        result = {'error': True, 'data': ''}
        headers = {'Content-Type': 'application/yaml',
                   'Authorization': 'Bearer {}'.format(token['id'])}
        _url = "{0}/nsd/v1/ns_descriptors/{1}/nsd".format(self._base_path, id)
        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
            return yaml.load(r.text)
        else:
            try:
                result['data'] = r.json()
            except Exception as e:
                result['data'] = {}
        return result

    def vnfd_get(self, token, id):
        result = {'error': True, 'data': ''}
        headers = {'Content-Type': 'application/yaml',
                   'Authorization': 'Bearer {}'.format(token['id'])}
        _url = "{0}/vnfpkgm/v1/vnf_packages/{1}/vnfd".format(self._base_path, id)
        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
            return yaml.load(r.text)
        else:
            try:
                result['data'] = r.json()
            except Exception as e:
                result['data'] = {}
        return result

    def nsd_artifacts(self, token, id):
        result = {'error': True, 'data': ''}
        headers = {'Content-Type': 'application/yaml', 'accept': 'text/plain',
                   'Authorization': 'Bearer {}'.format(token['id'])}
        _url = "{0}/nsd/v1/ns_descriptors/{1}/artifacts".format(self._base_path, id)
        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
            result['data'] = r.text
        else:
            try:
                result['data'] = r.json()
            except Exception as e:
                result['data'] = {}

        return result

    def vnf_packages_artifacts(self, token, id):
        result = {'error': True, 'data': ''}
        headers = {'Content-Type': 'application/yaml', 'accept': 'text/plain',
                   'Authorization': 'Bearer {}'.format(token['id'])}
        _url = "{0}/vnfpkgm/v1/vnf_packages/{1}/artifacts".format(self._base_path, id)
        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
            result['data'] = r.text
        else:
            try:
                result['data'] = r.json()
            except Exception as e:
                result['data'] = {}

        return result

    def ns_create(self, token, ns_data):
        token = self.get_token()
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}

        _url = "{0}/nslcm/v1/ns_instances_content".format(self._base_path)

        try:
            r = requests.post(_url, json=ns_data, verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)
        return result

    def ns_op_list(self, token, id):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}
        _url = "{0}/nslcm/v1/ns_lcm_op_occs/?nsInstanceId={1}".format(self._base_path, id)

        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)

        return result

    def ns_op(self, token, id):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}
        _url = "{0}/nslcm/v1/ns_lcm_op_occs/{1}".format(self._base_path, id)

        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)

        return result

    def ns_action(self, token, id, action_payload):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}

        _url = "{0}/nslcm/v1/ns_instances/{1}/action".format(self._base_path, id)

        try:
            r = requests.post(_url, json=action_payload, verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        print r.status_code
        if r.status_code == requests.codes.created:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)
        return result

    def ns_delete(self, token, id, force=None):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}
        query_path = ''
        if force:
            query_path = '?FORCE=true'
        _url = "{0}/nslcm/v1/ns_instances_content/{1}{2}".format(self._base_path, id, query_path)
        try:
            r = requests.delete(_url, params=None, verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)
        return result

    def ns_get(self, token, id):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}
        _url = "{0}/nslcm/v1/ns_instances_content/{1}".format(self._base_path, id)

        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)
        return result

    def vnf_get(self, token, id):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}
        _url = "{0}/nslcm/v1/vnfrs/{1}".format(self._base_path, id)

        try:
            r = requests.get(_url, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        result['data'] = Util.json_loads_byteified(r.text)
        return result

    def ns_alarm_create(self, token, id, alarm_payload):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}
        _url = "{0}/test/message/alarm_request".format(self._base_path)
        try:
            r = requests.post(_url, json=alarm_payload, verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        print r.status_code
        if r.status_code == requests.codes.ok:
            result['error'] = False
        #result['data'] = Util.json_loads_byteified(r.text)
        result['data'] = r.text
        return result

    def ns_metric_export(self, token, id, metric_payload):
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json",
                   'Authorization': 'Bearer {}'.format(token['id'])}
        _url = "{0}/test/message/metric_request".format(self._base_path)
        try:
            r = requests.post(_url, json=metric_payload, verify=False, headers=headers)
        except Exception as e:
            log.exception(e)
            result['data'] = str(e)
            return result
        print r.status_code
        if r.status_code == requests.codes.ok:
            result['error'] = False
        #result['data'] = Util.json_loads_byteified(r.text)
        result['data'] = r.text
        return result

    @staticmethod
    def md5(f):
        hash_md5 = hashlib.md5()
        for chunk in iter(lambda: f.read(1024), b""):
            hash_md5.update(chunk)
        return hash_md5.hexdigest()
