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

from PyQt4 import QtGui

from openlp.core.lib import translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.songs.forms.authorsdialog import Ui_AuthorsDialog


class AuthorsForm(QtGui.QDialog, Ui_AuthorsDialog):
    """
    Class to control the Maintenance of Authors Dialog
    """
    def __init__(self, parent=None):
        """
        Set up the screen and common data
        """
        super(AuthorsForm, self).__init__(parent)
        self.setupUi(self)
        self.auto_display_name = False
        self.first_name_edit.textEdited.connect(self.on_first_name_edited)
        self.last_name_edit.textEdited.connect(self.on_last_name_edited)

    def exec_(self, clear=True):
        """
        Execute the dialog.

        :param clear: Clear the form fields before displaying the dialog.
        """
        if clear:
            self.first_name_edit.clear()
            self.last_name_edit.clear()
            self.display_edit.clear()
        self.first_name_edit.setFocus()
        return QtGui.QDialog.exec_(self)

    def on_first_name_edited(self, display_name):
        """
        Slot for when the first name is edited.

        When the first name is edited and the setting to automatically create a display name is True, then try to create
        a display name from the first and last names.

        :param display_name: The text from the first_name_edit widget.
        """
        if not self.auto_display_name:
            return
        if self.last_name_edit.text():
            display_name = display_name + ' ' + self.last_name_edit.text()
        self.display_edit.setText(display_name)

    def on_last_name_edited(self, display_name):
        """
        Slot for when the last name is edited.

        When the last name is edited and the setting to automatically create a display name is True, then try to create
        a display name from the first and last names.

        :param display_name: The text from the last_name_edit widget.
        """
        if not self.auto_display_name:
            return
        if self.first_name_edit.text():
            display_name = self.first_name_edit.text() + ' ' + display_name
        self.display_edit.setText(display_name)

    def accept(self):
        """
        Override the QDialog's accept() method to do some validation before the dialog can be closed.
        """
        if not self.first_name_edit.text():
            critical_error_message_box(
                message=translate('SongsPlugin.AuthorsForm', 'You need to type in the first name of the author.'))
            self.first_name_edit.setFocus()
            return False
        elif not self.last_name_edit.text():
            critical_error_message_box(
                message=translate('SongsPlugin.AuthorsForm', 'You need to type in the last name of the author.'))
            self.last_name_edit.setFocus()
            return False
        elif not self.display_edit.text():
            if critical_error_message_box(
                message=translate('SongsPlugin.AuthorsForm',
                                  'You have not set a display name for the author, combine the first and last names?'),
                    parent=self, question=True) == QtGui.QMessageBox.Yes:
                self.display_edit.setText(self.first_name_edit.text() + ' ' + self.last_name_edit.text())
                return QtGui.QDialog.accept(self)
            else:
                self.display_edit.setFocus()
                return False
        else:
            return QtGui.QDialog.accept(self)

    def _get_first_name(self):
        """
        Get the value of the first name from the UI widget.
        """
        return self.first_name_edit.text()

    def _set_first_name(self, value):
        """
        Set the value of the first name in the UI widget.
        """
        self.first_name_edit.setText(value)

    first_name = property(_get_first_name, _set_first_name)

    def _get_last_name(self):
        """
        Get the value of the last name from the UI widget.
        """
        return self.last_name_edit.text()

    def _set_last_name(self, value):
        """
        Set the value of the last name in the UI widget.
        """
        self.last_name_edit.setText(value)

    last_name = property(_get_last_name, _set_last_name)

    def _get_display_name(self):
        return self.display_edit.text()

    def _set_display_name(self, value):
        self.display_edit.setText(value)

    display_name = property(_get_display_name, _set_display_name)
