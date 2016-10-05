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
Plugin to run tests attached to a job in the Control Server.

    :param sring undercloud_ip: IP of the undercloud host
    :param string key_filename: Path to the ssh keyfile
    :param string remoteci_id: RemoteCI id

"""

from dci_agent.plugins import plugin
from dciclient.v1 import tripleo_helper as dci_tripleo_helper


class Tests(plugin.Plugin):

    def __init__(self, conf):
        super(Tests, self).__init__(conf)

    def run(self, state, data=None, context=None):
        """Run the tripleo_helper.run_tests() method. """

        dci_tripleo_helper.run_tests(
            context,
            undercloud_ip=self.conf['undercloud_ip'],
            key_filename=self.conf['key_filename'],
            remoteci_id=self.conf['remoteci_id'],
            stack_name='overcloud')
