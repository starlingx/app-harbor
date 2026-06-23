#
# Copyright (c) 2026 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

"""Unit tests for k8sapp_harbor.common.constants module."""

import unittest

from k8sapp_harbor.common import constants as app_constants


class TestConstants(unittest.TestCase):
    """Tests for harbor application constants."""

    def test_helm_app_harbor_value(self):
        """Verify HELM_APP_HARBOR constant."""
        self.assertEqual(app_constants.HELM_APP_HARBOR, 'harbor')

    def test_helm_ns_harbor_value(self):
        """Verify HELM_NS_HARBOR constant."""
        self.assertEqual(app_constants.HELM_NS_HARBOR, 'harbor')

    def test_helm_chart_harbor_value(self):
        """Verify HELM_CHART_HARBOR constant."""
        self.assertEqual(app_constants.HELM_CHART_HARBOR, 'harbor')

    def test_helm_component_label_harbor_value(self):
        """Verify HELM_COMPONENT_LABEL_HARBOR constant."""
        self.assertEqual(
            app_constants.HELM_COMPONENT_LABEL_HARBOR,
            'app.starlingx.io/component'
        )

    def test_constants_are_strings(self):
        """Verify all constants are string type."""
        self.assertIsInstance(app_constants.HELM_APP_HARBOR, str)
        self.assertIsInstance(app_constants.HELM_NS_HARBOR, str)
        self.assertIsInstance(app_constants.HELM_CHART_HARBOR, str)
        self.assertIsInstance(
            app_constants.HELM_COMPONENT_LABEL_HARBOR, str
        )

    def test_constants_not_empty(self):
        """Verify no constants are empty strings."""
        self.assertTrue(app_constants.HELM_APP_HARBOR)
        self.assertTrue(app_constants.HELM_NS_HARBOR)
        self.assertTrue(app_constants.HELM_CHART_HARBOR)
        self.assertTrue(app_constants.HELM_COMPONENT_LABEL_HARBOR)

    def test_module_import(self):
        """Verify the constants module can be imported."""
        from k8sapp_harbor.common import constants  # noqa: F811
        self.assertIsNotNone(constants)
