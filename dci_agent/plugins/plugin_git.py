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
Plugin to clone a git repository

  :param string repository: URL of the git repository
  :param string version: Version (commit/tag) to retrieve
  :param string dest: Path on the filesystem where to store the repository
"""

from dci_agent.plugins import plugin


PARAMS = ['repository', 'version', 'dest']


class Git(plugin.Plugin):

    def __init__(self, conf):
        super(Git, self).__init__(conf)

    def run(self, state, data=None, context=None, auth=None):
        """Clone the specified git repository."""

        self.fill_configuration(state, data, PARAMS)

        if state in self.conf:
            repo = self.conf[state]['repo']
            dest = self.conf[state]['dest']
            version = None

            if 'version' in self.conf[state]:
                version = self.conf[state]['version']

        playbook = """
- hosts: localhost
  vars:
    dci_status: %s
    dci_comment: 'Clone repository %s'
    dci_log_prefix: 'git'
  tasks:
    - name: Clong repository %s
      git:
        repo: %s
        version: %s
        dest: %s
""" % (state, repo, repo, repo, version, dest)

        return self.run_playbook(playbook, context)
