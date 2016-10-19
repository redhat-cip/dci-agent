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
Plugin to collect sosreport archive from specified servers

  :param array hosts:
  :param array onlyplugins:
  :param array enableplugins:
  :param array noplugins:
"""

from dci_agent.plugins import plugin


PARAMS = ['undercloud_ip']


class TripleoCollectLogs(plugin.Plugin):

    def __init__(self, conf):
        super(TripleoCollectLogs, self).__init__(conf)

    def run(self, state, data=None, context=None):
        """Run the tripleo-collect-logs role on the specified hosts."""

        self.fill_configuration(state, data, PARAMS)

        host = data['undercloud_ip']
        module_url = 'https://api.github.com/repos/redhat-openstack/ \
                      ansible-role-tripleo-collect-logs/tarball'

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
  
- hosts: %s
  vars:
    dci_status: %s
    dci_comment: 'Running ansible module tripleo-collect-logs'
    dci_log_prefix: 'tripleo-collect-logs'
  roles:
    - tripleo-collect-logs

""" % (state, module_url, host, state)

            return self.run_playbook(playbook, context)
