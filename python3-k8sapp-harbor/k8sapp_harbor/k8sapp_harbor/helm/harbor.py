#
# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sysinv.common import constants
from sysinv.common import exception
from sysinv.helm import base

from k8sapp_harbor.common import constants as app_constants
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class HarborHelm(base.BaseHelm):
    """Class to encapsulate helm operations for the harbor chart"""

    SUPPORTED_NAMESPACES = base.BaseHelm.SUPPORTED_NAMESPACES + \
        [app_constants.HELM_NS_HARBOR]
    SUPPORTED_APP_NAMESPACES = {
        app_constants.HELM_APP_HARBOR:
            base.BaseHelm.SUPPORTED_NAMESPACES +
            [app_constants.HELM_NS_HARBOR],
    }

    CHART = app_constants.HELM_CHART_HARBOR

    SERVICE_NAME = app_constants.HELM_APP_HARBOR

    def get_namespaces(self):
        return self.SUPPORTED_NAMESPACES

    def get_master_worker_host_count(self):
        controller = len(self.dbapi.ihost_get_by_personality(constants.CONTROLLER))
        worker = len(self.dbapi.ihost_get_by_personality(constants.WORKER))
        return controller + worker

    def get_overrides(self, namespace=None):
        if self.get_master_worker_host_count() >= 2:
            overrides = {
                app_constants.HELM_NS_HARBOR: {
                    'core': {
                            'replicas': 2,
                    },
                    'portal': {
                            'replicas': 2,
                    },
                    'notary': {
                        'server': {
                            'replicas': 2,
                        },
                        'signer': {
                            'replicas': 2,
                        },
                    },
                    'jobservice': {
                        'replicas': 2,
                    },
                    'registry': {
                        'replicas': 2,
                    },
                    'trivy': {
                        'replicas': 2,
                    },
                }
            }
        else:
            overrides = {
                app_constants.HELM_NS_HARBOR: {
                    'core': {
                        'replicas': 1,
                    },
                    'portal': {
                        'replicas': 1,
                    },
                    'notary': {
                        'server': {
                            'replicas': 1,
                        },
                        'signer': {
                            'replicas': 1,
                        },
                    },
                    'jobservice': {
                        'replicas': 1,
                    },
                    'registry': {
                        'replicas': 1,
                    },
                    'trivy': {
                        'replicas': 1,
                    },
                }
            }

        if namespace in self.SUPPORTED_NAMESPACES:
            return overrides[namespace]
        elif namespace:
            raise exception.InvalidHelmNamespace(chart=self.CHART,
                                                 namespace=namespace)
        else:
            return overrides
