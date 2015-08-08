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
The :mod:`~openlp.core.common.historycombobox` module contains the HistoryComboBox widget
"""

from PyQt4 import QtCore, QtGui


class HistoryComboBox(QtGui.QComboBox):
    """
    The :class:`~openlp.core.common.historycombobox.HistoryComboBox` widget emulates the QLineEdit ``returnPressed``
    signal for when the :kbd:`Enter` or :kbd:`Return` keys are pressed, and saves anything that is typed into the edit
    box into its list.
    """
    returnPressed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        """
        Initialise the combo box, setting duplicates to False and the insert policy to insert items at the top.

        :param parent: The parent widget
        """
        super().__init__(parent)
        self.setDuplicatesEnabled(False)
        self.setEditable(True)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.setInsertPolicy(QtGui.QComboBox.InsertAtTop)

    def keyPressEvent(self, event):
        """
        Override the inherited keyPressEvent method to emit the ``returnPressed`` signal and to save the current text to
        the dropdown list.

        :param event: The keyboard event
        """
        # Handle Enter and Return ourselves
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            # Emit the returnPressed signal
            self.returnPressed.emit()
            # Save the current text to the dropdown list
            if self.currentText() and self.findText(self.currentText()) == -1:
                self.insertItem(0, self.currentText())
        # Let the parent handle any keypress events
        super().keyPressEvent(event)

    def focusOutEvent(self, event):
        """
        Override the inherited focusOutEvent to save the current text to the dropdown list.

        :param event: The focus event
        """
        # Save the current text to the dropdown list
        if self.currentText() and self.findText(self.currentText()) == -1:
            self.insertItem(0, self.currentText())
        # Let the parent handle any keypress events
        super().focusOutEvent(event)

    def getItems(self):
        """
        Get all the items from the history

        :return: A list of strings
        """
        return [self.itemText(i) for i in range(self.count())]
