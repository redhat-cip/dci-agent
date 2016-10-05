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

import os
import yaml


def load_config(config_path):
    with open(config_path, 'r') as fd:
        dci_conf = yaml.load(fd)
    if 'key_filename' not in dci_conf:
        dci_conf['key_filename'] = os.path.expanduser('~/.ssh/id_rsa')
    if 'repository' not in dci_conf['mirror']:
        dci_conf['mirror']['repository'] = '/var/www/html'

    return dci_conf
