#
# Copyright (c) 2026 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

"""Shared test helpers for k8sapp_harbor unit tests."""

import unittest
from unittest import mock


def create_sysinv_mock_modules(extra_modules=None):
    """Create base sysinv mock module dict.

    Args:
        extra_modules: Additional modules to add to the dict.

    Returns:
        Dict of module name to mock suitable for patch.dict.
    """
    mods = {
        'oslo_log': mock.MagicMock(),
        'oslo_log.log': mock.MagicMock(),
    }
    if extra_modules:
        mods.update(extra_modules)
    return mods


def patch_and_cleanup(mods, prefix):
    """Patch sys.modules and clean cached submodules.

    Args:
        mods: Dict of module mocks for patch.dict.
        prefix: Module prefix to clean (e.g. 'k8sapp_harbor.helm.').
    """
    patcher = mock.patch.dict('sys.modules', mods)
    patcher.start()
    unittest.addModuleCleanup(patcher.stop)
    sysmod = __import__('sys').modules
    for k in list(sysmod.keys()):
        if k.startswith(prefix) and k != prefix.rstrip('.'):
            del sysmod[k]
