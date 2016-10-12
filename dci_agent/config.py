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

import glob
import os
import yaml


def get_files_path(file_path):
    """Return a list of file as the result of the Include directive. """

    includes = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('Include '):
                includes.append(line)

    pathes = []
    for include in includes:
        path = include[8:-1]
        if path[0] != '/':
            path = '/etc/%s' % path
        pathes += glob.glob(path)

    return pathes


def load_config(config_path=None):
    """Serialize the configuration file into an object and return it. """

    if config_path:
        file_path = config_path
    elif os.getenv('DCI_AGENT_CONFIG'):
        file_path = os.getenv('DCI_AGENT_CONFIG')
    else:
        file_path = '/etc/dci/dci_agent.yaml'

    file_path_content = open(file_path, 'r').read()
    content = ''
    if 'Include ' in file_path_content:
        pathes = get_files_path(file_path)
        with open(file_path, 'r') as f:
            for line in f:
                if 'Include ' not in line:
                    content += line
        if content:
            config = yaml.load(content)
        else:
            config = {}
        for path in pathes:
            config.update(yaml.load(open(path, 'r')))
    else:
        config = yaml.load(open(file_path, 'r'))

    if 'key_filename' not in config:
        config['key_filename'] = os.path.expanduser('~/.ssh/id_rsa')
    if 'repository' not in config['mirror']:
        config['mirror']['repository'] = '/var/www/html'

    return config
