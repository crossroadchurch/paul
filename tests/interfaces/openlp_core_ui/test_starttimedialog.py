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
Package to test the openlp.core.ui package.
"""
from unittest import TestCase

from PyQt4 import QtCore, QtGui, QtTest

from openlp.core.common import Registry
from openlp.core.ui import starttimeform
from tests.interfaces import MagicMock, patch
from tests.helpers.testmixin import TestMixin


class TestStartTimeDialog(TestCase, TestMixin):

    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.setup_application()
        self.main_window = QtGui.QMainWindow()
        Registry().register('main_window', self.main_window)
        self.form = starttimeform.StartTimeForm()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.form
        del self.main_window

    def ui_defaults_test(self):
        """
        Test StartTimeDialog are defaults correct
        """
        self.assertEqual(self.form.hour_spin_box.minimum(), 0, 'The minimum hour should stay the same as the dialog')
        self.assertEqual(self.form.hour_spin_box.maximum(), 4, 'The maximum hour should stay the same as the dialog')
        self.assertEqual(self.form.minute_spin_box.minimum(), 0,
                         'The minimum minute should stay the same as the dialog')
        self.assertEqual(self.form.minute_spin_box.maximum(), 59,
                         'The maximum minute should stay the same as the dialog')
        self.assertEqual(self.form.second_spin_box.minimum(), 0,
                         'The minimum second should stay the same as the dialog')
        self.assertEqual(self.form.second_spin_box.maximum(), 59,
                         'The maximum second should stay the same as the dialog')
        self.assertEqual(self.form.hour_finish_spin_box.minimum(), 0,
                         'The minimum finish hour should stay the same as the dialog')
        self.assertEqual(self.form.hour_finish_spin_box.maximum(), 4,
                         'The maximum finish hour should stay the same as the dialog')
        self.assertEqual(self.form.minute_finish_spin_box.minimum(), 0,
                         'The minimum finish minute should stay the same as the dialog')
        self.assertEqual(self.form.minute_finish_spin_box.maximum(), 59,
                         'The maximum finish minute should stay the same as the dialog')
        self.assertEqual(self.form.second_finish_spin_box.minimum(), 0,
                         'The minimum finish second should stay the same as the dialog')
        self.assertEqual(self.form.second_finish_spin_box.maximum(), 59,
                         'The maximum finish second should stay the same as the dialog')

    def time_display_test(self):
        """
        Test StartTimeDialog display functionality
        """
        # GIVEN: A service item with with time
        mocked_serviceitem = MagicMock()
        mocked_serviceitem.start_time = 61
        mocked_serviceitem.end_time = 3701
        mocked_serviceitem.media_length = 3701

        # WHEN displaying the UI and pressing enter
        self.form.item = {'service_item': mocked_serviceitem}
        with patch('PyQt4.QtGui.QDialog.exec_'):
            self.form.exec_()
        ok_widget = self.form.button_box.button(self.form.button_box.Ok)
        QtTest.QTest.mouseClick(ok_widget, QtCore.Qt.LeftButton)

        # THEN the following input values are returned
        self.assertEqual(self.form.hour_spin_box.value(), 0)
        self.assertEqual(self.form.minute_spin_box.value(), 1)
        self.assertEqual(self.form.second_spin_box.value(), 1)
        self.assertEqual(self.form.item['service_item'].start_time, 61, 'The start time should stay the same')

        # WHEN displaying the UI, changing the time to 2min 3secs and pressing enter
        self.form.item = {'service_item': mocked_serviceitem}
        with patch('PyQt4.QtGui.QDialog.exec_'):
            self.form.exec_()
        self.form.minute_spin_box.setValue(2)
        self.form.second_spin_box.setValue(3)
        ok_widget = self.form.button_box.button(self.form.button_box.Ok)
        QtTest.QTest.mouseClick(ok_widget, QtCore.Qt.LeftButton)

        # THEN the following values are returned
        self.assertEqual(self.form.hour_spin_box.value(), 0)
        self.assertEqual(self.form.minute_spin_box.value(), 2)
        self.assertEqual(self.form.second_spin_box.value(), 3)
        self.assertEqual(self.form.item['service_item'].start_time, 123, 'The start time should have changed')
