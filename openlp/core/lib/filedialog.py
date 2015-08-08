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
Provide a work around for a bug in QFileDialog <https://bugs.launchpad.net/openlp/+bug/1209515>
"""
import logging
import os
from urllib import parse

from PyQt4 import QtGui

from openlp.core.common import UiStrings

log = logging.getLogger(__name__)


class FileDialog(QtGui.QFileDialog):
    """
    Subclass QFileDialog to work round a bug
    """
    @staticmethod
    def getOpenFileNames(parent, *args, **kwargs):
        """
        Reimplement getOpenFileNames to fix the way it returns some file names that url encoded when selecting multiple
        files
        """
        files = QtGui.QFileDialog.getOpenFileNames(parent, *args, **kwargs)
        file_list = []
        for file in files:
            if not os.path.exists(file):
                log.info('File not found. Attempting to unquote.')
                file = parse.unquote(file)
                if not os.path.exists(file):
                    log.error('File %s not found.' % file)
                    QtGui.QMessageBox.information(parent, UiStrings().FileNotFound,
                                                  UiStrings().FileNotFoundMessage % file)
                    continue
            file_list.append(file)
        return file_list
