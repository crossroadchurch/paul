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

from openlp.core.common import translate
from openlp.core.lib import build_icon
from openlp.core.lib.ui import create_button_box


class Ui_LanguageDialog(object):
    def setupUi(self, language_dialog):
        language_dialog.setObjectName('language_dialog')
        language_dialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        language_dialog.resize(400, 165)
        self.language_layout = QtGui.QVBoxLayout(language_dialog)
        self.language_layout.setSpacing(8)
        self.language_layout.setMargin(8)
        self.language_layout.setObjectName('language_layout')
        self.bible_label = QtGui.QLabel(language_dialog)
        self.bible_label.setObjectName('bible_label')
        self.language_layout.addWidget(self.bible_label)
        self.info_label = QtGui.QLabel(language_dialog)
        self.info_label.setWordWrap(True)
        self.info_label.setObjectName('info_label')
        self.language_layout.addWidget(self.info_label)
        self.language_h_box_layout = QtGui.QHBoxLayout()
        self.language_h_box_layout.setSpacing(8)
        self.language_h_box_layout.setObjectName('language_h_box_layout')
        self.language_label = QtGui.QLabel(language_dialog)
        self.language_label.setObjectName('language_label')
        self.language_h_box_layout.addWidget(self.language_label)
        self.language_combo_box = QtGui.QComboBox(language_dialog)
        size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.language_combo_box.sizePolicy().hasHeightForWidth())
        self.language_combo_box.setSizePolicy(size_policy)
        self.language_combo_box.setObjectName('language_combo_box')
        self.language_h_box_layout.addWidget(self.language_combo_box)
        self.language_layout.addLayout(self.language_h_box_layout)
        self.button_box = create_button_box(language_dialog, 'button_box', ['cancel', 'ok'])
        self.language_layout.addWidget(self.button_box)

        self.retranslateUi(language_dialog)

    def retranslateUi(self, language_dialog):
        language_dialog.setWindowTitle(translate('BiblesPlugin.LanguageDialog', 'Select Language'))
        self.bible_label.setText(translate('BiblesPlugin.LanguageDialog', ''))
        self.info_label.setText(
            translate('BiblesPlugin.LanguageDialog',
                      'OpenLP is unable to determine the language of this translation of the Bible. Please select '
                      'the language from the list below.'))
        self.language_label.setText(translate('BiblesPlugin.LanguageDialog', 'Language:'))
