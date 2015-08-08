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
Module to test the :mod:`~openlp.core.common.historycombobox` module.
"""

from unittest import TestCase

from PyQt4 import QtCore, QtGui, QtTest

from openlp.core.common import Registry
from openlp.core.common import HistoryComboBox
from tests.helpers.testmixin import TestMixin
from tests.interfaces import MagicMock, patch


class TestHistoryComboBox(TestCase, TestMixin):
    def setUp(self):
        """
        Some pre-test setup required.
        """
        Registry.create()
        self.setup_application()
        self.main_window = QtGui.QMainWindow()
        Registry().register('main_window', self.main_window)
        self.combo = HistoryComboBox(self.main_window)

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.combo
        del self.main_window

    def get_items_test(self):
        """
        Test the getItems() method
        """
        # GIVEN: The combo.

        # WHEN: Add two items.
        self.combo.addItem('test1')
        self.combo.addItem('test2')

        # THEN: The list of items should contain both strings.
        self.assertEqual(self.combo.getItems(), ['test1', 'test2'])
