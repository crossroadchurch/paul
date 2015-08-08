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
The layout of the theme
"""
from PyQt4 import QtGui

from openlp.core.common import translate
from openlp.core.lib import build_icon
from openlp.core.lib.ui import create_button_box


class Ui_ThemeLayoutDialog(object):
    """
    The layout of the theme
    """
    def setupUi(self, themeLayoutDialog):
        """
        Set up the UI
        """
        themeLayoutDialog.setObjectName('themeLayoutDialogDialog')
        themeLayoutDialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        self.preview_layout = QtGui.QVBoxLayout(themeLayoutDialog)
        self.preview_layout.setObjectName('preview_layout')
        self.preview_area = QtGui.QWidget(themeLayoutDialog)
        self.preview_area.setObjectName('preview_area')
        self.preview_area_layout = QtGui.QGridLayout(self.preview_area)
        self.preview_area_layout.setMargin(0)
        self.preview_area_layout.setColumnStretch(0, 1)
        self.preview_area_layout.setRowStretch(0, 1)
        self.preview_area_layout.setObjectName('preview_area_layout')
        self.theme_display_label = QtGui.QLabel(self.preview_area)
        self.theme_display_label.setFrameShape(QtGui.QFrame.Box)
        self.theme_display_label.setScaledContents(True)
        self.theme_display_label.setObjectName('theme_display_label')
        self.preview_area_layout.addWidget(self.theme_display_label)
        self.preview_layout.addWidget(self.preview_area)
        self.main_colour_label = QtGui.QLabel(self.preview_area)
        self.main_colour_label.setObjectName('main_colour_label')
        self.preview_layout.addWidget(self.main_colour_label)
        self.footer_colour_label = QtGui.QLabel(self.preview_area)
        self.footer_colour_label.setObjectName('footer_colour_label')
        self.preview_layout.addWidget(self.footer_colour_label)
        self.button_box = create_button_box(themeLayoutDialog, 'button_box', ['ok'])
        self.preview_layout.addWidget(self.button_box)
        self.retranslateUi(themeLayoutDialog)

    def retranslateUi(self, themeLayoutDialog):
        """
        Translate the UI on the fly
        """
        themeLayoutDialog.setWindowTitle(translate('OpenLP.StartTimeForm', 'Theme Layout'))
        self.main_colour_label.setText(translate('OpenLP.StartTimeForm', 'The blue box shows the main area.'))
        self.footer_colour_label.setText(translate('OpenLP.StartTimeForm', 'The red box shows the footer.'))
