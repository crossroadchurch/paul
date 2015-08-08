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
The file rename dialog.
"""

from PyQt4 import QtGui

from .filerenamedialog import Ui_FileRenameDialog

from openlp.core.common import Registry, RegistryProperties, translate


class FileRenameForm(QtGui.QDialog, Ui_FileRenameDialog, RegistryProperties):
    """
    The file rename dialog
    """
    def __init__(self):
        """
        Constructor
        """
        super(FileRenameForm, self).__init__(Registry().get('main_window'))
        self._setup()

    def _setup(self):
        """
        Set up the class. This method is mocked out by the tests.
        """
        self.setupUi(self)

    def exec_(self, copy=False):
        """
        Run the Dialog with correct heading.
        """
        if copy:
            self.setWindowTitle(translate('OpenLP.FileRenameForm', 'File Copy'))
        else:
            self.setWindowTitle(translate('OpenLP.FileRenameForm', 'File Rename'))
        self.file_name_edit.setFocus()
        return QtGui.QDialog.exec_(self)
