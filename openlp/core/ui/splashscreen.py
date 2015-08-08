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
The splash screen
"""

from PyQt4 import QtCore, QtGui


class SplashScreen(QtGui.QSplashScreen):
    """
    The splash screen
    """
    def __init__(self):
        """
        Constructor
        """
        super(SplashScreen, self).__init__()
        self.setupUi()

    def setupUi(self):
        """
        Set up the UI
        """
        self.setObjectName('splashScreen')
        self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        splash_image = QtGui.QPixmap(':/graphics/openlp-splash-screen.png')
        self.setPixmap(splash_image)
        self.setMask(splash_image.mask())
        self.resize(370, 370)
