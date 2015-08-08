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
Package to test the openlp.core.ui.firsttimeform package.
"""
import os
import socket
import tempfile
import urllib
from unittest import TestCase

from openlp.core.common import Registry
from openlp.core.ui.firsttimeform import FirstTimeForm

from tests.functional import MagicMock, patch
from tests.helpers.testmixin import TestMixin

FAKE_CONFIG = b"""
[general]
base url = http://example.com/frw/
[songs]
directory = songs
[bibles]
directory = bibles
[themes]
directory = themes
"""

FAKE_BROKEN_CONFIG = b"""
[general]
base url = http://example.com/frw/
[songs]
directory = songs
[bibles]
directory = bibles
"""

FAKE_INVALID_CONFIG = b"""
<html>
<head><title>This is not a config file</title></head>
<body>Some text</body>
</html>
"""


class TestFirstTimeForm(TestCase, TestMixin):

    def setUp(self):
        self.setup_application()
        self.app.setApplicationVersion('0.0')
        # Set up a fake "set_normal_cursor" method since we're not dealing with an actual OpenLP application object
        self.app.set_normal_cursor = lambda: None
        self.app.process_events = lambda: None
        Registry.create()
        Registry().register('application', self.app)
        self.tempfile = os.path.join(tempfile.gettempdir(), 'testfile')

    def tearDown(self):
        if os.path.isfile(self.tempfile):
            os.remove(self.tempfile)

    def initialise_test(self):
        """
        Test if we can intialise the FirstTimeForm
        """
        # GIVEN: A First Time Wizard and an expected screen object
        frw = FirstTimeForm(None)
        expected_screens = MagicMock()

        # WHEN: The First Time Wizard is initialised
        frw.initialize(expected_screens)

        # THEN: The screens should be set up, and the default values initialised
        self.assertEqual(expected_screens, frw.screens, 'The screens should be correct')
        self.assertTrue(frw.web_access, 'The default value of self.web_access should be True')
        self.assertFalse(frw.was_cancelled, 'The default value of self.was_cancelled should be False')
        self.assertListEqual([], frw.theme_screenshot_threads, 'The list of threads should be empty')
        self.assertListEqual([], frw.theme_screenshot_workers, 'The list of workers should be empty')
        self.assertFalse(frw.has_run_wizard, 'has_run_wizard should be False')

    def set_defaults_test(self):
        """
        Test that the default values are set when set_defaults() is run
        """
        # GIVEN: An initialised FRW and a whole lot of stuff mocked out
        frw = FirstTimeForm(None)
        frw.initialize(MagicMock())
        with patch.object(frw, 'restart') as mocked_restart, \
                patch.object(frw, 'cancel_button') as mocked_cancel_button, \
                patch.object(frw, 'no_internet_finish_button') as mocked_no_internet_finish_btn, \
                patch.object(frw, 'currentIdChanged') as mocked_currentIdChanged, \
                patch.object(Registry, 'register_function') as mocked_register_function, \
                patch('openlp.core.ui.firsttimeform.Settings') as MockedSettings, \
                patch('openlp.core.ui.firsttimeform.gettempdir') as mocked_gettempdir, \
                patch('openlp.core.ui.firsttimeform.check_directory_exists') as mocked_check_directory_exists, \
                patch.object(frw.application, 'set_normal_cursor') as mocked_set_normal_cursor:
            mocked_settings = MagicMock()
            mocked_settings.value.return_value = True
            MockedSettings.return_value = mocked_settings
            mocked_gettempdir.return_value = 'temp'
            expected_temp_path = os.path.join('temp', 'openlp')

            # WHEN: The set_defaults() method is run
            frw.set_defaults()

            # THEN: The default values should have been set
            mocked_restart.assert_called_with()
            self.assertEqual('http://openlp.org/files/frw/', frw.web, 'The default URL should be set')
            mocked_cancel_button.clicked.connect.assert_called_with(frw.on_cancel_button_clicked)
            mocked_no_internet_finish_btn.clicked.connect.assert_called_with(frw.on_no_internet_finish_button_clicked)
            mocked_currentIdChanged.connect.assert_called_with(frw.on_current_id_changed)
            mocked_register_function.assert_called_with('config_screen_changed', frw.update_screen_list_combo)
            mocked_no_internet_finish_btn.setVisible.assert_called_with(False)
            mocked_settings.value.assert_called_with('core/has run wizard')
            mocked_gettempdir.assert_called_with()
            mocked_check_directory_exists.assert_called_with(expected_temp_path)

    def update_screen_list_combo_test(self):
        """
        Test that the update_screen_list_combo() method works correctly
        """
        # GIVEN: A mocked Screen() object and an initialised First Run Wizard and a mocked display_combo_box
        expected_screen_list = ['Screen 1', 'Screen 2']
        mocked_screens = MagicMock()
        mocked_screens.get_screen_list.return_value = expected_screen_list
        frw = FirstTimeForm(None)
        frw.initialize(mocked_screens)
        with patch.object(frw, 'display_combo_box') as mocked_display_combo_box:
            mocked_display_combo_box.count.return_value = 2

            # WHEN: update_screen_list_combo() is called
            frw.update_screen_list_combo()

            # THEN: The combobox should have been updated
            mocked_display_combo_box.clear.assert_called_with()
            mocked_screens.get_screen_list.assert_called_with()
            mocked_display_combo_box.addItems.assert_called_with(expected_screen_list)
            mocked_display_combo_box.count.assert_called_with()
            mocked_display_combo_box.setCurrentIndex.assert_called_with(1)

    def on_cancel_button_clicked_test(self):
        """
        Test that the cancel button click slot shuts down the threads correctly
        """
        # GIVEN: A FRW, some mocked threads and workers (that isn't quite done) and other mocked stuff
        frw = FirstTimeForm(None)
        frw.initialize(MagicMock())
        mocked_worker = MagicMock()
        mocked_thread = MagicMock()
        mocked_thread.isRunning.side_effect = [True, False]
        frw.theme_screenshot_workers.append(mocked_worker)
        frw.theme_screenshot_threads.append(mocked_thread)
        with patch('openlp.core.ui.firsttimeform.time') as mocked_time, \
                patch.object(frw.application, 'set_normal_cursor') as mocked_set_normal_cursor:

            # WHEN: on_cancel_button_clicked() is called
            frw.on_cancel_button_clicked()

            # THEN: The right things should be called in the right order
            self.assertTrue(frw.was_cancelled, 'The was_cancelled property should have been set to True')
            mocked_worker.set_download_canceled.assert_called_with(True)
            mocked_thread.isRunning.assert_called_with()
            self.assertEqual(2, mocked_thread.isRunning.call_count, 'isRunning() should have been called twice')
            mocked_time.sleep.assert_called_with(0.1)
            self.assertEqual(1, mocked_time.sleep.call_count, 'sleep() should have only been called once')
            mocked_set_normal_cursor.assert_called_with()

    def broken_config_test(self):
        """
        Test if we can handle an config file with missing data
        """
        # GIVEN: A mocked get_web_page, a First Time Wizard, an expected screen object, and a mocked broken config file
        with patch('openlp.core.ui.firsttimeform.get_web_page') as mocked_get_web_page:
            first_time_form = FirstTimeForm(None)
            first_time_form.initialize(MagicMock())
            mocked_get_web_page.return_value.read.return_value = FAKE_BROKEN_CONFIG

            # WHEN: The First Time Wizard is downloads the config file
            first_time_form._download_index()

            # THEN: The First Time Form should not have web access
            self.assertFalse(first_time_form.web_access, 'There should not be web access with a broken config file')

    def invalid_config_test(self):
        """
        Test if we can handle an config file in invalid format
        """
        # GIVEN: A mocked get_web_page, a First Time Wizard, an expected screen object, and a mocked invalid config file
        with patch('openlp.core.ui.firsttimeform.get_web_page') as mocked_get_web_page:
            first_time_form = FirstTimeForm(None)
            first_time_form.initialize(MagicMock())
            mocked_get_web_page.return_value.read.return_value = FAKE_INVALID_CONFIG

            # WHEN: The First Time Wizard is downloads the config file
            first_time_form._download_index()

            # THEN: The First Time Form should not have web access
            self.assertFalse(first_time_form.web_access, 'There should not be web access with an invalid config file')

    @patch('openlp.core.ui.firsttimeform.get_web_page')
    @patch('openlp.core.ui.firsttimeform.QtGui.QMessageBox')
    def network_error_test(self, mocked_message_box, mocked_get_web_page):
        """
        Test we catch a network error in First Time Wizard - bug 1409627
        """
        # GIVEN: Initial setup and mocks
        first_time_form = FirstTimeForm(None)
        first_time_form.initialize(MagicMock())
        mocked_get_web_page.side_effect = urllib.error.HTTPError(url='http//localhost',
                                                                 code=407,
                                                                 msg='Network proxy error',
                                                                 hdrs=None,
                                                                 fp=None)
        # WHEN: the First Time Wizard calls to get the initial configuration
        first_time_form._download_index()

        # THEN: the critical_error_message_box should have been called
        self.assertEquals(mocked_message_box.mock_calls[1][1][0], 'Network Error 407',
                          'first_time_form should have caught Network Error')

    @patch('openlp.core.ui.firsttimeform.urllib.request.urlopen')
    def socket_timeout_test(self, mocked_urlopen):
        """
        Test socket timeout gets caught
        """
        # GIVEN: Mocked urlopen to fake a network disconnect in the middle of a download
        first_time_form = FirstTimeForm(None)
        first_time_form.initialize(MagicMock())
        mocked_urlopen.side_effect = socket.timeout()

        # WHEN: Attempt to retrieve a file
        first_time_form.url_get_file(url='http://localhost/test', f_path=self.tempfile)

        # THEN: socket.timeout should have been caught
        # NOTE: Test is if $tmpdir/tempfile is still there, then test fails since ftw deletes bad downloaded files
        self.assertFalse(os.path.exists(self.tempfile), 'FTW url_get_file should have caught socket.timeout')
