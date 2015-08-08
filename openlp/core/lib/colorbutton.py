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
Provide a custom widget based on QPushButton for the selection of colors
"""
from PyQt4 import QtCore, QtGui

from openlp.core.common import translate


class ColorButton(QtGui.QPushButton):
    """
    Subclasses QPushbutton to create a "Color Chooser" button
    """

    colorChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Initialise the ColorButton
        """
        super(ColorButton, self).__init__()
        self.parent = parent
        self.change_color('#ffffff')
        self.setToolTip(translate('OpenLP.ColorButton', 'Click to select a color.'))
        self.clicked.connect(self.on_clicked)

    def change_color(self, color):
        """
        Sets the _color variable and the background color.

        :param color:  String representation of a hexidecimal color
        """
        self._color = color
        self.setStyleSheet('background-color: %s' % color)

    @property
    def color(self):
        """
        Property method to return the color variable

        :return:  String representation of a hexidecimal color
        """
        return self._color

    @color.setter
    def color(self, color):
        """
        Property setter to change the instance color

        :param color:  String representation of a hexidecimal color
        """
        self.change_color(color)

    def on_clicked(self):
        """
        Handle the PushButton clicked signal, showing the ColorDialog and validating the input
        """
        new_color = QtGui.QColorDialog.getColor(QtGui.QColor(self._color), self.parent)
        if new_color.isValid() and self._color != new_color.name():
            self.change_color(new_color.name())
            self.colorChanged.emit(new_color.name())
