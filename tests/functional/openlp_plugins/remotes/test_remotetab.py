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
This module contains tests for the lib submodule of the Remotes plugin.
"""
import os
import re
from unittest import TestCase

from PyQt4 import QtGui

from openlp.core.common import Settings
from openlp.plugins.remotes.lib.remotetab import RemoteTab
from tests.functional import patch
from tests.helpers.testmixin import TestMixin

__default_settings__ = {
    'remotes/twelve hour': True,
    'remotes/port': 4316,
    'remotes/https port': 4317,
    'remotes/https enabled': False,
    'remotes/user id': 'openlp',
    'remotes/password': 'password',
    'remotes/authentication enabled': False,
    'remotes/ip address': '0.0.0.0',
    'remotes/thumbnails': True
}
ZERO_URL = '0.0.0.0'
TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'resources'))


class TestRemoteTab(TestCase, TestMixin):
    """
    Test the functions in the :mod:`lib` module.
    """
    def setUp(self):
        """
        Create the UI
        """
        self.setup_application()
        self.build_settings()
        Settings().extend_default_settings(__default_settings__)
        self.parent = QtGui.QMainWindow()
        self.form = RemoteTab(self.parent, 'Remotes', None, None)

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.parent
        del self.form
        self.destroy_settings()

    def get_ip_address_default_test(self):
        """
        Test the get_ip_address function with ZERO_URL
        """
        # WHEN: the default ip address is given
        ip_address = self.form.get_ip_address(ZERO_URL)
        # THEN: the default ip address will be returned
        self.assertTrue(re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip_address),
                        'The return value should be a valid ip address')

    def get_ip_address_with_ip_test(self):
        """
        Test the get_ip_address function with given ip address
        """
        # GIVEN: A mocked location
        # GIVEN: An ip address
        given_ip = '192.168.1.1'
        # WHEN: the default ip address is given
        ip_address = self.form.get_ip_address(given_ip)
        # THEN: the default ip address will be returned
        self.assertEqual(ip_address, given_ip, 'The return value should be %s' % given_ip)

    def set_basic_urls_test(self):
        """
        Test the set_urls function with standard defaults
        """
        # GIVEN: A mocked location
        with patch('openlp.core.common.Settings') as mocked_class, \
                patch('openlp.core.utils.AppLocation.get_directory') as mocked_get_directory, \
                patch('openlp.core.common.check_directory_exists') as mocked_check_directory_exists, \
                patch('openlp.core.common.applocation.os') as mocked_os:
            # GIVEN: A mocked out Settings class and a mocked out AppLocation.get_directory()
            mocked_settings = mocked_class.return_value
            mocked_settings.contains.return_value = False
            mocked_get_directory.return_value = 'test/dir'
            mocked_check_directory_exists.return_value = True
            mocked_os.path.normpath.return_value = 'test/dir'

            # WHEN: when the set_urls is called having reloaded the form.
            self.form.load()
            self.form.set_urls()
            # THEN: the following screen values should be set
            self.assertEqual(self.form.address_edit.text(), ZERO_URL, 'The default URL should be set on the screen')
            self.assertEqual(self.form.https_settings_group_box.isEnabled(), False,
                             'The Https box should not be enabled')
            self.assertEqual(self.form.https_settings_group_box.isChecked(), False,
                             'The Https checked box should note be Checked')
            self.assertEqual(self.form.user_login_group_box.isChecked(), False,
                             'The authentication box should not be enabled')

    def set_certificate_urls_test(self):
        """
        Test the set_urls function with certificate available
        """
        # GIVEN: A mocked location
        with patch('openlp.core.common.Settings') as mocked_class, \
                patch('openlp.core.utils.AppLocation.get_directory') as mocked_get_directory, \
                patch('openlp.core.common.check_directory_exists') as mocked_check_directory_exists, \
                patch('openlp.core.common.applocation.os') as mocked_os:
            # GIVEN: A mocked out Settings class and a mocked out AppLocation.get_directory()
            mocked_settings = mocked_class.return_value
            mocked_settings.contains.return_value = False
            mocked_get_directory.return_value = TEST_PATH
            mocked_check_directory_exists.return_value = True
            mocked_os.path.normpath.return_value = TEST_PATH

            # WHEN: when the set_urls is called having reloaded the form.
            self.form.load()
            self.form.set_urls()
            # THEN: the following screen values should be set
            self.assertEqual(self.form.http_settings_group_box.isEnabled(), True,
                             'The Http group box should be enabled')
            self.assertEqual(self.form.https_settings_group_box.isChecked(), False,
                             'The Https checked box should be Checked')
            self.assertEqual(self.form.https_settings_group_box.isEnabled(), True,
                             'The Https box should be enabled')
