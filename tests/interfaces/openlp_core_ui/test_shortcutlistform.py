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
Package to test the openlp.core.ui.shortcutform package.
"""
from unittest import TestCase

from PyQt4 import QtCore, QtGui, QtTest

from openlp.core.common import Registry
from openlp.core.ui.shortcutlistform import ShortcutListForm
from tests.interfaces import patch
from tests.helpers.testmixin import TestMixin


class TestShortcutform(TestCase, TestMixin):

    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.setup_application()
        self.main_window = QtGui.QMainWindow()
        Registry().register('main_window', self.main_window)
        self.form = ShortcutListForm()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.form
        del self.main_window

    def adjust_button_test(self):
        """
        Test the _adjust_button() method
        """
        # GIVEN: A button.
        button = QtGui.QPushButton()
        checked = True
        enabled = True
        text = "new!"

        # WHEN: Call the method.
        with patch('PyQt4.QtGui.QPushButton.setChecked') as mocked_check_method:
            self.form._adjust_button(button, checked, enabled, text)

            # THEN: The button should be changed.
            self.assertEqual(button.text(), text, "The text should match.")
            mocked_check_method.assert_called_once_with(True)
            self.assertEqual(button.isEnabled(), enabled, "The button should be disabled.")
