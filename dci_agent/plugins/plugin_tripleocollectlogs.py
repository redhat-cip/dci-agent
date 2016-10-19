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

"""
Plugin to collect output from tripleo-collect-logs.

  :param string undercloud_ip:
"""

from dci_agent.plugins import plugin


PARAMS = ['undercloud_ip']


class Tripleocollectlogs(plugin.Plugin):

    def __init__(self, conf):
        super(Tripleocollectlogs, self).__init__(conf)

    def run(self, state, data=None, context=None, auth=None):
        """Run the tripleo-collect-logs role on the specified hosts."""

        self.fill_configuration(state, data, PARAMS)

        host = self.conf['undercloud_ip']
        module_url = ('https://api.github.com/repos/redhat-openstack/'
                      'ansible-role-tripleo-collect-logs/tarball')

        playbook = """
- hosts: localhost
  vars:
    dci_status: %s
    dci_comment: 'Installing tripleo-collect-logs on localhost'
    dci_log_prefix: 'tripleo-collect-logs'
  tasks:
    - name: Install ansible tripleo-collect-logs role
      shell: ansible-galaxy install %s && mv /etc/ansible/roles/tarball /etc/ansible/roles/tripleo-collect-logs
      args:
        creates: /etc/ansible/roles/tripleo-collect-logs
""" % (state, module_url)  # noqa

        rv = self.run_playbook(playbook, context)
        if rv != 0:
            return rv

        playbook = """
- hosts: %s
  remote_user: stack
  vars:
    dci_status: %s
    dci_comment: 'Running ansible module tripleo-collect-logs'
    dci_log_prefix: 'tripleo-collect-logs'
    artcl_collect_dir: /tmp/collect-files
  roles:
    - tripleo-collect-logs

- hosts: localhost
  vars:
    dci_status: %s
    dci_comment: 'Upload tripleo-collect-logs results'
    dci_log_prefix: 'tripleo-collect-logs'
  tasks:
    - name: Upload tripleo-collect-logs
      dci_upload:
        file: '{{ artcl_collect_dir }}/%s.tar.gz'
        dci_login: %s
        dci_password: %s
        dci_cs_url: %s
        dci_status: %s
        job_id: %s
""" % (host, state, state, host, context.login, auth['dci_password'], context.dci_cs_api.replace('/api/v1', ''), state, context.last_job_id)  # noqa

        return self.run_playbook(playbook, context)
