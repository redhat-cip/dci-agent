#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Red Hat, Inc
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

from dci_agent.plugins import plugin
from dci_agent.ansible import runner


import os
import random
import string


class Mirror(plugin.Plugin):

    def __init__(self, conf):
        super(Mirror, self).__init__(conf)

    def run(self, state, data=None, context=None):
        """Sync remote repository to local mirror. """

        base_dir = self.conf.get('directory', '/srv/puddles')

        for component in data['components']:

            dest = '%s/%s' % (base_dir, component['data']['path'])
            if not os.path.exists(dest):
                os.makedirs(dest)

            repo = component['data']['repo_name']
            data_path = component['data']['path']

            playbook = """
- hosts: localhost
  vars:
    dci_status: %s
    dci_comment: 'Synchronizing repositories %s'
    dci_log_prefix: 'mirror'
  tasks:
    - name: Synchronize the puddles repository %s
      shell: rsync -av --hard-links \
    partner@rhos-mirror.distributed-ci.io:/srv/puddles/%s %s/../

    - name: Create yum repo for %s
      yum_repository:
        name: %s
        description: %s
        baseurl: file://%s
        enabled: 1
        gpgcheck: 0
        priority: 0
""" % (state, repo, repo, data_path, dest, repo, repo, repo, dest)

            for _ in range(10):
                tmp_str = random.choice(string.ascii_uppercase + string.digits)
                rand_string = ''.join(tmp_str)
            open('/tmp/%s.yml' % rand_string, 'w').write(playbook)

            l_runner = runner.Runner(playbook='/tmp/%s.yml' % rand_string,
                                     dci_context=context,
                                     verbosity=0)
            l_runner.run(job_id=context.last_job_id)
            os.remove('/tmp/%s.yml' % rand_string)
