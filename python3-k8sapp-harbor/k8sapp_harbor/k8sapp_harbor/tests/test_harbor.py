# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from k8sapp_harbor.tests import test_plugins

from sysinv.db import api as dbapi
from sysinv.tests.db import base as dbbase
from sysinv.tests.db import utils as dbutils
from sysinv.tests.helm import base


class HarborTestCase(test_plugins.K8SAppHarborAppMixin,
                     base.HelmTestCaseMixin):

    def setUp(self):
        super(HarborTestCase, self).setUp()
        self.app = dbutils.create_test_app(name='harbor')
        self.dbapi = dbapi.get_instance()


class HarborTestCaseDummy(HarborTestCase,
                          dbbase.ProvisionedControllerHostTestCase):

    def test_dummy(self):
        pass
