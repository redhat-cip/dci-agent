#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Red Hat, Inc
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

import codecs
from pip.req import parse_requirements
import setuptools


def _get_readme():
    with codecs.open('README.rst', 'r', encoding='utf8') as f:
        return f.read()

dep_requires = []
dep_links = []
for req_line in parse_requirements('requirements.txt', session=False):
    if req_line.link:
        dep_links.append(str(req_line.link.url))
    else:
        dep_requires.append(str(req_line.req))

setuptools.setup(
    name='dci-agent',
    version='0.1a3',
    packages=['dci_agent'],
    author='Distributed CI team',
    author_email='distributed-ci@redhat.com',
    description='DCI agent for DCI Control Server',
    long_description=_get_readme(),
    install_requires=dep_requires,
    dependency_links=dep_links,
    url='https://github.com/redhat-cip/python-dciclient',
    license='Apache v2.0',
    include_package_data=True,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: System :: Distributed Computing'
    ],
    entry_points={
        'console_scripts': [
            'dci-agent = dci_agent.dci_agent:main',
        ],
    }
)
