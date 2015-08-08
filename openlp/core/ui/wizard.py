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
The :mod:``wizard`` module provides generic wizard tools for OpenLP.
"""
import logging
import os

from PyQt4 import QtGui

from openlp.core.common import Registry, RegistryProperties, Settings, UiStrings, translate, is_macosx
from openlp.core.lib import build_icon
from openlp.core.lib.ui import add_welcome_page

log = logging.getLogger(__name__)


class WizardStrings(object):
    """
    Provide standard strings for wizards to use.
    """
    # Applications/Formats we import from or export to. These get used in
    # multiple places but do not need translating unless you find evidence of
    # the writers translating their own product name.
    CSV = 'CSV'
    OS = 'OpenSong'
    OSIS = 'OSIS'
    ZEF = 'Zefania'
    # These strings should need a good reason to be retranslated elsewhere.
    FinishedImport = translate('OpenLP.Ui', 'Finished import.')
    FormatLabel = translate('OpenLP.Ui', 'Format:')
    HeaderStyle = '<span style="font-size:14pt; font-weight:600;">%s</span>'
    Importing = translate('OpenLP.Ui', 'Importing')
    ImportingType = translate('OpenLP.Ui', 'Importing "%s"...')
    ImportSelect = translate('OpenLP.Ui', 'Select Import Source')
    ImportSelectLong = translate('OpenLP.Ui', 'Select the import format and the location to import from.')
    OpenTypeFile = translate('OpenLP.Ui', 'Open %s File')
    OpenTypeFolder = translate('OpenLP.Ui', 'Open %s Folder')
    PercentSymbolFormat = translate('OpenLP.Ui', '%p%')
    Ready = translate('OpenLP.Ui', 'Ready.')
    StartingImport = translate('OpenLP.Ui', 'Starting import...')
    YouSpecifyFile = translate('OpenLP.Ui', 'You need to specify one %s file to import from.',
                               'A file type e.g. OpenSong')
    YouSpecifyFiles = translate('OpenLP.Ui', 'You need to specify at least one %s file to import from.',
                                'A file type e.g. OpenSong')
    YouSpecifyFolder = translate('OpenLP.Ui', 'You need to specify one %s folder to import from.',
                                 'A song format e.g. PowerSong')


class OpenLPWizard(QtGui.QWizard, RegistryProperties):
    """
    Generic OpenLP wizard to provide generic functionality and a unified look
    and feel.

    ``parent``
        The QWidget-derived parent of the wizard.

    ``plugin``
        Plugin this wizard is part of. The plugin will be saved in the "plugin" variable.
        The plugin will also be used as basis for the file dialog methods this class provides.

    ``name``
        The object name this wizard should have.

    ``image``
        The image to display on the "welcome" page of the wizard. Should be 163x350.

    ``add_progress_page``
        Whether to add a progress page with a progressbar at the end of the wizard.
    """
    def __init__(self, parent, plugin, name, image, add_progress_page=True):
        """
        Constructor
        """
        super(OpenLPWizard, self).__init__(parent)
        self.plugin = plugin
        self.with_progress_page = add_progress_page
        self.setObjectName(name)
        self.open_icon = build_icon(':/general/general_open.png')
        self.delete_icon = build_icon(':/general/general_delete.png')
        self.finish_button = self.button(QtGui.QWizard.FinishButton)
        self.cancel_button = self.button(QtGui.QWizard.CancelButton)
        self.setupUi(image)
        self.register_fields()
        self.custom_init()
        self.custom_signals()
        self.currentIdChanged.connect(self.on_current_id_changed)
        if self.with_progress_page:
            self.error_copy_to_button.clicked.connect(self.on_error_copy_to_button_clicked)
            self.error_save_to_button.clicked.connect(self.on_error_save_to_button_clicked)

    def setupUi(self, image):
        """
        Set up the wizard UI.
        """
        self.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        self.setModal(True)
        self.setOptions(QtGui.QWizard.IndependentPages |
                        QtGui.QWizard.NoBackButtonOnStartPage | QtGui.QWizard.NoBackButtonOnLastPage)
        if is_macosx():
            self.setPixmap(QtGui.QWizard.BackgroundPixmap, QtGui.QPixmap(':/wizards/openlp-osx-wizard.png'))
        else:
            self.setWizardStyle(QtGui.QWizard.ModernStyle)
        add_welcome_page(self, image)
        self.add_custom_pages()
        if self.with_progress_page:
            self.add_progress_page()
        self.retranslateUi()

    def register_fields(self):
        """
        Hook method for wizards to register any fields they need.
        """
        pass

    def custom_init(self):
        """
        Hook method for custom initialisation
        """
        pass

    def custom_signals(self):
        """
        Hook method for adding custom signals
        """
        pass

    def add_custom_pages(self):
        """
        Hook method for wizards to add extra pages
        """
        pass

    def add_progress_page(self):
        """
        Add the progress page for the wizard. This page informs the user how
        the wizard is progressing with its task.
        """
        self.progress_page = QtGui.QWizardPage()
        self.progress_page.setObjectName('progress_page')
        self.progress_layout = QtGui.QVBoxLayout(self.progress_page)
        self.progress_layout.setMargin(48)
        self.progress_layout.setObjectName('progress_layout')
        self.progress_label = QtGui.QLabel(self.progress_page)
        self.progress_label.setObjectName('progress_label')
        self.progress_label.setWordWrap(True)
        self.progress_layout.addWidget(self.progress_label)
        self.progress_bar = QtGui.QProgressBar(self.progress_page)
        self.progress_bar.setObjectName('progress_bar')
        self.progress_layout.addWidget(self.progress_bar)
        # Add a QTextEdit and a copy to file and copy to clipboard button to be
        # able to provide feedback to the user. Hidden by default.
        self.error_report_text_edit = QtGui.QTextEdit(self.progress_page)
        self.error_report_text_edit.setObjectName('error_report_text_edit')
        self.error_report_text_edit.setHidden(True)
        self.error_report_text_edit.setReadOnly(True)
        self.progress_layout.addWidget(self.error_report_text_edit)
        self.error_button_layout = QtGui.QHBoxLayout()
        self.error_button_layout.setObjectName('error_button_layout')
        spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.error_button_layout.addItem(spacer)
        self.error_copy_to_button = QtGui.QPushButton(self.progress_page)
        self.error_copy_to_button.setObjectName('error_copy_to_button')
        self.error_copy_to_button.setHidden(True)
        self.error_copy_to_button.setIcon(build_icon(':/system/system_edit_copy.png'))
        self.error_button_layout.addWidget(self.error_copy_to_button)
        self.error_save_to_button = QtGui.QPushButton(self.progress_page)
        self.error_save_to_button.setObjectName('error_save_to_button')
        self.error_save_to_button.setHidden(True)
        self.error_save_to_button.setIcon(build_icon(':/general/general_save.png'))
        self.error_button_layout.addWidget(self.error_save_to_button)
        self.progress_layout.addLayout(self.error_button_layout)
        self.addPage(self.progress_page)

    def exec_(self):
        """
        Run the wizard.
        """
        self.set_defaults()
        return QtGui.QWizard.exec_(self)

    def reject(self):
        """
        Stop the wizard on cancel button, close button or ESC key.
        """
        log.debug('Wizard cancelled by user.')
        if self.with_progress_page and self.currentPage() == self.progress_page:
            Registry().execute('openlp_stop_wizard')
        self.done(QtGui.QDialog.Rejected)

    def on_current_id_changed(self, page_id):
        """
        Perform necessary functions depending on which wizard page is active.
        """
        if self.with_progress_page and self.page(page_id) == self.progress_page:
            self.pre_wizard()
            self.perform_wizard()
            self.post_wizard()
        else:
            self.custom_page_changed(page_id)

    def custom_page_changed(self, page_id):
        """
        Called when changing to a page other than the progress page
        """
        pass

    def on_error_copy_to_button_clicked(self):
        """
        Called when the ``error_copy_to_button`` has been clicked.
        """
        pass

    def on_error_save_to_button_clicked(self):
        """
        Called when the ``error_save_to_button`` has been clicked.
        """
        pass

    def increment_progress_bar(self, status_text, increment=1):
        """
        Update the wizard progress page.

        :param status_text: Current status information to display.
        :param increment: The value to increment the progress bar by.
        """
        log.debug('IncrementBar %s', status_text)
        self.progress_label.setText(status_text)
        if increment > 0:
            self.progress_bar.setValue(self.progress_bar.value() + increment)
        self.application.process_events()

    def pre_wizard(self):
        """
        Prepare the UI for the import.
        """
        self.finish_button.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(1188)
        self.progress_bar.setValue(0)

    def post_wizard(self):
        """
        Clean up the UI after the import has finished.
        """
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.finish_button.setVisible(True)
        self.cancel_button.setVisible(False)
        self.application.process_events()

    def get_file_name(self, title, editbox, setting_name, filters=''):
        """
        Opens a QFileDialog and saves the filename to the given editbox.

        :param title: The title of the dialog (unicode).
        :param editbox:  An editbox (QLineEdit).
        :param setting_name: The place where to save the last opened directory.
        :param filters: The file extension filters. It should contain the file description
            as well as the file extension. For example::

                'OpenLP 2.0 Databases (*.sqlite)'
        """
        if filters:
            filters += ';;'
        filters += '%s (*)' % UiStrings().AllFiles
        filename = QtGui.QFileDialog.getOpenFileName(
            self, title, os.path.dirname(Settings().value(self.plugin.settings_section + '/' + setting_name)), filters)
        if filename:
            editbox.setText(filename)
        Settings().setValue(self.plugin.settings_section + '/' + setting_name, filename)

    def get_folder(self, title, editbox, setting_name):
        """
        Opens a QFileDialog and saves the selected folder to the given editbox.

        :param title: The title of the dialog (unicode).
        :param editbox: An editbox (QLineEdit).
        :param setting_name: The place where to save the last opened directory.
        """
        folder = QtGui.QFileDialog.getExistingDirectory(
            self, title, Settings().value(self.plugin.settings_section + '/' + setting_name),
            QtGui.QFileDialog.ShowDirsOnly)
        if folder:
            editbox.setText(folder)
        Settings().setValue(self.plugin.settings_section + '/' + setting_name, folder)
