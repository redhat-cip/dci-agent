#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""
Plugin to run ansible playbook

  :param string playbook: Path to playbook to run
  :param string template: Path to playbook template to generate

"""

import jinja2

from dci_agent.plugins import plugin


class Ansible(plugin.Plugin):

    def __init__(self, conf):
        super(Ansible, self).__init__(conf)

    def generate_ansible_playbook_from_template(self, template_file, data):
        templateLoader = jinja2.FileSystemLoader(searchpath="/")
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(template_file)
        outputText = template.render(data)

        return outputText

    def run(self, state, data=None, context=None, auth=None):
        """Run ansible-playbook on the specified playbook. """

        playbook = None
        template = None

        if state in self.conf:
            if 'playbook' in self.conf[state]:
                playbook = self.conf[state]['playbook']
            if 'template' in self.conf[state]:
                template = self.conf[state]['template']

        if playbook is None:
            playbook = self.conf['playbook']
        if template is None and template in self.conf:
            template = self.conf['template']

        if template:
            open(playbook, 'w').write(
                self.generate_ansible_playbook_from_template(template, data)
            )

        kwargs = {}
        if 'certification_id' in data['remoteci']['data']:
            kwargs.update({'certification_id':
                           data['remoteci']['data']['certification_id']})

        return self.run_playbook(open(playbook, 'r').read(), context, **kwargs)
