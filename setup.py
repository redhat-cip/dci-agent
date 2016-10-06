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
import os
import setuptools

from dci_agent import version


def _get_requirements():
    requirements_path = '%s/%s' % (os.path.dirname(os.path.abspath(__file__)),
                                   'requirements.txt')
    with open(requirements_path, 'r') as f:
        requirements = f.read()
        # remove the dependencies which comes from url source because
        # it's not supported by install_requires
        return [dep for dep in requirements.split('\n')
                if not dep.startswith('-e')]


def _get_readme():
    with codecs.open('README.rst', 'r', encoding='utf8') as f:
        return f.read()


setuptools.setup(
    name='dci-agent',
    version=version,
    packages=['dci_agent'],
    author='Distributed CI team',
    author_email='distributed-ci@redhat.com',
    url='https://github.com/redhat-openstack/dci-agent',
    description='DCI agent for DCI Control Server',
    long_description=_get_readme(),
    install_requires=_get_requirements(),
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
