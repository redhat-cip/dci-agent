# -*- encoding: utf-8 -*-
#
# Copyright 2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import dci_agent.dci_agent as agent
from dciclient.v1.api import file as dci_file
from dciclient.v1.api import jobstate as dci_jobstate
import dciclient.v1.helper
import tripleohelper.undercloud

import mock
from mock import ANY
import os.path
import pytest


def test_prepare_local_mirror(dci_context, components, tmpdir, job_id):
    td = tmpdir
    agent.prepare_local_mirror(
        dci_context,
        td.strpath,
        'http://somewhere',
        components)
    c_dir = tmpdir.join(dci_context.last_job_id)
    c_dir = c_dir.join(components[0]['canonical_project_name'])
    assert c_dir.check()
    assert c_dir.join('some-file.txt').open().read() == 'foo'


def test_dci_agent_success(monkeypatch, dci_context, job_id):
    def return_context(**args):
        return dci_context
    mock_run_commands = mock.Mock()
    mock_run_tests = mock.Mock()
    monkeypatch.setattr(agent, 'get_dci_context', return_context)
    monkeypatch.setattr(dciclient.v1.helper, 'run_command',
                        mock_run_commands)
    monkeypatch.setattr(tripleohelper.undercloud, 'Undercloud', mock.Mock())
    monkeypatch.setattr(dciclient.v1.tripleo_helper, 'run_tests',
                        mock_run_tests)
    with pytest.raises(SystemExit):
        agent.main(['--topic', 'topic_name', '--config',
                    os.path.dirname(__file__) + '/dci_agent.yaml'])

    calls = [
        mock.call(dci_context, 'ansible-playbook provisioning.yaml',
                  shell=True),
        mock.call(dci_context, 'ansible-playbook undercloud.yaml',
                  shell=True),
        mock.call(dci_context, 'ansible-playbook overcloud.yaml',
                  shell=True),
    ]
    mock_run_commands.assert_has_calls(calls)
    js = dci_jobstate.list(dci_context).json()['jobstates']
    comments = [i['comment'] for i in js]
    assert comments[0] == 'refreshing local mirror'
    assert comments[1] == 'director node provisioning'
    assert comments[2] == 'undercloud deployment'
    assert comments[3] == 'overcloud deployment'
    mock_run_tests.assert_called_with(dci_context,
                                      key_filename='/home/dci/.ssh/id_rsa',
                                      remoteci_id=ANY,
                                      stack_name='lab2',
                                      undercloud_ip='192.168.100.10')

    assert js[-1]['status'] == 'success'
    assert js[-1]['comment'] is None


def test_dci_agent_failure(monkeypatch, dci_context, job_id):
    def return_context(**a):
        return dci_context

    def raise_exception(*a, **b):
        raise Exception('booom')
    mock_run_commands = mock.Mock()
    mock_run_tests = raise_exception
    monkeypatch.setattr(agent, 'get_dci_context', return_context)
    monkeypatch.setattr(dciclient.v1.helper, 'run_command',
                        mock_run_commands)
    monkeypatch.setattr(tripleohelper.undercloud, 'Undercloud', mock.Mock())
    monkeypatch.setattr(dciclient.v1.tripleo_helper, 'run_tests',
                        mock_run_tests)
    with pytest.raises(SystemExit):
        agent.main(['--topic', 'topic_name', '--config',
                    os.path.dirname(__file__) + '/dci_agent.yaml'])

    js = dci_jobstate.list(dci_context).json()['jobstates']
    assert js[-1]['status'] == 'failure'
    assert js[-1]['comment'] == 'booom'

    # the where filter does not work yet:
    #   I1f0df01f813efae75f6e0e75a3861d2d4ba5694a
    files = dci_file.list(dci_context).json()['files']
    content = dci_file.content(dci_context, files[-1]['id'])
    assert 'most recent call last' in content.text
