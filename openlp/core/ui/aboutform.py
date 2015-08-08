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
The About dialog.
"""
import webbrowser

from PyQt4 import QtGui

from openlp.core.lib import translate
from openlp.core.utils import get_application_version
from .aboutdialog import UiAboutDialog


class AboutForm(QtGui.QDialog, UiAboutDialog):
    """
    The About dialog
    """

    def __init__(self, parent):
        """
        Do some initialisation stuff
        """
        super(AboutForm, self).__init__(parent)
        self._setup()

    def _setup(self):
        """
        Set up the dialog. This method is mocked out in tests.
        """
        self.setup_ui(self)
        application_version = get_application_version()
        about_text = self.about_text_edit.toPlainText()
        about_text = about_text.replace('<version>', application_version['version'])
        if application_version['build']:
            build_text = translate('OpenLP.AboutForm', ' build %s') % application_version['build']
        else:
            build_text = ''
        about_text = about_text.replace('<revision>', build_text)
        self.about_text_edit.setPlainText(about_text)
        self.volunteer_button.clicked.connect(self.on_volunteer_button_clicked)

    def on_volunteer_button_clicked(self):
        """
        Launch a web browser and go to the contribute page on the site.
        """
        webbrowser.open_new('http://openlp.org/en/contribute')
