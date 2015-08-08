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

from openlp.core.common import UiStrings, translate
from openlp.core.lib import SpellTextEdit, build_icon
from openlp.core.lib.ui import create_button, create_button_box


class Ui_CustomSlideEditDialog(object):
    def setupUi(self, custom_slide_edit_dialog):
        custom_slide_edit_dialog.setObjectName('custom_slide_edit_dialog')
        custom_slide_edit_dialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        custom_slide_edit_dialog.resize(350, 300)
        self.dialog_layout = QtGui.QVBoxLayout(custom_slide_edit_dialog)
        self.slide_text_edit = SpellTextEdit(self)
        self.slide_text_edit.setObjectName('slide_text_edit')
        self.dialog_layout.addWidget(self.slide_text_edit)
        self.split_button = create_button(custom_slide_edit_dialog, 'splitButton', icon=':/general/general_add.png')
        self.insert_button = create_button(custom_slide_edit_dialog, 'insertButton',
                                           icon=':/general/general_add.png')
        self.button_box = create_button_box(custom_slide_edit_dialog, 'button_box', ['cancel', 'save'],
                                            [self.split_button, self.insert_button])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslateUi(custom_slide_edit_dialog)

    def retranslateUi(self, custom_slide_edit_dialog):
        custom_slide_edit_dialog.setWindowTitle(translate('CustomPlugin.EditVerseForm', 'Edit Slide'))
        self.split_button.setText(UiStrings().Split)
        self.split_button.setToolTip(UiStrings().SplitToolTip)
        self.insert_button.setText(translate('CustomPlugin.EditCustomForm', 'Insert Slide'))
        self.insert_button.setToolTip(translate('CustomPlugin.EditCustomForm',
                                                'Split a slide into two by inserting a slide splitter.'))
