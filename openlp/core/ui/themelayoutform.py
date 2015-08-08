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
The form layout
"""
from PyQt4 import QtGui, QtCore

from .themelayoutdialog import Ui_ThemeLayoutDialog


class ThemeLayoutForm(QtGui.QDialog, Ui_ThemeLayoutDialog):
    """
    The exception dialog
    """
    def __init__(self, parent):
        """
        Constructor
        """
        super(ThemeLayoutForm, self).__init__(parent)
        self.setupUi(self)

    def exec_(self, image):
        """
        Run the Dialog with correct heading.
        """
        pixmap = image.scaledToHeight(400, QtCore.Qt.SmoothTransformation)
        self.theme_display_label.setPixmap(pixmap)
        display_aspect_ratio = float(image.width()) / image.height()
        self.theme_display_label.setFixedSize(400, 400 / display_aspect_ratio)
        return QtGui.QDialog.exec_(self)
