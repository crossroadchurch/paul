# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2015 OpenLP Developers                                   #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 2 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
#                                                                             #
# You should have received a copy of the GNU General Public License along     #
# with this program; if not, write to the Free Software Foundation, Inc., 59  #
# Temple Place, Suite 330, Boston, MA 02111-1307 USA                          #
###############################################################################
"""
Package to test the openlp.core.common package.
"""
import os
from unittest import TestCase

from openlp.core.common import RegistryMixin, Registry

TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '..', 'resources'))


class TestRegistryMixin(TestCase):

    def registry_mixin_missing_test(self):
        """
        Test the registry creation and its usage
        """
        # GIVEN: A new registry
        Registry.create()

        # WHEN: I create a new class
        mock_1 = Test1()

        # THEN: The following methods are missing
        self.assertEqual(len(Registry().functions_list), 0), 'The function should not be in the dict anymore.'

    def registry_mixin_present_test(self):
        """
        Test the registry creation and its usage
        """
        # GIVEN: A new registry
        Registry.create()

        # WHEN: I create a new class
        mock_2 = Test2()

        # THEN: The following bootstrap methods should be present
        self.assertEqual(len(Registry().functions_list), 2), 'The bootstrap functions should be in the dict.'


class Test1(object):
    def __init__(self):
        pass


class Test2(RegistryMixin):
    def __init__(self):
        super(Test2, self).__init__(None)
