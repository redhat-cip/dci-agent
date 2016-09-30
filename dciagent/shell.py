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

import click
import requests

from dciagent import config

from dciclient.v1.api import job as dci_job
from dciclient.v1.api import jobstate as dci_jobstate
from dciclient.v1.api import context as dci_context
from dciclient.v1.api import remoteci as dci_remoteci
from dciclient.v1.api import topic as dci_topic

import importlib
import sys


def get_dci_context(**auth):
    """Retrieve a DCI context from the dciclient. """

    if 'dci_cs_url' not in auth:
        auth['dci_cs_url'] = 'https://api.distributed-ci.io'

    return dci_context.build_dci_context(**auth)


def get_dci_job_data(ctx, **dci):
    """Retrieve informations about the job to run. """

    topic_id = dci_topic.get(ctx, dci['topic']).json()['topic']['id']
    remoteci = dci_remoteci.get(ctx, dci['remoteci']).json()
    remoteci_id = remoteci['remoteci']['id']

    r = dci_job.schedule(ctx, remoteci_id, topic_id=topic_id)
    if r.status_code == 412:
        exit(0)
    elif r.status_code != 201:
        exit(1)

    job_full_data = dci_job.get_full_data(ctx, ctx.last_job_id)

    return job_full_data


def load_plugin(hook):
    """Dynamically load a plugin associated to a given hook. The plugin module
    should be located at 'dciagent.plugins.plugin_<hook>', within the plugin
    module a class should be found with the name corresponding to the hook's
    name with the first character capitalized.

    Example: with the hook 'file', a module should be found
    at 'dciagent.plugins.plugin_file' and the class 'File' within it.
    """

    try:
        module_path = 'dciagent.plugins.plugin_%s' % hook
        loaded_module = importlib.import_module(module_path)
        class_name = hook.capitalize()
        return getattr(loaded_module, hook.capitalize())
    except ImportError:
        print("hook '%s' does not exist.")
        sys.exit(1)
    except AttributeError:
        print("Attribute '%s' of module '%s' does not exist." % (class_name,
                                                                 module_path))
        sys.exit(1)


@click.command()
@click.option('--config-file', envvar='DCI_AGENT_CONFIG', required=False,
              help="DCI CS url.")
def main(config_file=None):
    # redirect the log messages to the DCI Control Server
    # https://github.com/shazow/urllib3/issues/523
    requests.packages.urllib3.disable_warnings()

    RV = 0

    # Parse and retrieve configuration file
    configuration = config.load_config(config_file)

    # Parse and retrieve dci_context
    context = get_dci_context(**configuration['auth'])

    # Retrieve available job
    datas = get_dci_job_data(context, **configuration['dci'])

    states = ['new', 'pre-run', 'running', 'post-run', 'success']
    for state in states:

        if RV != 0:
            break

        if state in configuration['dci']:
            for hook in configuration['dci'][state]:

                if RV != 0:
                    break

                dci_jobstate.create(context, state, 'Running %s hook' % hook,
                                    context.last_job_id)

                # load the plugin associated to the hook and then run it
                plugin_class = load_plugin(hook)
                plugin_class(configuration[hook]).run(state, data=datas,
                                                      context=context)

    # Handle the push of the last 'success' job state if no plugin
    # have been configured to take an action on success
    if RV == 0 and 'success' not in configuration['dci']:
        dci_jobstate.create(context, 'success', 'Successfully ran the agent',
                            context.last_job_id)

    # Deal with failure state, run on failure actions
    if RV != 0 and 'failure' in configuration['dci']:
        for hook in configuration['dci']['failure']:
            dci_jobstate.create(context, 'failure', 'Running %s hook' % hook,
                                context.last_job_id)

    if RV != 0:
        dci_jobstate.create(context, 'failure',
                            'A failure occured during the agent run',
                            context.last_job_id)
        # load the plugin associated to the hook and then run it
        plugin_class = load_plugin(hook)
        plugin_class(configuration[hook]).run('failure', data=datas,
                                              context=context)
