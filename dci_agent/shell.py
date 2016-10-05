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

from dci_agent import config
from dci_agent import version
from dciclient.v1.api import context as dci_context
from dciclient.v1.api import file as dci_file
from dciclient.v1.api import job as dci_job
from dciclient.v1.api import jobstate as dci_jobstate
from dciclient.v1.api import remoteci as dci_remoteci
from dciclient.v1.api import topic as dci_topic
from dciclient.v1 import helper as dci_helper
from dciclient.v1 import tripleo_helper as dci_tripleo_helper

import tripleohelper.server
import tripleohelper.undercloud

import argparse
import logging
import os
import os.path
import sys
import traceback


def get_dci_context(**args):
    """Retrieve a DCI context from the dciclient. """

    args['user_agent'] = 'dci-agent-' + version.__version__
    if 'dci_cs_url' not in args:
        args['dci_cs_url'] = 'https://api.distributed-ci.io'

    return dci_context.build_dci_context(**args)


def get_dci_job_data(ctx, **dci):
    """Retrieve informations about the job to run. """

    topic_id = dci_topic.get(ctx, dci['topic']).json()['topic']['id']
    remoteci = dci_remoteci.get(ctx, dci['remoteci']).json()
    remoteci_id = remoteci['remoteci']['id']

    r = dci_job.schedule(ctx, remoteci_id, topic_id=topic_id)
    if r.status_code == 412:
        logging.info('Nothing to do')
        exit(0)
    elif r.status_code != 201:
        logging.error('Unexpected code: %d' % r.status_code)
        logging.error(r.text)
        exit(1)

    job_full_data = dci_job.get_full_data(ctx, ctx.last_job_id)

    return job_full_data


def init_undercloud_host(undercloud_ip, key_filename):
    # Waiting for the undercloud host to be back
    undercloud = tripleohelper.undercloud.Undercloud(
        hostname=undercloud_ip,
        user='stack',
        key_filename=key_filename)
    # copy our public SSH key to be able later to run our tests
    undercloud.run('sudo mkdir -p /root/.ssh', retry=600, user='stack')
    undercloud.run('sudo chmod 700 /root/.ssh', user='stack')
    undercloud.run('sudo cp /home/stack/.ssh/authorized_keys /root/.ssh/',
                   user='stack')


def prepare_local_mirror(ctx, mirror_location, mirror_url, components):
    repo_entry = """
[{name}]
name={name}
baseurl={mirror_url}{path}
enable=1
gpgcheck=0
priority=0

"""
    dci_jobstate.create(ctx, 'pre-run', 'refreshing local mirror',
                        ctx.last_job_id)
    with open(mirror_location + '/RHOS-DCI.repo', 'w') as f:
        for c in components:
            dest = mirror_location + '/' + c['data']['path']
            if not os.path.exists(dest):
                os.makedirs(dest)
            dci_helper.run_command(
                ctx,
                [
                    'rsync',
                    '-av',
                    '--hard-links',
                    'partner@rhos-mirror.distributed-ci.io:/srv/puddles/' +
                    c['data']['path'] + '/',
                    dest])
            f.write(repo_entry.format(
                mirror_url=mirror_url,
                name=c['data']['repo_name'],
                path=c['data']['path']))


def main(argv=None):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic')
    parser.add_argument('--config', default='/etc/dci/dci_agent.yaml')
    parser.add_argument('--version', action='version',
                        version=('dci-agent %s' % version.__version__))
    args = parser.parse_args(argv)

    dci_conf = config.load_config(args.config)
    ctx = get_dci_context(**dci_conf['auth'])

    topic_name = args.topic if args.topic else dci_conf['topic']
    cnf = {'topic': topic_name, 'remoteci': dci_conf['remoteci']}
    job_data = get_dci_job_data(ctx, **cnf)

    logging.debug(job_data['components'])

    try:
        prepare_local_mirror(ctx,
                             dci_conf['mirror']['directory'],
                             dci_conf['mirror']['url'],
                             job_data['components'])
        dci_jobstate.create(ctx, 'pre-run', 'director node provisioning',
                            ctx.last_job_id)
        for c in dci_conf['hooks']['provisioning']:
            dci_helper.run_command(ctx, c, shell=True)
        init_undercloud_host(dci_conf['undercloud_ip'],
                             dci_conf['key_filename'])
        dci_jobstate.create(
            ctx,
            'running',
            'undercloud deployment',
            ctx.last_job_id)
        for c in dci_conf['hooks']['undercloud']:
            dci_helper.run_command(ctx, c, shell=True)
        dci_jobstate.create(ctx, 'running', 'overcloud deployment',
                            ctx.last_job_id)
        for c in dci_conf['hooks']['overcloud']:
            dci_helper.run_command(ctx, c, shell=True)
        dci_tripleo_helper.run_tests(
            ctx,
            undercloud_ip=dci_conf['undercloud_ip'],
            key_filename=dci_conf['key_filename'],
            remoteci_id=job_data['remoteci']['id'],
            stack_name=dci_conf.get('stack_name', 'overcloud'))
        final_status = 'success'
        backtrace = ''
        msg = ''
    except Exception as e:
        final_status = 'failure'
        backtrace = traceback.format_exc()
        msg = str(e)
        pass

    # Teardown should happen even in case of failure and should not make the
    # agent run fail.
    try:
        teardown_commands = dci_conf['hooks'].get('teardown')
        if teardown_commands:
            dci_jobstate.create(ctx, 'post-run', 'teardown',
                                ctx.last_job_id)
            for c in teardown_commands:
                dci_helper.run_command(ctx, c, shell=True)
    except Exception as e:
        backtrace_teardown = str(e) + '\n' + traceback.format_exc()
        logging.error(backtrace_teardown)
        dci_file.create(
            ctx,
            'backtrace_teardown',
            backtrace_teardown,
            mime='text/plain',
            jobstate_id=ctx.last_jobstate_id)
        pass

    dci_jobstate.create(
        ctx,
        final_status,
        msg,
        ctx.last_job_id)
    logging.info('Final status: ' + final_status)
    if backtrace:
        logging.error(backtrace)
        dci_file.create(
            ctx,
            'backtrace',
            backtrace,
            mime='text/plain',
            jobstate_id=ctx.last_jobstate_id)
    sys.exit(0 if final_status == 'success' else 1)
