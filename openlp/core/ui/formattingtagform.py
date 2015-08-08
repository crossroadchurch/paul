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
The :mod:`formattingtagform` provides an Tag Edit facility. The Base set are protected and included each time loaded.
Custom tags can be defined and saved. The Custom Tag arrays are saved in a json string so QSettings works on them.
Base Tags cannot be changed.
"""

from PyQt4 import QtGui

from openlp.core.common import translate
from openlp.core.lib import FormattingTags
from openlp.core.ui.formattingtagdialog import Ui_FormattingTagDialog
from openlp.core.ui.formattingtagcontroller import FormattingTagController


class EditColumn(object):
    """
    Hides the magic numbers for the table columns
    """
    Description = 0
    Tag = 1
    StartHtml = 2
    EndHtml = 3


class FormattingTagForm(QtGui.QDialog, Ui_FormattingTagDialog, FormattingTagController):
    """
    The :class:`FormattingTagForm` manages the settings tab .
    """
    def __init__(self, parent):
        """
        Constructor
        """
        super(FormattingTagForm, self).__init__(parent)
        self.setupUi(self)
        self._setup()

    def _setup(self):
        """
        Set up the class. This method is mocked out by the tests.
        """
        self.services = FormattingTagController()
        self.tag_table_widget.itemSelectionChanged.connect(self.on_row_selected)
        self.new_button.clicked.connect(self.on_new_clicked)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.tag_table_widget.currentCellChanged.connect(self.on_current_cell_changed)
        self.button_box.rejected.connect(self.close)
        # Forces reloading of tags from openlp configuration.
        FormattingTags.load_tags()
        self.is_deleting = False
        self.reloading = False

    def exec_(self):
        """
        Load Display and set field state.
        """
        # Create initial copy from master
        self._reloadTable()
        return QtGui.QDialog.exec_(self)

    def on_row_selected(self):
        """
        Table Row selected so display items and set field state.
        """
        self.delete_button.setEnabled(True)

    def on_new_clicked(self):
        """
        Add a new tag to edit list and select it for editing.
        """
        new_row = self.tag_table_widget.rowCount()
        self.tag_table_widget.insertRow(new_row)
        self.tag_table_widget.setItem(new_row, 0, QtGui.QTableWidgetItem(translate('OpenLP.FormattingTagForm',
                                                                                   'New Tag %d' % new_row)))
        self.tag_table_widget.setItem(new_row, 1, QtGui.QTableWidgetItem('n%d' % new_row))
        self.tag_table_widget.setItem(new_row, 2,
                                      QtGui.QTableWidgetItem(translate('OpenLP.FormattingTagForm', '<HTML here>')))
        self.tag_table_widget.setItem(new_row, 3, QtGui.QTableWidgetItem(''))
        self.tag_table_widget.resizeRowsToContents()
        self.tag_table_widget.scrollToBottom()
        self.tag_table_widget.selectRow(new_row)

    def on_delete_clicked(self):
        """
        Delete selected custom row.
        """
        selected = self.tag_table_widget.currentRow()
        if selected != -1:
            self.is_deleting = True
            self.tag_table_widget.removeRow(selected)

    def accept(self):
        """
        Update Custom Tag details if not duplicate and save the data.
        """
        count = 0
        self.services.pre_save()
        while count < self.tag_table_widget.rowCount():
            error = self.services.validate_for_save(self.tag_table_widget.item(count, 0).text(),
                                                    self.tag_table_widget.item(count, 1).text(),
                                                    self.tag_table_widget.item(count, 2).text(),
                                                    self.tag_table_widget.item(count, 3).text())
            if error:
                QtGui.QMessageBox.warning(self, translate('OpenLP.FormattingTagForm', 'Validation Error'), error,
                                          QtGui.QMessageBox.Ok)
                self.tag_table_widget.selectRow(count)
                return
            count += 1
        self.services.save_tags()
        QtGui.QDialog.accept(self)

    def _reloadTable(self):
        """
        Reset List for loading.
        """
        self.reloading = True
        self.tag_table_widget_read.clearContents()
        self.tag_table_widget_read.setRowCount(0)
        self.tag_table_widget.clearContents()
        self.tag_table_widget.setRowCount(0)
        self.new_button.setEnabled(True)
        self.delete_button.setEnabled(False)
        for line_number, html in enumerate(FormattingTags.get_html_tags()):
            if html['protected']:
                line = self.tag_table_widget_read.rowCount()
                self.tag_table_widget_read.setRowCount(line + 1)
                self.tag_table_widget_read.setItem(line, 0, QtGui.QTableWidgetItem(html['desc']))
                self.tag_table_widget_read.setItem(line, 1, QtGui.QTableWidgetItem(self._strip(html['start tag'])))
                self.tag_table_widget_read.setItem(line, 2, QtGui.QTableWidgetItem(html['start html']))
                self.tag_table_widget_read.setItem(line, 3, QtGui.QTableWidgetItem(html['end html']))
                self.tag_table_widget_read.resizeRowsToContents()
            else:
                line = self.tag_table_widget.rowCount()
                self.tag_table_widget.setRowCount(line + 1)
                self.tag_table_widget.setItem(line, 0, QtGui.QTableWidgetItem(html['desc']))
                self.tag_table_widget.setItem(line, 1, QtGui.QTableWidgetItem(self._strip(html['start tag'])))
                self.tag_table_widget.setItem(line, 2, QtGui.QTableWidgetItem(html['start html']))
                self.tag_table_widget.setItem(line, 3, QtGui.QTableWidgetItem(html['end html']))
                self.tag_table_widget.resizeRowsToContents()
                # Permanent (persistent) tags do not have this key
                html['temporary'] = False
        self.reloading = False

    def on_current_cell_changed(self, cur_row, cur_col, pre_row, pre_col):
        """
        This function processes all user edits in the table. It is called on each cell change.
        """
        if self.is_deleting:
            self.is_deleting = False
            return
        if self.reloading:
            return
        # only process for editable rows
        if self.tag_table_widget.item(pre_row, 0):
            item = self.tag_table_widget.item(pre_row, pre_col)
            text = item.text()
            errors = None
            if pre_col is EditColumn.Description:
                if not text:
                    errors = translate('OpenLP.FormattingTagForm', 'Description is missing')
            elif pre_col is EditColumn.Tag:
                if not text:
                    errors = translate('OpenLP.FormattingTagForm', 'Tag is missing')
            elif pre_col is EditColumn.StartHtml:
                # HTML edited
                item = self.tag_table_widget.item(pre_row, 3)
                end_html = item.text()
                errors, tag = self.services.start_tag_changed(text, end_html)
                if tag:
                    self.tag_table_widget.setItem(pre_row, 3, QtGui.QTableWidgetItem(tag))
                self.tag_table_widget.resizeRowsToContents()
            elif pre_col is EditColumn.EndHtml:
                # HTML edited
                item = self.tag_table_widget.item(pre_row, 2)
                start_html = item.text()
                errors, tag = self.services.end_tag_changed(start_html, text)
                if tag:
                    self.tag_table_widget.setItem(pre_row, 3, QtGui.QTableWidgetItem(tag))
            if errors:
                QtGui.QMessageBox.warning(self, translate('OpenLP.FormattingTagForm', 'Validation Error'), errors,
                                          QtGui.QMessageBox.Ok)
            self.tag_table_widget.resizeRowsToContents()
