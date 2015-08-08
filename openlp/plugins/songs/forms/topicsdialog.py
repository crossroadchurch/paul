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

from openlp.core.lib import translate, build_icon
from openlp.core.lib.ui import create_button_box


class Ui_TopicsDialog(object):
    """
    The user interface for the topics dialog.
    """
    def setupUi(self, topics_dialog):
        """
        Set up the user interface for the topics dialog.
        """
        topics_dialog.setObjectName('topics_dialog')
        topics_dialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        topics_dialog.resize(300, 10)
        self.dialog_layout = QtGui.QVBoxLayout(topics_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.name_layout = QtGui.QFormLayout()
        self.name_layout.setObjectName('name_layout')
        self.name_label = QtGui.QLabel(topics_dialog)
        self.name_label.setObjectName('name_label')
        self.name_edit = QtGui.QLineEdit(topics_dialog)
        self.name_edit.setObjectName('name_edit')
        self.name_label.setBuddy(self.name_edit)
        self.name_layout.addRow(self.name_label, self.name_edit)
        self.dialog_layout.addLayout(self.name_layout)
        self.button_box = create_button_box(topics_dialog, 'button_box', ['cancel', 'save'])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslateUi(topics_dialog)
        topics_dialog.setMaximumHeight(topics_dialog.sizeHint().height())

    def retranslateUi(self, topics_dialog):
        """
        Translate the UI on the fly.
        """
        topics_dialog.setWindowTitle(translate('SongsPlugin.TopicsForm', 'Topic Maintenance'))
        self.name_label.setText(translate('SongsPlugin.TopicsForm', 'Topic name:'))
