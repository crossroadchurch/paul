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
The list of shortcuts within a dialog.
"""
from PyQt4 import QtCore, QtGui

from openlp.core.common import translate
from openlp.core.lib import build_icon
from openlp.core.lib.ui import create_button_box


class CaptureShortcutButton(QtGui.QPushButton):
    """
    A class to encapsulate a ``QPushButton``.
    """
    def __init__(self, *args):
        """
        Constructor
        """
        super(CaptureShortcutButton, self).__init__(*args)
        self.setCheckable(True)

    def keyPressEvent(self, event):
        """
        Block the ``Key_Space`` key, so that the button will not change the
        checked state.
        """
        if event.key() == QtCore.Qt.Key_Space and self.isChecked():
            # Ignore the event, so that the parent can take care of this.
            event.ignore()


class Ui_ShortcutListDialog(object):
    """
    The UI widgets for the shortcut dialog.
    """
    def setupUi(self, shortcutListDialog):
        """
        Set up the UI
        """
        shortcutListDialog.setObjectName('shortcutListDialog')
        shortcutListDialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        shortcutListDialog.resize(500, 438)
        self.shortcut_list_layout = QtGui.QVBoxLayout(shortcutListDialog)
        self.shortcut_list_layout.setObjectName('shortcut_list_layout')
        self.description_label = QtGui.QLabel(shortcutListDialog)
        self.description_label.setObjectName('description_label')
        self.description_label.setWordWrap(True)
        self.shortcut_list_layout.addWidget(self.description_label)
        self.tree_widget = QtGui.QTreeWidget(shortcutListDialog)
        self.tree_widget.setObjectName('tree_widget')
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setColumnCount(3)
        self.tree_widget.setColumnWidth(0, 250)
        self.shortcut_list_layout.addWidget(self.tree_widget)
        self.details_layout = QtGui.QGridLayout()
        self.details_layout.setObjectName('details_layout')
        self.details_layout.setContentsMargins(-1, 0, -1, -1)
        self.default_radio_button = QtGui.QRadioButton(shortcutListDialog)
        self.default_radio_button.setObjectName('default_radio_button')
        self.default_radio_button.setChecked(True)
        self.details_layout.addWidget(self.default_radio_button, 0, 0, 1, 1)
        self.custom_radio_button = QtGui.QRadioButton(shortcutListDialog)
        self.custom_radio_button.setObjectName('custom_radio_button')
        self.details_layout.addWidget(self.custom_radio_button, 1, 0, 1, 1)
        self.primary_layout = QtGui.QHBoxLayout()
        self.primary_layout.setObjectName('primary_layout')
        self.primary_push_button = CaptureShortcutButton(shortcutListDialog)
        self.primary_push_button.setObjectName('primary_push_button')
        self.primary_push_button.setMinimumSize(QtCore.QSize(84, 0))
        self.primary_push_button.setIcon(build_icon(':/system/system_configure_shortcuts.png'))
        self.primary_layout.addWidget(self.primary_push_button)
        self.clear_primary_button = QtGui.QToolButton(shortcutListDialog)
        self.clear_primary_button.setObjectName('clear_primary_button')
        self.clear_primary_button.setMinimumSize(QtCore.QSize(0, 16))
        self.clear_primary_button.setIcon(build_icon(':/system/clear_shortcut.png'))
        self.primary_layout.addWidget(self.clear_primary_button)
        self.details_layout.addLayout(self.primary_layout, 1, 1, 1, 1)
        self.alternate_layout = QtGui.QHBoxLayout()
        self.alternate_layout.setObjectName('alternate_layout')
        self.alternate_push_button = CaptureShortcutButton(shortcutListDialog)
        self.alternate_push_button.setObjectName('alternate_push_button')
        self.alternate_push_button.setIcon(build_icon(':/system/system_configure_shortcuts.png'))
        self.alternate_layout.addWidget(self.alternate_push_button)
        self.clear_alternate_button = QtGui.QToolButton(shortcutListDialog)
        self.clear_alternate_button.setObjectName('clear_alternate_button')
        self.clear_alternate_button.setIcon(build_icon(':/system/clear_shortcut.png'))
        self.alternate_layout.addWidget(self.clear_alternate_button)
        self.details_layout.addLayout(self.alternate_layout, 1, 2, 1, 1)
        self.primary_label = QtGui.QLabel(shortcutListDialog)
        self.primary_label.setObjectName('primary_label')
        self.details_layout.addWidget(self.primary_label, 0, 1, 1, 1)
        self.alternate_label = QtGui.QLabel(shortcutListDialog)
        self.alternate_label.setObjectName('alternate_label')
        self.details_layout.addWidget(self.alternate_label, 0, 2, 1, 1)
        self.shortcut_list_layout.addLayout(self.details_layout)
        self.button_box = create_button_box(shortcutListDialog, 'button_box', ['cancel', 'ok', 'defaults'])
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.shortcut_list_layout.addWidget(self.button_box)
        self.retranslateUi(shortcutListDialog)

    def retranslateUi(self, shortcutListDialog):
        """
        Translate the UI on the fly
        """
        shortcutListDialog.setWindowTitle(translate('OpenLP.ShortcutListDialog', 'Configure Shortcuts'))
        self.description_label.setText(
            translate('OpenLP.ShortcutListDialog', 'Select an action and click one of the buttons below to start '
                      'capturing a new primary or alternate shortcut, respectively.'))
        self.tree_widget.setHeaderLabels([translate('OpenLP.ShortcutListDialog', 'Action'),
                                         translate('OpenLP.ShortcutListDialog', 'Shortcut'),
                                         translate('OpenLP.ShortcutListDialog', 'Alternate')])
        self.default_radio_button.setText(translate('OpenLP.ShortcutListDialog', 'Default'))
        self.custom_radio_button.setText(translate('OpenLP.ShortcutListDialog', 'Custom'))
        self.primary_push_button.setToolTip(translate('OpenLP.ShortcutListDialog', 'Capture shortcut.'))
        self.alternate_push_button.setToolTip(translate('OpenLP.ShortcutListDialog', 'Capture shortcut.'))
        self.clear_primary_button.setToolTip(translate('OpenLP.ShortcutListDialog',
                                             'Restore the default shortcut of this action.'))
        self.clear_alternate_button.setToolTip(translate('OpenLP.ShortcutListDialog',
                                               'Restore the default shortcut of this action.'))
