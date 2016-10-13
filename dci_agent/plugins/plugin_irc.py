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
Plugin to send irc notification

  :param string message: Message to send to the IRC channel
  :param string server: IRC server to connect to
  :param int port: IRC server port to connect to
  :param string chan: IRC channel to connect to
  :param string nick: Nick to use when connecting to IRC

"""

from dci_agent.plugins import plugin


class Irc(plugin.Plugin):

    def __init__(self, conf):
        super(Irc, self).__init__(conf)

    def run(self, state, data=None, context=None):
        """Connect to the specified IRC server/channel and post a message. """

        message = self.conf[state]['message']

        server = self.conf['server']
        port = self.conf['port']
        chan = self.conf['chan']

        nick = self.conf['nick']

        playbook = """
- hosts: localhost
  tasks:
    - irc: channel='%s'
           server='%s'
           msg='%s'
           nick='%s'
           port='%s'
""" % (chan, server, self.format(message, data, context), nick, port)

        return self.run_playbook(playbook, context)
