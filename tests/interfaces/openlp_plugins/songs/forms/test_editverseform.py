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
Package to test the openlp.plugins.songs.forms.editverseform package.
"""
from unittest import TestCase

from PyQt4 import QtCore, QtGui, QtTest

from openlp.core.common import Registry
from openlp.plugins.songs.forms.editverseform import EditVerseForm
from tests.helpers.testmixin import TestMixin


class TestEditVerseForm(TestCase, TestMixin):
    """
    Test the EditVerseForm class
    """

    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.setup_application()
        self.main_window = QtGui.QMainWindow()
        Registry().register('main_window', self.main_window)
        self.form = EditVerseForm()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.form
        del self.main_window

    def ui_defaults_test(self):
        """
        Test the EditVerseForm defaults are correct
        """
        # GIVEN: An EditVerseForm instance
        # WHEN: The form is shown
        # THEN: The default value is correct
        self.assertEqual(self.form.verse_text_edit.toPlainText(), '', 'The verse edit box is empty.')

    def type_verse_text_tests(self):
        """
        Test that typing into the verse text edit box returns the correct text
        """
        # GIVEN: An instance of the EditVerseForm and some text to type
        text = 'Amazing Grace, how sweet the sound!'

        # WHEN: Some verse text is typed into the text edit
        QtTest.QTest.keyClicks(self.form.verse_text_edit, text)

        # THEN: The verse text edit should have the verse text in it
        self.assertEqual(text, self.form.verse_text_edit.toPlainText(),
                         'The verse text edit should have the typed out verse')

    def insert_verse_test(self):
        """
        Test that clicking the insert button inserts the correct verse marker
        """
        # GIVEN: An instance of the EditVerseForm
        # WHEN: The Insert button is clicked
        QtTest.QTest.mouseClick(self.form.insert_button, QtCore.Qt.LeftButton)

        # THEN: The verse text edit should have a Verse:1 in it
        self.assertIn('---[Verse:1]---', self.form.verse_text_edit.toPlainText(),
                      'The verse text edit should have a verse marker')

    def insert_verse_2_test(self):
        """
        Test that clicking the up button on the spin box and then clicking the insert button inserts the correct marker
        """
        # GIVEN: An instance of the EditVerseForm
        # WHEN: The spin button and then the Insert button are clicked
        QtTest.QTest.keyClick(self.form.verse_number_box, QtCore.Qt.Key_Up)
        QtTest.QTest.mouseClick(self.form.insert_button, QtCore.Qt.LeftButton)

        # THEN: The verse text edit should have a Verse:1 in it
        self.assertIn('---[Verse:2]---', self.form.verse_text_edit.toPlainText(),
                      'The verse text edit should have a "Verse 2" marker')

    def insert_chorus_test(self):
        """
        Test that clicking the verse type combo box and then clicking the insert button inserts the correct marker
        """
        # GIVEN: An instance of the EditVerseForm
        # WHEN: The verse type combo box and then the Insert button are clicked
        QtTest.QTest.keyClick(self.form.verse_type_combo_box, QtCore.Qt.Key_Down)
        QtTest.QTest.mouseClick(self.form.insert_button, QtCore.Qt.LeftButton)

        # THEN: The verse text edit should have a Chorus:1 in it
        self.assertIn('---[Chorus:1]---', self.form.verse_text_edit.toPlainText(),
                      'The verse text edit should have a "Chorus 1" marker')
