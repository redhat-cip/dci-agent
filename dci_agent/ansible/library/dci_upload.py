#!/usr/bin/env python
#  -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2017 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from ansible.module_utils.basic import *  # noqa
from dciclient.v1.api import context as dci_context
from dciclient.v1.api import file as dci_file

import mimetypes
import os


DOCUMENTATION = '''
---
module: dci_upload
short_description: upload logs from local directory to the dci control server
'''

EXAMPLES = '''
- name: upload local logs
  dci_upload:
    src_dir: <path-logs-directory>
    dci_login: <dci login>
    dci_password: <dci password>
    dci_cs_url: <dci cs url>
    dci_status: <dci status>
    job_id: <job id>
'''


def upload(context, dci_status, job_id, src_dir=None, file_path=None):
    """This function upload logs to dci control server from local logs
    directory.
    """
    def upload_directory():
        status_dir = '%s/%s' % (src_dir, dci_status)
        jobstate_id = open('%s/jobstate_id' % status_dir).read()
        logs_files = os.listdir(status_dir)
        # sort the file by date in order to upload the files in order
        logs_files_paths = [os.path.join(status_dir, f) for f in logs_files]
        logs_files_paths.sort(key=lambda x: os.path.getmtime(x))
        for log_file_path in logs_files_paths:
            name = os.path.basename(log_file_path)
            if not log_file_path.endswith('jobstate_id'):
                # junit file a associated directly to the job
                if log_file_path.endswith('.junit'):
                    dci_file.create_with_stream(context, name=name,
                                                file_path=log_file_path,
                                                mime='application/junit',
                                                job_id=job_id)
                else:
                    dci_file.create_with_stream(context, name=name,
                                                file_path=log_file_path,
                                                jobstate_id=jobstate_id)
                os.remove(log_file_path)

        return {'uploaded': logs_files}

    def upload_file():
        if not os.path.exists(file_path):
            return {'failed': True,
                    'msg': 'file %s does not exist' % file_path}
        mimetype, _ = mimetypes.guess_type(file_path)
        mimetype = mimetype or 'text/plain'
        name = os.path.basename(file_path)
        dci_file.create_with_stream(context, name=name,
                                    file_path=file_path,
                                    mime=mimetype,
                                    job_id=job_id)
        return {'uploaded': file_path}

    if src_dir is not None:
        return upload_directory()
    else:
        return upload_file()


def main():

    fields = {
        "src_dir": {"required": False, "type": "str"},
        "file": {"required": False, "type": "str"},
        "dci_status": {"required": True, "type": "str"},
        "dci_login": {"required": True, "type": "str"},
        "dci_password": {"required": True, "type": "str"},
        "dci_cs_url": {"required": True, "type": "str"},
        "job_id": {"required": True, "type": "str"}
    }

    module = AnsibleModule(argument_spec=fields)

    src_dir = module.params.get('src_dir')
    file = module.params.get('file')
    dci_status = module.params['dci_status']
    dci_login = module.params['dci_login']
    dci_password = module.params['dci_password']
    dci_cs_url = module.params['dci_cs_url']
    job_id = module.params['job_id']

    _dci_context = dci_context.build_dci_context(
        dci_cs_url,
        dci_login,
        dci_password
    )

    response = upload(_dci_context, dci_status, job_id, src_dir, file)
    module.exit_json(changed=True, meta=response)


if __name__ == '__main__':
    main()
