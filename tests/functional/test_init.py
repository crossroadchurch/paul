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
Package to test the openlp.core.__init__ package.
"""
import os
from unittest import TestCase

from PyQt4 import QtCore, QtGui

from openlp.core import OpenLP, parse_options
from openlp.core.common import Settings

from tests.helpers.testmixin import TestMixin
from tests.functional import MagicMock, patch, call


TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources'))


class TestInit(TestCase, TestMixin):
    def setUp(self):
        self.build_settings()
        with patch('openlp.core.common.OpenLPMixin.__init__') as constructor:
            constructor.return_value = None
            self.openlp = OpenLP(list())

    def tearDown(self):
        self.destroy_settings()
        del self.openlp

    def event_test(self):
        """
        Test the reimplemented event method
        """
        # GIVEN: A file path and a QEvent.
        file_path = os.path.join(TEST_PATH, 'church.jpg')
        mocked_file_method = MagicMock(return_value=file_path)
        event = QtCore.QEvent(QtCore.QEvent.FileOpen)
        event.file = mocked_file_method

        # WHEN: Call the vent method.
        result = self.openlp.event(event)

        # THEN: The path should be inserted.
        self.assertTrue(result, "The method should have returned True.")
        mocked_file_method.assert_called_once_with()
        self.assertEqual(self.openlp.args[0], file_path, "The path should be in args.")

    @patch('openlp.core.is_macosx')
    def application_activate_event_test(self, mocked_is_macosx):
        """
        Test that clicking on the dock icon on Mac OS X restores the main window if it is minimized
        """
        # GIVEN: Mac OS X and an ApplicationActivate event
        mocked_is_macosx.return_value = True
        event = MagicMock()
        event.type.return_value = QtCore.QEvent.ApplicationActivate
        mocked_main_window = MagicMock()
        self.openlp.main_window = mocked_main_window

        # WHEN: The icon in the dock is clicked
        result = self.openlp.event(event)

        # THEN:
        self.assertTrue(result, "The method should have returned True.")
        # self.assertFalse(self.openlp.main_window.isMinimized())

    def backup_on_upgrade_first_install_test(self):
        """
        Test that we don't try to backup on a new install
        """
        # GIVEN: Mocked data version and OpenLP version which are the same
        old_install = False
        MOCKED_VERSION = {
            'full': '2.2.0-bzr000',
            'version': '2.2.0',
            'build': 'bzr000'
        }
        Settings().setValue('core/application version', '2.2.0')
        with patch('openlp.core.get_application_version') as mocked_get_application_version,\
                patch('openlp.core.QtGui.QMessageBox.question') as mocked_question:
            mocked_get_application_version.return_value = MOCKED_VERSION
            mocked_question.return_value = QtGui.QMessageBox.No

            # WHEN: We check if a backup should be created
            self.openlp.backup_on_upgrade(old_install)

            # THEN: It should not ask if we want to create a backup
            self.assertEqual(Settings().value('core/application version'), '2.2.0', 'Version should be the same!')
            self.assertEqual(mocked_question.call_count, 0, 'No question should have been asked!')

    def backup_on_upgrade_test(self):
        """
        Test that we try to backup on a new install
        """
        # GIVEN: Mocked data version and OpenLP version which are different
        old_install = True
        MOCKED_VERSION = {
            'full': '2.2.0-bzr000',
            'version': '2.2.0',
            'build': 'bzr000'
        }
        Settings().setValue('core/application version', '2.0.5')
        with patch('openlp.core.get_application_version') as mocked_get_application_version,\
                patch('openlp.core.QtGui.QMessageBox.question') as mocked_question:
            mocked_get_application_version.return_value = MOCKED_VERSION
            mocked_question.return_value = QtGui.QMessageBox.No

            # WHEN: We check if a backup should be created
            self.openlp.backup_on_upgrade(old_install)

            # THEN: It should ask if we want to create a backup
            self.assertEqual(Settings().value('core/application version'), '2.2.0', 'Version should be upgraded!')
            self.assertEqual(mocked_question.call_count, 1, 'A question should have been asked!')

    @patch(u'openlp.core.OptionParser')
    def parse_options_test(self, MockedOptionParser):
        """
        Test that parse_options sets up OptionParser correctly and parses the options given
        """
        # GIVEN: A list of valid options and a mocked out OptionParser object
        options = ['-e', '-l', 'debug', '-pd', '-s', 'style', 'extra', 'qt', 'args']
        mocked_parser = MagicMock()
        MockedOptionParser.return_value = mocked_parser
        expected_calls = [
            call('-e', '--no-error-form', dest='no_error_form', action='store_true',
                 help='Disable the error notification form.'),
            call('-l', '--log-level', dest='loglevel', default='warning', metavar='LEVEL',
                 help='Set logging to LEVEL level. Valid values are "debug", "info", "warning".'),
            call('-p', '--portable', dest='portable', action='store_true',
                 help='Specify if this should be run as a portable app, off a USB flash drive (not implemented).'),
            call('-d', '--dev-version', dest='dev_version', action='store_true',
                 help='Ignore the version file and pull the version directly from Bazaar'),
            call('-s', '--style', dest='style', help='Set the Qt4 style (passed directly to Qt4).')
        ]

        # WHEN: Calling parse_options
        parse_options(options)

        # THEN: A tuple should be returned with the parsed options and left over options
        MockedOptionParser.assert_called_with(usage='Usage: %prog [options] [qt-options]')
        self.assertEquals(expected_calls, mocked_parser.add_option.call_args_list)
        mocked_parser.parse_args.assert_called_with(options)

    @patch(u'openlp.core.OptionParser')
    def parse_options_from_sys_argv_test(self, MockedOptionParser):
        """
        Test that parse_options sets up OptionParser correctly and parses sys.argv
        """
        # GIVEN: A list of valid options and a mocked out OptionParser object
        mocked_parser = MagicMock()
        MockedOptionParser.return_value = mocked_parser
        expected_calls = [
            call('-e', '--no-error-form', dest='no_error_form', action='store_true',
                 help='Disable the error notification form.'),
            call('-l', '--log-level', dest='loglevel', default='warning', metavar='LEVEL',
                 help='Set logging to LEVEL level. Valid values are "debug", "info", "warning".'),
            call('-p', '--portable', dest='portable', action='store_true',
                 help='Specify if this should be run as a portable app, off a USB flash drive (not implemented).'),
            call('-d', '--dev-version', dest='dev_version', action='store_true',
                 help='Ignore the version file and pull the version directly from Bazaar'),
            call('-s', '--style', dest='style', help='Set the Qt4 style (passed directly to Qt4).')
        ]

        # WHEN: Calling parse_options
        parse_options([])

        # THEN: A tuple should be returned with the parsed options and left over options
        MockedOptionParser.assert_called_with(usage='Usage: %prog [options] [qt-options]')
        self.assertEquals(expected_calls, mocked_parser.add_option.call_args_list)
        mocked_parser.parse_args.assert_called_with()
