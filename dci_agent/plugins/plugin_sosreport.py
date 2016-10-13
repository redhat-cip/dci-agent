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


PARAMS = ['hosts', 'onlyplugins', 'enableplugins', 'noplugins']


class Sosreport(plugin.Plugin):

    def __init__(self, conf):
        super(Sosreport, self).__init__(conf)

    def run(self, state, data=None, context=None):
        """Run the sosreport command on the specified hosts."""

        self.fill_configuration(state, data, PARAMS)

        for host in self.conf[state]['hosts']:

            command = 'sosreport --batch --name %s' % host

            if 'onlyplugins' in self.conf[state]:
                command += ' -o %s' % ','.join(self.conf[state]['onlyplugins'])
            else:
                if 'enableplugins' in self.conf[state]:
                    command += ' -e %s' % ','.join(
                        self.conf[state]['enableplugins']
                    )
                if 'noplugins' in self.conf[state]:
                    command += ' -n %s' % ','.join(
                        self.conf[state]['noplugins']
                    )

            playbook = """
- hosts: %s
  vars:
    dci_status: %s
    dci_comment: 'Collecting sosreport for %s'
    dci_log_prefix: 'sosreport'
  tasks:
    - name: Install sos package
      package:
        name: sos

    - name: Run sosreport
      shell: %s
""" % (host, state, host, command)

            self.run_playbook(playbook, context)
