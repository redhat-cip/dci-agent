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

import dci_agent.config as conf
import dci_agent.utils as utils
import dci_agent.version as version

from dciclient.v1.api import component as dci_component
from dciclient.v1.api import context as dci_context
from dciclient.v1.api import file as dci_file
from dciclient.v1.api import job as dci_job
from dciclient.v1.api import jobstate as dci_jobstate
from dciclient.v1.api import remoteci as dci_remoteci
from dciclient.v1.api import topic as dci_topic
from dciclient.v1 import helper as dci_helper
from dciclient.v1 import tripleo_helper as dci_tripleo_helper

import click
import glob
import logging
import os
import os.path
import shutil
import subprocess
import sys
import tarfile
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


def prepare_local_mirror(ctx, mirror_location, mirror_url, components):
    """Fetch the different components and prepare a repo file."""
    repo_entry = """
[{name}]
name={name}
baseurl={mirror_url}{path}
enable=1
gpgcheck=0
priority=0

"""
    if os.path.exists(mirror_location + '/current'):
        shutil.rmtree(mirror_location + '/current')
    dci_jobstate.create(ctx, 'pre-run', 'refreshing local mirror',
                        ctx.last_job_id)
    repo_dest = mirror_location + '/' + ctx.last_job_id
    print(mirror_location + '/' + ctx.last_job_id + '.repo')
    with open(mirror_location + '/' + ctx.last_job_id + '.repo', 'w') as f:
        for c in components:
            tarball_dest = mirror_location + '/' + c['id'] + '.tar'
            if not os.path.exists(repo_dest):
                os.makedirs(repo_dest)
            component_file = dci_component.file_list(
                ctx, c['id']).json()['component_files'][0]
            # TODO(Goneri): test the md5/size of the existing tarball first
            if not os.path.exists(tarball_dest):
                dci_component.file_download(
                    ctx,
                    c['id'],
                    component_file['id'],
                    tarball_dest)
            with tarfile.open(name=tarball_dest, mode='r:') as tf:
                tf.extractall(path=repo_dest)
            project_name = c['canonical_project_name']
            f.write(repo_entry.format(
                mirror_url=mirror_url,
                name=c['data']['repo_name'],
                path='/' + ctx.last_job_id + '/' + project_name))


def clean_local_mirror(ctx, mirror_location):
    os.unlink(mirror_location + '/' + ctx.last_job_id + '.repo')
    shutil.rmtree(mirror_location + '/' + ctx.last_job_id)


def get_topic_and_remoteci(dci_conf, topic=None):
    """Return the Topic and RemoteCI details."""

    if 'dci' in dci_conf:
        topic_name = dci_conf['dci']['topic']
        remoteci_name = dci_conf['dci']['remoteci']
    else:
        remoteci_name = dci_conf['remoteci']
        if 'topic' in dci_conf:
            topic_name = dci_conf['topic']
        else:
            topic_name = topic

    return {
        'topic': topic_name,
        'remoteci': remoteci_name,
    }


@click.command()
@click.option('--topic', envvar='DCI_AGENT_TOPIC', required=False,
              help="Topic the agent apply to.")
@click.option('--config', envvar='DCI_AGENT_CONFIG', required=False,
              help="Path to DCI config file.")
def main(config=None, topic=None):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    dci_conf = conf.load_config(config)
    ctx = get_dci_context(**dci_conf['auth'])

    cnf = get_topic_and_remoteci(dci_conf, topic)
    job_data = get_dci_job_data(ctx, **cnf)

    logging.debug(job_data['components'])

    # This is the core of the v2 of the agent
    # It is triggered only if a 'dci' section is present in the
    # configuration file.
    if 'dci' in dci_conf:
        RV = 0
        states = ['new', 'pre-run', 'running', 'post-run', 'success']
        # (spredzy): Make a plugin out of the prepare_local_mirror
        # function
        try:
            prepare_local_mirror(ctx,
                                 dci_conf['mirror']['directory'],
                                 dci_conf['mirror']['url'],
                                 job_data['components'])
        except Exception as e:
            RV = 1
            dci_jobstate.create(ctx, 'failure',
                                'Failure during the local mirror preparation',
                                ctx.last_job_id)

        for state in states:
            if state in dci_conf['dci'] and RV == 0:
                for hook in dci_conf['dci'][state]:
                    dci_jobstate.create(ctx, state, 'Running %s hook' % hook,
                                        ctx.last_job_id)
                    # load the plugin associated to the hook and then run it
                    plugin_class = utils.load_plugin(hook)
                    RV = plugin_class(dci_conf[hook]).run(state, data=job_data,
                                                          context=ctx)
                    if RV != 0:
                        if 'failure' in dci_conf['dci']:
                            for hook in dci_conf['dci']['failure']:
                                dci_jobstate.create(ctx, 'failure',
                                                    'Running %s hook' % hook,
                                                    ctx.last_job_id)
                                # load the plugin associated to the hook and
                                # then run it
                                plugin_class = utils.load_plugin(hook)
                                plugin_class(dci_conf[hook]).run(
                                    'failure', data=job_data, context=ctx
                                )
                        else:
                            dci_jobstate.create(
                                ctx, 'failure',
                                'A failure occured during the agent run',
                                ctx.last_job_id
                            )
                        break

        # Handle the push of the last 'success' job state if no plugin
        # have been configured to take an action on success
        if RV == 0 and 'success' not in dci_conf['dci']:
            dci_jobstate.create(ctx, 'success', 'Successfully ran the agent',
                                ctx.last_job_id)
        clean_local_mirror(ctx, dci_conf['mirror']['directory'])

    # This is the core of the v1 of the agent
    # This code is run by default except if a 'dci' section is specified in
    # the configuration file
    else:
        try:
            prepare_local_mirror(ctx,
                                 dci_conf['mirror']['directory'],
                                 dci_conf['mirror']['url'],
                                 job_data['components'])
            dci_jobstate.create(ctx, 'pre-run', 'director node provisioning',
                                ctx.last_job_id)
            for c in dci_conf['hooks']['provisioning']:
                dci_helper.run_command(ctx, c, shell=True)
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
            if 'undercloud_ip_command' in dci_conf:
                undercloud_ip = subprocess.Popen(
                    dci_conf['undercloud_ip_command'],
                    shell=True,
                    stdout=subprocess.PIPE).stdout.read().rstrip()
            else:
                undercloud_ip = dci_conf['undercloud_ip']
            dci_tripleo_helper.run_tests(
                ctx,
                undercloud_ip=undercloud_ip,
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

        # Teardown should happen even in case of failure and should not make
        # the agent run fail.
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

        clean_local_mirror(ctx, dci_conf['mirror']['directory'])

        if dci_conf.get('log_path'):
            for log_file in glob.glob(dci_conf['log_path']):
                logging.info('Uploading: %s' % log_file)
                with open(log_file, 'r') as f:
                    print(dci_file.create(
                        ctx,
                        log_file,
                        f.read(),
                        mime='text/plain',
                        job_id=ctx.last_job_id).text)

        sys.exit(0 if final_status == 'success' else 1)
