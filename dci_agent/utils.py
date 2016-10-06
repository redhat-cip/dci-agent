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

import importlib
import sys


def load_plugin(hook):
    """Dynamically load a plugin associated to a given hook. The plugin module
    should be located at 'dci_agent.plugins.plugin_<hook>', within the plugin
    module a class should be found with the name corresponding to the hook's
    name with the first character capitalized.

    Example: with the hook 'file', a module should be found
    at 'dci_agent.plugins.plugin_file' and the class 'File' within it.
    """

    try:
        module_path = 'dci_agent.plugins.plugin_%s' % hook
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
