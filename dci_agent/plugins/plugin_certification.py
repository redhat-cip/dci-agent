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
Plugin to run the certification test suite

  :param string undercloud_ip:
"""

from dci_agent.plugins import plugin


PARAMS = ['undercloud_ip']


class Certification(plugin.Plugin):

    def __init__(self, conf):
        super(Certification, self).__init__(conf)

    def run(self, state, data=None, context=None, auth=None):
        """Run the certification test suite on the specified host."""

        self.fill_configuration(state, data, PARAMS)

        host = self.conf['undercloud_ip']
        module_url = ('https://api.github.com/repos/redhat-cip/'
                      'ansible-role-openstack-certification/tarball')

        playbook = """
- hosts: localhost
  vars:
    dci_status: %s
    dci_comment: 'Installing openstack-certification ansible role  on localhost'
    dci_log_prefix: 'certification'
  tasks:
    - name: Install ansible openstack-certification role
      shell: ansible-galaxy install %s && mv /etc/ansible/roles/tarball /etc/ansible/roles/openstack-certification
      args:
        creates: /etc/ansible/roles/openstack-certification
""" % (state, module_url)  # noqa

        rv = self.run_playbook(playbook, context)
        if rv != 0:
            return rv

        playbook = """
- hosts: %s
  remote_user: stack
  become: yes
  vars:
    dci_status: %s
    dci_comment: 'Running ansible module openstack-certification'
    dci_log_prefix: 'certification'
  roles:
    - openstack-certification
""" % (host, state)

        kwargs = {}
        if 'certification_id' in data['remoteci']['data']:
            kwargs.update({'certification_id':
                           data['remoteci']['data']['certification_id']})

        return self.run_playbook(playbook, context, **kwargs)
