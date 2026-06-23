#
# Copyright (c) 2026 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

"""Unit tests for k8sapp_harbor.lifecycle.lifecycle_harbor module."""

import unittest
from unittest import mock

from k8sapp_harbor.common import constants as app_constants
from tests.unit.conftest import (
    create_sysinv_mock_modules,
    patch_and_cleanup,
)


class _FakeBase(object):
    """Fake AppLifecycleOperator."""
    def app_lifecycle_actions(self, context, conductor_obj,
                              app_op, app, hook_info):
        """Default no-op."""


class _LifecycleMissingInfo(Exception):
    """Fake exception."""
    def __init__(self, msg=''):
        super(_LifecycleMissingInfo, self).__init__(msg)


class _AppApplyFailure(Exception):
    """Fake exception."""
    def __init__(self, **kw):
        super(_AppApplyFailure, self).__init__()


class _HelmOverrideNotFound(Exception):
    """Fake exception."""


_LC = mock.MagicMock()
_LC.APP_LIFECYCLE_TYPE_FLUXCD_REQUEST = 'fluxcd-request'
_LC.APP_LIFECYCLE_TYPE_OPERATION = 'operation'
_LC.APP_LIFECYCLE_TIMING_POST = 'post'
_LC.APP_LIFECYCLE_TIMING_PRE = 'pre'
_LC.EXTRA = 'extra'
_LC.RETURN_CODE = 'return_code'
_LC_MOD = mock.MagicMock()
_LC_MOD.LifecycleConstants = _LC
_BASE_MOD = mock.MagicMock()
_BASE_MOD.AppLifecycleOperator = _FakeBase
_EXC_MOD = mock.MagicMock()
_EXC_MOD.LifecycleMissingInfo = _LifecycleMissingInfo
_EXC_MOD.ApplicationApplyFailure = _AppApplyFailure
_EXC_MOD.HelmOverrideNotFound = _HelmOverrideNotFound
_K8S_MOD = mock.MagicMock()
_K8S_MOD.KUBERNETES_ADMIN_CONF = '/etc/kubernetes/admin.conf'
_CUTILS = mock.MagicMock()
_CONST_MOD = mock.MagicMock()
_CONST_MOD.APP_APPLY_OP = 'apply'
_CONST_MOD.APP_REMOVE_OP = 'remove'
_COMMON_MOD = mock.MagicMock()
_COMMON_MOD.constants = _CONST_MOD
_COMMON_MOD.exception = _EXC_MOD
_COMMON_MOD.kubernetes = _K8S_MOD
_COMMON_MOD.utils = _CUTILS
_HELM_MOD = mock.MagicMock()
_HELM_MOD.lifecycle_base = _BASE_MOD
_HELM_MOD.lifecycle_constants = _LC_MOD
_SYSINV_MOD = mock.MagicMock()
_SYSINV_MOD.common = _COMMON_MOD
_SYSINV_MOD.helm = _HELM_MOD

_MODS = create_sysinv_mock_modules({
    'sysinv': _SYSINV_MOD, 'sysinv.common': _COMMON_MOD,
    'sysinv.common.constants': _CONST_MOD,
    'sysinv.common.exception': _EXC_MOD,
    'sysinv.common.kubernetes': _K8S_MOD,
    'sysinv.common.utils': _CUTILS,
    'sysinv.helm': _HELM_MOD,
    'sysinv.helm.lifecycle_base': _BASE_MOD,
    'sysinv.helm.lifecycle_constants': _LC_MOD,
})
patch_and_cleanup(_MODS, 'k8sapp_harbor.lifecycle.')

from k8sapp_harbor.lifecycle import lifecycle_harbor  # noqa: E402
HarborOp = lifecycle_harbor.HarborAppLifecycleOperator


def _hook(ltype, operation, timing):
    """Create mock hook_info."""
    hook = mock.MagicMock()
    hook.lifecycle_type = ltype
    hook.operation = operation
    hook.relative_timing = timing
    return hook


class TestDispatch(unittest.TestCase):
    """Tests for app_lifecycle_actions dispatch."""

    def _op(self):
        return HarborOp.__new__(HarborOp)

    def test_post_apply(self):
        """Verify post_apply dispatched."""
        with mock.patch.object(HarborOp, 'post_apply') as pa:
            self._op().app_lifecycle_actions(
                None, None, mock.MagicMock(), mock.MagicMock(),
                _hook('fluxcd-request', 'apply', 'post'))
            pa.assert_called_once()

    def test_pre_remove(self):
        """Verify pre_remove dispatched."""
        with mock.patch.object(HarborOp, 'pre_remove') as pr:
            self._op().app_lifecycle_actions(
                None, None, mock.MagicMock(), mock.MagicMock(),
                _hook('operation', 'remove', 'pre'))
            pr.assert_called_once()

    def test_post_remove(self):
        """Verify post_remove dispatched."""
        with mock.patch.object(HarborOp, 'post_remove') as pr:
            self._op().app_lifecycle_actions(
                None, None, mock.MagicMock(), mock.MagicMock(),
                _hook('operation', 'remove', 'post'))
            pr.assert_called_once()

    def test_fallback(self):
        """Verify super called for unknown hook."""
        self._op().app_lifecycle_actions(
            None, None, mock.MagicMock(), mock.MagicMock(),
            _hook('x', 'x', 'x'))


class TestPostApply(unittest.TestCase):
    """Tests for post_apply."""

    def _op(self):
        return HarborOp.__new__(HarborOp)

    def test_missing_extra(self):
        """Verify raises when EXTRA missing."""
        hook = mock.MagicMock()
        hook.__contains__ = mock.Mock(return_value=False)
        with self.assertRaises(_LifecycleMissingInfo):
            self._op().post_apply(
                mock.MagicMock(), mock.MagicMock(), hook)

    def test_missing_return_code(self):
        """Verify raises when RETURN_CODE missing."""
        hook = mock.MagicMock()
        hook.__contains__ = mock.Mock(return_value=True)
        extra = mock.MagicMock()
        extra.__contains__ = mock.Mock(return_value=False)
        hook.__getitem__ = mock.Mock(return_value=extra)
        with self.assertRaises(_LifecycleMissingInfo):
            self._op().post_apply(
                mock.MagicMock(), mock.MagicMock(), hook)

    def test_apply_failure(self):
        """Verify retry on failed apply."""
        hook = mock.MagicMock()
        hook.__contains__ = mock.Mock(return_value=True)
        hook.__getitem__ = mock.Mock(
            return_value={'return_code': False})
        app_op = mock.MagicMock()
        app_op.is_app_aborted.return_value = False
        app = mock.MagicMock()
        app.name = 'harbor'
        with self.assertRaises(_AppApplyFailure):
            self._op().post_apply(app_op, app, hook)

    def test_success_default_label(self):
        """Verify default application label."""
        hook = mock.MagicMock()
        hook.__contains__ = mock.Mock(return_value=True)
        hook.__getitem__ = mock.Mock(
            return_value={'return_code': True})
        app_op = mock.MagicMock()
        app = mock.MagicMock()
        app.name = 'harbor'
        db_app = mock.MagicMock()
        db_app.id = 1
        app_op._dbapi.kube_app_get.return_value = db_app
        ns = mock.MagicMock()
        ns.metadata.labels = {}
        client = \
            app_op._kube._get_kubernetesclient_core.return_value
        client.read_namespace.return_value = ns
        with mock.patch.object(
                HarborOp, '_get_helm_user_overrides',
                return_value=''), \
             mock.patch.object(HarborOp, '_delete_harbor_pods'):
            self._op().post_apply(app_op, app, hook)
        lbl = app_constants.HELM_COMPONENT_LABEL_HARBOR
        self.assertEqual(
            ns.metadata.labels.get(lbl), 'application')


class TestPreRemove(unittest.TestCase):
    """Tests for pre_remove."""

    def setUp(self):
        _CUTILS.trycmd.reset_mock()

    def test_pre_remove(self):
        """Verify pre_remove calls trycmd."""
        _CUTILS.trycmd.return_value = ('', '')
        op = HarborOp.__new__(HarborOp)
        app = mock.MagicMock()
        app.name = 'harbor'
        app.sync_fluxcd_manifest = '/tmp/m'
        op.pre_remove(app)
        self.assertTrue(_CUTILS.trycmd.called)


class TestHelmOverrides(unittest.TestCase):
    """Tests for _get_helm_user_overrides."""

    def test_found(self):
        """Verify existing override returned."""
        op = HarborOp.__new__(HarborOp)
        dbapi = mock.MagicMock()
        ov = mock.MagicMock()
        ov.user_overrides = 'k: v'
        dbapi.helm_override_get.return_value = ov
        self.assertEqual(
            op._get_helm_user_overrides(dbapi, 1), 'k: v')

    def test_not_found(self):
        """Verify override created when missing."""
        op = HarborOp.__new__(HarborOp)
        dbapi = mock.MagicMock()
        dbapi.helm_override_get.side_effect = \
            _HelmOverrideNotFound()
        new = mock.MagicMock()
        new.user_overrides = None
        dbapi.helm_override_create.return_value = new
        self.assertEqual(
            op._get_helm_user_overrides(dbapi, 1), '')

    def test_none(self):
        """Verify None returns empty string."""
        op = HarborOp.__new__(HarborOp)
        dbapi = mock.MagicMock()
        ov = mock.MagicMock()
        ov.user_overrides = None
        dbapi.helm_override_get.return_value = ov
        self.assertEqual(
            op._get_helm_user_overrides(dbapi, 1), '')


class TestDeletePods(unittest.TestCase):
    """Tests for _delete_harbor_pods."""

    def test_deletes(self):
        """Verify pods deleted."""
        op = HarborOp.__new__(HarborOp)
        app_op = mock.MagicMock()
        client = mock.MagicMock()
        pod = mock.MagicMock()
        pod.metadata.name = 'p1'
        pods = mock.MagicMock()
        pods.items = [pod]
        client.list_namespaced_pod.return_value = pods
        op._delete_harbor_pods(app_op, client)
        app_op._kube.kube_delete_pod.assert_called_once()

    def test_empty(self):
        """Verify no error with no pods."""
        op = HarborOp.__new__(HarborOp)
        app_op = mock.MagicMock()
        client = mock.MagicMock()
        pods = mock.MagicMock()
        pods.items = []
        client.list_namespaced_pod.return_value = pods
        op._delete_harbor_pods(app_op, client)
        app_op._kube.kube_delete_pod.assert_not_called()
