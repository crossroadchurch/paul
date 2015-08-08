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
Module to test the EditCustomSlideForm.
"""
from unittest import TestCase

from PyQt4 import QtGui

from openlp.core.common import Registry
from openlp.plugins.custom.forms.editcustomslideform import EditCustomSlideForm
from tests.interfaces import MagicMock, patch
from tests.helpers.testmixin import TestMixin


class TestEditCustomSlideForm(TestCase, TestMixin):
    """
    Test the EditCustomSlideForm.
    """
    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.setup_application()
        self.main_window = QtGui.QMainWindow()
        Registry().register('main_window', self.main_window)
        self.form = EditCustomSlideForm()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.form
        del self.main_window

    def basic_test(self):
        """
        Test if the dialog is correctly set up.
        """
        # GIVEN: A mocked QDialog.exec_() method
        with patch('PyQt4.QtGui.QDialog.exec_') as mocked_exec:
            # WHEN: Show the dialog.
            self.form.exec_()

            # THEN: The dialog should be empty.
            assert self.form.slide_text_edit.toPlainText() == '', 'There should not be any text in the text editor.'

    def set_text_test(self):
        """
        Test the set_text() method.
        """
        # GIVEN: A mocked QDialog.exec_() method
        with patch('PyQt4.QtGui.QDialog.exec_') as mocked_exec:
            mocked_set_focus = MagicMock()
            self.form.slide_text_edit.setFocus = mocked_set_focus
            wanted_text = 'THIS TEXT SHOULD BE SHOWN.'

            # WHEN: Show the dialog and set the text.
            self.form.exec_()
            self.form.set_text(wanted_text)

            # THEN: The dialog should show the text.
            assert self.form.slide_text_edit.toPlainText() == wanted_text, \
                'The text editor should show the correct text.'

            # THEN: The dialog should have focus.
            mocked_set_focus.assert_called_with()
