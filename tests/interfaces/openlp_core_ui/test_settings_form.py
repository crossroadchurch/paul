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
Package to test the openlp.core.lib.settingsform package.
"""
from unittest import TestCase

from PyQt4 import QtCore, QtTest

from openlp.core.common import Registry
from openlp.core.ui import settingsform
from openlp.core.lib import ScreenList
from tests.interfaces import MagicMock, patch
from tests.helpers.testmixin import TestMixin

SCREEN = {
    'primary': False,
    'number': 1,
    'size': QtCore.QRect(0, 0, 1024, 768)
}


class TestSettingsForm(TestCase, TestMixin):
    """
    Test the PluginManager class
    """

    def setUp(self):
        """
        Some pre-test setup required.
        """
        self.dummy1 = MagicMock()
        self.dummy2 = MagicMock()
        self.dummy3 = MagicMock()
        self.desktop = MagicMock()
        self.setup_application()
        self.desktop.primaryScreen.return_value = SCREEN['primary']
        self.desktop.screenCount.return_value = SCREEN['number']
        self.desktop.screenGeometry.return_value = SCREEN['size']
        self.screens = ScreenList.create(self.desktop)
        Registry.create()
        self.form = settingsform.SettingsForm()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.form

    def basic_cancel_test(self):
        """
        Test running the settings form and pressing Cancel
        """
        # GIVEN: An initial form

        # WHEN displaying the UI and pressing cancel
        with patch('PyQt4.QtGui.QDialog.reject') as mocked_reject:
            cancel_widget = self.form.button_box.button(self.form.button_box.Cancel)
            QtTest.QTest.mouseClick(cancel_widget, QtCore.Qt.LeftButton)

            # THEN the dialog reject should have been called
            assert mocked_reject.call_count == 1, 'The QDialog.reject should have been called'

    def basic_accept_test(self):
        """
        Test running the settings form and pressing Ok
        """
        # GIVEN: An initial form

        # WHEN displaying the UI and pressing Ok
        with patch('PyQt4.QtGui.QDialog.accept') as mocked_accept:
            ok_widget = self.form.button_box.button(self.form.button_box.Ok)
            QtTest.QTest.mouseClick(ok_widget, QtCore.Qt.LeftButton)

            # THEN the dialog reject should have been called
            assert mocked_accept.call_count == 1, 'The QDialog.accept should have been called'

    def basic_register_test(self):
        """
        Test running the settings form and adding a single function
        """
        # GIVEN: An initial form add a register function
        self.form.register_post_process('function1')

        # WHEN displaying the UI and pressing Ok
        with patch('PyQt4.QtGui.QDialog.accept'):
            ok_widget = self.form.button_box.button(self.form.button_box.Ok)
            QtTest.QTest.mouseClick(ok_widget, QtCore.Qt.LeftButton)

            # THEN the processing stack should be empty
            assert len(self.form.processes) == 0, 'The one requested process should have been removed from the stack'

    def register_multiple_functions_test(self):
        """
        Test running the settings form and adding multiple functions
        """
        # GIVEN: Registering a single function
        self.form.register_post_process('function1')

        # WHEN testing the processing stack
        # THEN the processing stack should have one item
        assert len(self.form.processes) == 1, 'The one requested process should have been added to the stack'

        # GIVEN: Registering a new function
        self.form.register_post_process('function2')

        # WHEN testing the processing stack
        # THEN the processing stack should have two items
        assert len(self.form.processes) == 2, 'The two requested processes should have been added to the stack'

        # GIVEN: Registering a process for the second time
        self.form.register_post_process('function1')

        # WHEN testing the processing stack
        # THEN the processing stack should still have two items
        assert len(self.form.processes) == 2, 'No new processes should have been added to the stack'

    def register_image_manager_trigger_test_one(self):
        """
        Test the triggering of the image manager rebuild event from image background change
        """
        # GIVEN: Three functions registered to be call
        Registry().register_function('images_config_updated', self.dummy1)
        Registry().register_function('config_screen_changed', self.dummy2)
        Registry().register_function('images_regenerate', self.dummy3)

        # WHEN: The Images have been changed and the form submitted
        self.form.register_post_process('images_config_updated')
        self.form.accept()

        # THEN: images_regenerate should have been added.
        assert self.dummy1.call_count == 1, 'dummy1 should have been called once'
        assert self.dummy2.call_count == 0, 'dummy2 should not have been called at all'
        assert self.dummy3.call_count == 1, 'dummy3 should have been called once'

    def register_image_manager_trigger_test_two(self):
        """
        Test the triggering of the image manager rebuild event from screen dimension change
        """
        # GIVEN: Three functions registered to be call
        Registry().register_function('images_config_updated', self.dummy1)
        Registry().register_function('config_screen_changed', self.dummy2)
        Registry().register_function('images_regenerate', self.dummy3)

        # WHEN: The Images have been changed and the form submitted
        self.form.register_post_process('config_screen_changed')
        self.form.accept()

        # THEN: images_regenerate should have been added.
        assert self.dummy1.call_count == 0, 'dummy1 should not have been called at all'
        assert self.dummy2.call_count == 1, 'dummy2 should have been called once'
        assert self.dummy3.call_count == 1, 'dummy3 should have been called once'

    def register_image_manager_trigger_test_three(self):
        """
        Test the triggering of the image manager rebuild event from image background change and a change to the
        screen dimension.
        """
        # GIVEN: Three functions registered to be call
        Registry().register_function('images_config_updated', self.dummy1)
        Registry().register_function('config_screen_changed', self.dummy2)
        Registry().register_function('images_regenerate', self.dummy3)

        # WHEN: The Images have been changed and the form submitted
        self.form.register_post_process('config_screen_changed')
        self.form.register_post_process('images_config_updated')
        self.form.accept()

        # THEN: Images_regenerate should have been added.
        assert self.dummy1.call_count == 1, 'dummy1 should have been called once'
        assert self.dummy2.call_count == 1, 'dummy2 should have been called once'
        assert self.dummy3.call_count == 1, 'dummy3 should have been called once'
