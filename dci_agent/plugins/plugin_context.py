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
Plugin to upload file to the Control-Server

  :param array path: Array of path to files to upload

"""

from dci_agent.plugins import plugin
from dciclient.v1.api import file as dci_file


class Context(plugin.Plugin):

    def __init__(self, conf):
        super(Context, self).__init__(conf)

    def run(self, state, data=None, context=None, auth=None):
        """Upload configuration files. """

        if 'path' in self.conf:
            for f in self.conf['path']:
                try:
                    content = open(f, 'r').read()
                    dci_file.create(context=context, name=f,
                                    content=content,
                                    job_id=context.last_job_id)
                except OSError as e:
                    raise(e)
                except IOError as e:
                    raise(e)
        return 0
