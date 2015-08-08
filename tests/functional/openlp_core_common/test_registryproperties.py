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
Test the registry properties
"""
from unittest import TestCase

from openlp.core.common import Registry, RegistryProperties
from tests.functional import MagicMock


class TestRegistryProperties(TestCase, RegistryProperties):
    """
    Test the functions in the ThemeManager module
    """
    def setUp(self):
        """
        Create the Register
        """
        Registry.create()

    def no_application_test(self):
        """
        Test property if no registry value assigned
        """
        # GIVEN an Empty Registry
        # WHEN there is no Application
        # THEN the application should be none
        self.assertEqual(self.application, None, 'The application value should be None')

    def application_test(self):
        """
        Test property if registry value assigned
        """
        # GIVEN an Empty Registry
        application = MagicMock()
        # WHEN the application is registered
        Registry().register('application', application)
        # THEN the application should be none
        self.assertEqual(self.application, application, 'The application value should match')
