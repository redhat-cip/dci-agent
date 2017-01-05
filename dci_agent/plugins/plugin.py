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
Base Plugin class. Every plugin must inherit from it.
"""

from dci_agent.ansible import runner

import os
import random
import string


class Plugin(object):

    def __init__(self, conf):
        self.conf = conf

    def format(self, message, data=None, context=None):
        """Format string by interpolating known variable.

          %j: jobdefinition name
          %r: remoteci name
          %c: comma separated list of components name
          %i: the job id
          %u: user name
        """

        if '%j' in message:
            message = message.replace('%j', data['jobdefinition']['name'])
        if '%r' in message:
            message = message.replace('%r', data['remoteci']['name'])
        if '%i' in message:
            message = message.replace('%i', context.last_job_id)
        if '%u' in message:
            message = message.replace('%u', context.login)
        if '%c' in message:
            components = ', '.join([c['name'] for c in data['components']])
            message = message.replace('%c', components)

        return message

    def run(self, state, data=None, context=None, auth=None):
        pass

    def fill_configuration(self, state, data, keys):
        """Return a structure with all the keys set. """

        for key in keys:
            if state in self.conf and key in self.conf[state]:
                continue
            if key in self.conf:
                if state not in self.conf:
                    self.conf[state] = {}
                self.conf[state][key] = self.conf[key]

    def run_playbook(self, playbook, context, **kwargs):
        """Run the playbook generated by the plugin. """

        rand_string = ''.join(
            random.choice(
                string.ascii_letters + string.digits
            ) for _ in range(10)
        )
        open('/tmp/%s.yml' % rand_string, 'w').write(playbook)

        l_runner = runner.Runner(playbook='/tmp/%s.yml' % rand_string,
                                 dci_context=context,
                                 verbosity=0)
        res = l_runner.run(job_id=context.last_job_id, **kwargs)

        os.remove('/tmp/%s.yml' % rand_string)

        return len(res.failures)
