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

# Goal: Send an email after the job has finished. Mail can be sent upon status
#       exit
#
#
# Requisite: In order to use this plugin an 'email_receivers' value should be
#            part of the RemoteCI data field.


from dciclient.v1 import remoteci 


class Email(object):
    """The email DCI post-plugin. """

    def __init__(self):
        self.email_receivers = remoteci.get_data(remoteci_id,
                                                 ['email_receivers'])


    def _run_command(self, cmd):
        """Generic method to run a shell script command. """

        process = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)

        out, err = process.communicate()
        errcode = process.returncode


    def run(remoteci_id):
        pass
