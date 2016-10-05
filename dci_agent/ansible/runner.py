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

from ansible import inventory
from ansible import vars
from ansible.executor import playbook_executor
from ansible.executor import task_queue_manager
from ansible.parsing import dataloader
from ansible.playbook import Playbook
from ansible.plugins import callback
from dciagent.ansible.dci_callback_plugin import CallbackModule as DciCallback


class Options(object):
    def __init__(self, verbosity=None, inventory=None, listhosts=None,
                 subset=None, module_path=None, extra_vars=[], forks=5,
                 ask_vault_pass=None, vault_password_files=None,
                 new_vault_password_file=None, output_file=None, tags='all',
                 skip_tags=None, one_line=None, tree=None, ask_sudo_pass=None,
                 ask_su_pass=None, sudo=None, sudo_user=None, become=None,
                 become_method=None, become_user=None, become_ask_pass=None,
                 ask_pass=None, private_key_file=None, remote_user=None,
                 connection=None, timeout=None, ssh_common_args=None,
                 sftp_extra_args=None, scp_extra_args=None,
                 ssh_extra_args=None, poll_interval=None, seconds=None,
                 check=None, syntax=None, diff=None, force_handlers=None,
                 flush_cache=None, listtasks=None, listtags=None):
        self.verbosity = verbosity
        self.inventory = inventory
        self.listhosts = listhosts
        self.subset = subset
        self.module_path = module_path
        self.extra_vars = extra_vars
        self.forks = forks
        self.ask_vault_pass = ask_vault_pass
        self.vault_password_files = vault_password_files
        self.new_vault_password_file = new_vault_password_file
        self.output_file = output_file
        self.tags = tags
        self.skip_tags = skip_tags
        self.one_line = one_line
        self.tree = tree
        self.ask_sudo_pass = ask_sudo_pass
        self.ask_su_pass = ask_su_pass
        self.sudo = sudo
        self.sudo_user = sudo_user
        self.become = become
        self.become_method = become_method
        self.become_user = become_user
        self.become_ask_pass = become_ask_pass
        self.ask_pass = ask_pass
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.connection = connection
        self.timeout = timeout
        self.ssh_common_args = ssh_common_args
        self.sftp_extra_args = sftp_extra_args
        self.scp_extra_args = scp_extra_args
        self.ssh_extra_args = ssh_extra_args
        self.poll_interval = poll_interval
        self.seconds = seconds
        self.check = check
        self.syntax = syntax
        self.diff = diff
        self.force_handlers = force_handlers
        self.flush_cache = flush_cache
        self.listtasks = listtasks
        self.listtags = listtags


class Runner(object):

    def __init__(self, playbook, dci_context, options=None, verbosity=3):

        if options is None:
            self._options = Options()
            self._options.verbosity = verbosity
            self._options.connection = 'ssh'

        self._loader = dataloader.DataLoader()
        self._variable_manager = vars.VariableManager()

        task_queue_manager.display.verbosity = verbosity
        callback.global_display.verbosity = verbosity

        self._inventory = inventory.Inventory(
            loader=self._loader,
            variable_manager=self._variable_manager,
            host_list='/etc/ansible/hosts'
        )
        self._variable_manager.set_inventory(self._inventory)

        # Instantiate our Callback plugin
        self._results_callback = DciCallback(dci_context=dci_context)

        self._playbook = Playbook.load(
            playbook,
            variable_manager=self._variable_manager,
            loader=self._loader)

        self._pbex = playbook_executor.PlaybookExecutor(
            playbooks=[playbook],
            inventory=self._inventory,
            variable_manager=self._variable_manager,
            loader=self._loader,
            options=self._options,
            passwords={})

    def run(self, job_id, **kwargs):
        """Run the playbook and returns the playbook's stats."""

        extra_vars = {'job_id': job_id}
        extra_vars.update(kwargs)

        self._variable_manager.extra_vars = extra_vars
        # set the custom callback plugin
        self._pbex._tqm._stdout_callback = self._results_callback
        self._pbex.run()
