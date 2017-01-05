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
Plugin to write data to file.

  :param string path: Path of the file to write data to
  :param string message: Message to write to the file

"""

from dci_agent.plugins import plugin


class File(plugin.Plugin):

    def __init__(self, conf):
        super(File, self).__init__(conf)

    def run(self, state, data=None, context=None, auth=None):
        """Write into the file specified in the configuration file.

           Write the specified string in the file specified in the
           configuration file while doing all the interpolation process.
        """

        message = None
        path = None

        if state in self.conf:
            if 'message' in self.conf[state]:
                message = self.conf[state]['message']
            if 'path' in self.conf[state]:
                path = self.conf[state]['path']

        if message is None:
            message = self.conf['message']

        if path is None:
            path = self.conf['path']

        try:
            open(path, 'w').write(message)
            return 0
        except OSError as e:
            raise(e)
        except IOError as e:
            raise(e)
