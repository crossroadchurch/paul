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
The :mod:`songexportform` module provides the wizard for exporting songs to the
OpenLyrics format.
"""
import logging

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, UiStrings, translate
from openlp.core.lib import create_separated_list, build_icon
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.wizard import OpenLPWizard, WizardStrings
from openlp.plugins.songs.lib.db import Song
from openlp.plugins.songs.lib.openlyricsexport import OpenLyricsExport

log = logging.getLogger(__name__)


class SongExportForm(OpenLPWizard):
    """
    This is the Song Export Wizard, which allows easy exporting of Songs to the
    OpenLyrics format.
    """
    log.info('SongExportForm loaded')

    def __init__(self, parent, plugin):
        """
        Instantiate the wizard, and run any extra setup we need to.

        :param parent: The QWidget-derived parent of the wizard.
        :param plugin: The songs plugin.
        """
        super(SongExportForm, self).__init__(parent, plugin, 'song_export_wizard', ':/wizards/wizard_exportsong.bmp')
        self.stop_export_flag = False
        Registry().register_function('openlp_stop_wizard', self.stop_export)

    def stop_export(self):
        """
        Sets the flag for the exporter to stop the export.
        """
        log.debug('Stopping songs export')
        self.stop_export_flag = True

    def setupUi(self, image):
        """
        Set up the song wizard UI.
        """
        super(SongExportForm, self).setupUi(image)

    def custom_signals(self):
        """
        Song wizard specific signals.
        """
        self.available_list_widget.itemActivated.connect(self.on_item_activated)
        self.search_line_edit.textEdited.connect(self.on_search_line_edit_changed)
        self.uncheck_button.clicked.connect(self.on_uncheck_button_clicked)
        self.check_button.clicked.connect(self.on_check_button_clicked)
        self.directory_button.clicked.connect(self.on_directory_button_clicked)

    def add_custom_pages(self):
        """
        Add song wizard specific pages.
        """
        # The page with all available songs.
        self.available_songs_page = QtGui.QWizardPage()
        self.available_songs_page.setObjectName('available_songs_page')
        self.available_songs_layout = QtGui.QHBoxLayout(self.available_songs_page)
        self.available_songs_layout.setObjectName('available_songs_layout')
        self.vertical_layout = QtGui.QVBoxLayout()
        self.vertical_layout.setObjectName('vertical_layout')
        self.available_list_widget = QtGui.QListWidget(self.available_songs_page)
        self.available_list_widget.setObjectName('available_list_widget')
        self.vertical_layout.addWidget(self.available_list_widget)
        self.horizontal_layout = QtGui.QHBoxLayout()
        self.horizontal_layout.setObjectName('horizontal_layout')
        self.search_label = QtGui.QLabel(self.available_songs_page)
        self.search_label.setObjectName('search_label')
        self.horizontal_layout.addWidget(self.search_label)
        self.search_line_edit = QtGui.QLineEdit(self.available_songs_page)
        self.search_line_edit.setObjectName('search_line_edit')
        self.horizontal_layout.addWidget(self.search_line_edit)
        spacer_item = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontal_layout.addItem(spacer_item)
        self.uncheck_button = QtGui.QPushButton(self.available_songs_page)
        self.uncheck_button.setObjectName('uncheck_button')
        self.horizontal_layout.addWidget(self.uncheck_button)
        self.check_button = QtGui.QPushButton(self.available_songs_page)
        self.check_button.setObjectName('selectButton')
        self.horizontal_layout.addWidget(self.check_button)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.available_songs_layout.addLayout(self.vertical_layout)
        self.addPage(self.available_songs_page)
        # The page with the selected songs.
        self.export_song_page = QtGui.QWizardPage()
        self.export_song_page.setObjectName('available_songs_page')
        self.export_song_layout = QtGui.QHBoxLayout(self.export_song_page)
        self.export_song_layout.setObjectName('export_song_layout')
        self.grid_layout = QtGui.QGridLayout()
        self.grid_layout.setObjectName('range_layout')
        self.selected_list_widget = QtGui.QListWidget(self.export_song_page)
        self.selected_list_widget.setObjectName('selected_list_widget')
        self.grid_layout.addWidget(self.selected_list_widget, 1, 0, 1, 1)
        # FIXME: self.horizontal_layout is already defined above?!?!?
        self.horizontal_layout = QtGui.QHBoxLayout()
        self.horizontal_layout.setObjectName('horizontal_layout')
        self.directory_label = QtGui.QLabel(self.export_song_page)
        self.directory_label.setObjectName('directory_label')
        self.horizontal_layout.addWidget(self.directory_label)
        self.directory_line_edit = QtGui.QLineEdit(self.export_song_page)
        self.directory_line_edit.setObjectName('directory_line_edit')
        self.horizontal_layout.addWidget(self.directory_line_edit)
        self.directory_button = QtGui.QToolButton(self.export_song_page)
        self.directory_button.setIcon(build_icon(':/exports/export_load.png'))
        self.directory_button.setObjectName('directory_button')
        self.horizontal_layout.addWidget(self.directory_button)
        self.grid_layout.addLayout(self.horizontal_layout, 0, 0, 1, 1)
        self.export_song_layout.addLayout(self.grid_layout)
        self.addPage(self.export_song_page)

    def retranslateUi(self):
        """
        Song wizard localisation.
        """
        self.setWindowTitle(translate('SongsPlugin.ExportWizardForm', 'Song Export Wizard'))
        self.title_label.setText(WizardStrings.HeaderStyle %
                                 translate('OpenLP.Ui', 'Welcome to the Song Export Wizard'))
        self.information_label.setText(
            translate('SongsPlugin.ExportWizardForm', 'This wizard will help to export your songs to the open and free '
                                                      '<strong>OpenLyrics </strong> worship song format.'))
        self.available_songs_page.setTitle(translate('SongsPlugin.ExportWizardForm', 'Select Songs'))
        self.available_songs_page.setSubTitle(translate('SongsPlugin.ExportWizardForm',
                                              'Check the songs you want to export.'))
        self.search_label.setText('%s:' % UiStrings().Search)
        self.uncheck_button.setText(translate('SongsPlugin.ExportWizardForm', 'Uncheck All'))
        self.check_button.setText(translate('SongsPlugin.ExportWizardForm', 'Check All'))
        self.export_song_page.setTitle(translate('SongsPlugin.ExportWizardForm', 'Select Directory'))
        self.export_song_page.setSubTitle(translate('SongsPlugin.ExportWizardForm',
                                          'Select the directory where you want the songs to be saved.'))
        self.directory_label.setText(translate('SongsPlugin.ExportWizardForm', 'Directory:'))
        self.progress_page.setTitle(translate('SongsPlugin.ExportWizardForm', 'Exporting'))
        self.progress_page.setSubTitle(translate('SongsPlugin.ExportWizardForm',
                                       'Please wait while your songs are exported.'))
        self.progress_label.setText(WizardStrings.Ready)
        self.progress_bar.setFormat(WizardStrings.PercentSymbolFormat)

    def validateCurrentPage(self):
        """
        Validate the current page before moving on to the next page.
        """
        if self.currentPage() == self.welcome_page:
            return True
        elif self.currentPage() == self.available_songs_page:
            items = [
                item for item in self._find_list_widget_items(self.available_list_widget) if item.checkState()
            ]
            if not items:
                critical_error_message_box(
                    UiStrings().NISp,
                    translate('SongsPlugin.ExportWizardForm', 'You need to add at least one Song to export.'))
                return False
            self.selected_list_widget.clear()
            # Add the songs to the list of selected songs.
            for item in items:
                song = QtGui.QListWidgetItem(item.text())
                song.setData(QtCore.Qt.UserRole, item.data(QtCore.Qt.UserRole))
                song.setFlags(QtCore.Qt.ItemIsEnabled)
                self.selected_list_widget.addItem(song)
            return True
        elif self.currentPage() == self.export_song_page:
            if not self.directory_line_edit.text():
                critical_error_message_box(
                    translate('SongsPlugin.ExportWizardForm', 'No Save Location specified'),
                    translate('SongsPlugin.ExportWizardForm', 'You need to specify a directory.'))
                return False
            return True
        elif self.currentPage() == self.progress_page:
            self.available_list_widget.clear()
            self.selected_list_widget.clear()
            return True

    def set_defaults(self):
        """
        Set default form values for the song export wizard.
        """
        self.restart()
        self.finish_button.setVisible(False)
        self.cancel_button.setVisible(True)
        self.available_list_widget.clear()
        self.selected_list_widget.clear()
        self.directory_line_edit.clear()
        self.search_line_edit.clear()
        # Load the list of songs.
        self.application.set_busy_cursor()
        songs = self.plugin.manager.get_all_objects(Song)
        songs.sort(key=lambda song: song.sort_key)
        for song in songs:
            # No need to export temporary songs.
            if song.temporary:
                continue
            authors = create_separated_list([author.display_name for author in song.authors])
            title = '%s (%s)' % (str(song.title), authors)
            item = QtGui.QListWidgetItem(title)
            item.setData(QtCore.Qt.UserRole, song)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.available_list_widget.addItem(item)
        self.application.set_normal_cursor()

    def pre_wizard(self):
        """
        Perform pre export tasks.
        """
        super(SongExportForm, self).pre_wizard()
        self.progress_label.setText(translate('SongsPlugin.ExportWizardForm', 'Starting export...'))
        self.application.process_events()

    def perform_wizard(self):
        """
        Perform the actual export. This creates an *openlyricsexport* instance and calls the *do_export* method.
        """
        songs = [
            song.data(QtCore.Qt.UserRole)
            for song in self._find_list_widget_items(self.selected_list_widget)
        ]
        exporter = OpenLyricsExport(self, songs, self.directory_line_edit.text())
        try:
            if exporter.do_export():
                self.progress_label.setText(
                    translate('SongsPlugin.SongExportForm',
                              'Finished export. To import these files use the <strong>OpenLyrics</strong> importer.'))
            else:
                self.progress_label.setText(translate('SongsPlugin.SongExportForm', 'Your song export failed.'))
        except OSError as ose:
            self.progress_label.setText(translate('SongsPlugin.SongExportForm', 'Your song export failed because this '
                                                  'error occurred: %s') % ose.strerror)

    def _find_list_widget_items(self, list_widget, text=''):
        """
        Returns a list of *QListWidgetItem*s of the ``list_widget``. Note, that hidden items are included.

        :param list_widget: The widget to get all items from. (QListWidget)
        :param text: The text to search for. (unicode string)
        """
        return [
            item for item in list_widget.findItems(text, QtCore.Qt.MatchContains)
        ]

    def on_item_activated(self, item):
        """
        Called, when an item in the *available_list_widget* has been triggered.
        The item is check if it was not checked, whereas it is unchecked when it
        was checked.

        :param item:  The *QListWidgetItem* which was triggered.
        """
        item.setCheckState(
            QtCore.Qt.Unchecked if item.checkState() else QtCore.Qt.Checked)

    def on_search_line_edit_changed(self, text):
        """
        The *search_line_edit*'s text has been changed. Update the list of
        available songs. Note that any song, which does not match the ``text``
        will be hidden, but not unchecked!

        :param text:  The text of the *search_line_edit*.
        """
        search_result = [
            song for song in self._find_list_widget_items(self.available_list_widget, text)
        ]
        for item in self._find_list_widget_items(self.available_list_widget):
            item.setHidden(item not in search_result)

    def on_uncheck_button_clicked(self):
        """
        The *uncheck_button* has been clicked. Set all visible songs unchecked.
        """
        for row in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(row)
            if not item.isHidden():
                item.setCheckState(QtCore.Qt.Unchecked)

    def on_check_button_clicked(self):
        """
        The *check_button* has been clicked. Set all visible songs checked.
        """
        for row in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(row)
            if not item.isHidden():
                item.setCheckState(QtCore.Qt.Checked)

    def on_directory_button_clicked(self):
        """
        Called when the *directory_button* was clicked. Opens a dialog and writes
        the path to *directory_line_edit*.
        """
        self.get_folder(
            translate('SongsPlugin.ExportWizardForm', 'Select Destination Folder'),
            self.directory_line_edit, 'last directory export')
