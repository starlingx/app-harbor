#
# Copyright (c) 2026 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

"""Unit tests for k8sapp_harbor.helm.harbor module."""

import unittest
from unittest import mock

from k8sapp_harbor.common import constants as app_constants
from tests.unit.conftest import (
    create_sysinv_mock_modules,
    patch_and_cleanup,
)


class _FakeBaseHelm(object):
    """Fake BaseHelm for testing."""
    SUPPORTED_NAMESPACES = ['kube-system']
    SUPPORTED_APP_NAMESPACES = {}

    def __init__(self):
        self.dbapi = mock.MagicMock()


class _FakeInvalidHelmNamespace(Exception):
    """Fake exception."""
    def __init__(self, **kwargs):
        super(_FakeInvalidHelmNamespace, self).__init__()


_BASE_MOD = mock.MagicMock()
_BASE_MOD.BaseHelm = _FakeBaseHelm
_EXC_MOD = mock.MagicMock()
_EXC_MOD.InvalidHelmNamespace = _FakeInvalidHelmNamespace
_CONST_MOD = mock.MagicMock()
_CONST_MOD.CONTROLLER = 'controller'
_CONST_MOD.WORKER = 'worker'
_HELM_MOD = mock.MagicMock()
_HELM_MOD.base = _BASE_MOD
_COMMON_MOD = mock.MagicMock()
_COMMON_MOD.constants = _CONST_MOD
_COMMON_MOD.exception = _EXC_MOD
_SYSINV_MOD = mock.MagicMock()
_SYSINV_MOD.common = _COMMON_MOD
_SYSINV_MOD.helm = _HELM_MOD

_MODS = create_sysinv_mock_modules({
    'sysinv': _SYSINV_MOD, 'sysinv.common': _COMMON_MOD,
    'sysinv.common.constants': _CONST_MOD,
    'sysinv.common.exception': _EXC_MOD,
    'sysinv.helm': _HELM_MOD, 'sysinv.helm.base': _BASE_MOD,
})
patch_and_cleanup(_MODS, 'k8sapp_harbor.helm.')

from k8sapp_harbor.helm import harbor  # noqa: E402
HarborHelm = harbor.HarborHelm


class TestHarborHelmAttributes(unittest.TestCase):
    """Tests for HarborHelm class attributes."""

    def test_chart(self):
        """Verify CHART constant."""
        self.assertEqual(HarborHelm.CHART,
                         app_constants.HELM_CHART_HARBOR)

    def test_service_name(self):
        """Verify SERVICE_NAME constant."""
        self.assertEqual(HarborHelm.SERVICE_NAME,
                         app_constants.HELM_APP_HARBOR)

    def test_supported_namespaces(self):
        """Verify harbor in SUPPORTED_NAMESPACES."""
        self.assertIn(app_constants.HELM_NS_HARBOR,
                      HarborHelm.SUPPORTED_NAMESPACES)

    def test_supported_app_namespaces_key(self):
        """Verify harbor key in SUPPORTED_APP_NAMESPACES."""
        self.assertIn(app_constants.HELM_APP_HARBOR,
                      HarborHelm.SUPPORTED_APP_NAMESPACES)

    def test_supported_app_namespaces_value(self):
        """Verify harbor ns in app namespaces."""
        ns_list = HarborHelm.SUPPORTED_APP_NAMESPACES[
            app_constants.HELM_APP_HARBOR]
        self.assertIn(app_constants.HELM_NS_HARBOR, ns_list)


class TestHarborHelmMethods(unittest.TestCase):
    """Tests for HarborHelm instance methods."""

    def _make(self, controllers=1, workers=1):
        """Create instance with mocked dbapi."""
        inst = HarborHelm.__new__(HarborHelm)
        inst.dbapi = mock.MagicMock()
        inst.dbapi.ihost_get_by_personality.side_effect = \
            lambda p: (['c'] * controllers if p == 'controller'
                       else ['w'] * workers)
        return inst

    def test_get_namespaces(self):
        """Verify get_namespaces returns SUPPORTED_NAMESPACES."""
        self.assertEqual(self._make().get_namespaces(),
                         HarborHelm.SUPPORTED_NAMESPACES)

    def test_host_count(self):
        """Verify host count calculation."""
        self.assertEqual(
            self._make(1, 2).get_master_worker_host_count(), 3)

    def test_overrides_multi_node(self):
        """Verify replicas=2 for multi-node."""
        result = self._make(1, 1).get_overrides(
            namespace=app_constants.HELM_NS_HARBOR)
        self.assertEqual(result['core']['replicas'], 2)
        self.assertEqual(result['portal']['replicas'], 2)
        self.assertEqual(result['jobservice']['replicas'], 2)
        self.assertEqual(result['registry']['replicas'], 2)
        self.assertEqual(result['trivy']['replicas'], 2)
        self.assertEqual(
            result['notary']['server']['replicas'], 2)
        self.assertEqual(
            result['notary']['signer']['replicas'], 2)

    def test_overrides_single_node(self):
        """Verify replicas=1 for single node."""
        result = self._make(1, 0).get_overrides(
            namespace=app_constants.HELM_NS_HARBOR)
        self.assertEqual(result['core']['replicas'], 1)
        self.assertEqual(result['portal']['replicas'], 1)

    def test_overrides_no_namespace(self):
        """Verify full dict when namespace is None."""
        result = self._make(0, 0).get_overrides(namespace=None)
        self.assertIn(app_constants.HELM_NS_HARBOR, result)

    def test_overrides_invalid_namespace(self):
        """Verify exception for invalid namespace."""
        with self.assertRaises(_FakeInvalidHelmNamespace):
            self._make(0, 0).get_overrides(namespace='bad')
