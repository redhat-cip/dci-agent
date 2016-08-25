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

# Goal: Run the Red Hat certification test suite and submit back the results
#       to Red Hat servers
#
#
# Requisite: In order to use this plugin a 'certification_id' value should be
#            part of the RemoteCI data field.


from dciclient.v1 import remoteci 




class RhCert(object):
    """The rhcert DCI test-plugin. """

    def __init__(self):
        self.certification_id = remoteci.get_data(remoteci_id,
                                                  ['certification_id'])


    def _run_command(self, cmd):
        """Generic method to run a shell script command. """

        process = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)

        out, err = process.communicate()
        errcode = process.returncode


    def run(remoteci_id):

        # 1. Run the tests for the given 'certification_id'
        cmd = 'rhcert-ci run --key "%s" --client "127.0.0.1" --debug high' %
              certification_id 
        self._run_command(cmd)
        

        # 2. Submit the results to Red Hat servers
        cmd = 'rhcert-ci submit --key "%s" --client "127.0.0.1" --debug high' %
              certification_id 
        self._run_command(cmd)
