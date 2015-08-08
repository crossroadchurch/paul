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
Package to test the openlp.core.ui.formattingtagsform package.
"""
from unittest import TestCase

from tests.functional import MagicMock, patch, call

from openlp.core.ui.formattingtagform import FormattingTagForm

# TODO: Tests Still TODO
# __init__
# exec_
# on_saved_clicked
# _reloadTable


class TestFormattingTagForm(TestCase):

    def setUp(self):
        """
        Mock out stuff for all the tests
        """
        self.setup_patcher = patch('openlp.core.ui.formattingtagform.FormattingTagForm._setup')
        self.setup_patcher.start()

    def tearDown(self):
        """
        Remove the mocks
        """
        self.setup_patcher.stop()

    def on_row_selected_test(self):
        """
        Test that the appropriate actions are preformed when on_row_selected is called
        """
        # GIVEN: An instance of the Formatting Tag Form and a mocked delete_button
        form = FormattingTagForm(None)
        form.delete_button = MagicMock()

        # WHEN: on_row_selected is called
        form.on_row_selected()

        # THEN: setEnabled and should have been called on delete_button
        form.delete_button.setEnabled.assert_called_with(True)

    def on_new_clicked_test(self):
        """
        Test that clicking the Add a new tag button does the right thing
        """

        # GIVEN: A formatting tag form and a mocked out tag table widget
        form = FormattingTagForm(None)
        form.tag_table_widget = MagicMock()
        row_count = 5
        form.tag_table_widget.rowCount.return_value = row_count

        # WHEN: on_new_clicked is run (i.e. the Add new button was clicked)
        with patch('openlp.core.ui.formattingtagform.QtGui.QTableWidgetItem') as MockedQTableWidgetItem:
            mocked_table_widget = MagicMock()
            MockedQTableWidgetItem.return_value = mocked_table_widget
            form.on_new_clicked()

            # THEN: A new row should be added to the table
            form.tag_table_widget.rowCount.assert_called_with()
            form.tag_table_widget.insertRow.assert_called_with(row_count)
            expected_set_item_calls = [
                call(row_count, 0, mocked_table_widget),
                call(row_count, 1, mocked_table_widget),
                call(row_count, 2, mocked_table_widget),
                call(row_count, 3, mocked_table_widget)
            ]
            self.assertEqual(expected_set_item_calls, form.tag_table_widget.setItem.call_args_list,
                             'setItem should have been called correctly')
            form.tag_table_widget.resizeRowsToContents.assert_called_with()
            form.tag_table_widget.scrollToBottom.assert_called_with()
            form.tag_table_widget.selectRow.assert_called_with(row_count)
