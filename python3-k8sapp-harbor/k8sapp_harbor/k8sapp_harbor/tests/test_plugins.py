#
# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from k8sapp_harbor.common import constants as app_constants
from sysinv.tests.helm.test_helm import HelmOperatorTestSuiteMixin

from sysinv.tests.db import base as dbbase


class K8SAppHarborAppMixin(object):
    app_name = app_constants.HELM_APP_HARBOR
    path_name = app_name + '.tgz'

    def setUp(self):
        super(K8SAppHarborAppMixin, self).setUp()


# Test Configuration:
# - Controller
# - IPv6
# - Ceph Storage
# - harbor app
class K8SAppHarborControllerTestCase(K8SAppHarborAppMixin,
                                         dbbase.BaseIPv6Mixin,
                                         dbbase.BaseCephStorageBackendMixin,
                                         HelmOperatorTestSuiteMixin,
                                         dbbase.ControllerHostTestCase):
    pass


# Test Configuration:
# - AIO
# - IPv4
# - Ceph Storage
# - harbor app
class K8SAppHarborAIOTestCase(K8SAppHarborAppMixin,
                                  dbbase.BaseCephStorageBackendMixin,
                                  HelmOperatorTestSuiteMixin,
                                  dbbase.AIOSimplexHostTestCase):
    pass

