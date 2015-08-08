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
The :mod:`~openlp.plugins.songs.forms.songselectform` module contains the GUI for the SongSelect importer
"""

import logging
import os
from time import sleep

from PyQt4 import QtCore, QtGui

from openlp.core import Settings
from openlp.core.common import Registry, is_win
from openlp.core.lib import translate
from openlp.plugins.songs.forms.songselectdialog import Ui_SongSelectDialog
from openlp.plugins.songs.lib.songselect import SongSelectImport

log = logging.getLogger(__name__)


class SearchWorker(QtCore.QObject):
    """
    Run the actual SongSelect search, and notify the GUI when we find each song.
    """
    show_info = QtCore.pyqtSignal(str, str)
    found_song = QtCore.pyqtSignal(dict)
    finished = QtCore.pyqtSignal()
    quit = QtCore.pyqtSignal()

    def __init__(self, importer, search_text):
        super().__init__()
        self.importer = importer
        self.search_text = search_text

    def start(self):
        """
        Run a search and then parse the results page of the search.
        """
        songs = self.importer.search(self.search_text, 1000, self._found_song_callback)
        if len(songs) >= 1000:
            self.show_info.emit(
                translate('SongsPlugin.SongSelectForm', 'More than 1000 results'),
                translate('SongsPlugin.SongSelectForm', 'Your search has returned more than 1000 results, it has '
                                                        'been stopped. Please refine your search to fetch better '
                                                        'results.'))
        self.finished.emit()
        self.quit.emit()

    def _found_song_callback(self, song):
        """
        A callback used by the paginate function to notify watching processes when it finds a song.

        :param song: The song that was found
        """
        self.found_song.emit(song)


class SongSelectForm(QtGui.QDialog, Ui_SongSelectDialog):
    """
    The :class:`SongSelectForm` class is the SongSelect dialog.
    """

    def __init__(self, parent=None, plugin=None, db_manager=None):
        QtGui.QDialog.__init__(self, parent)
        self.plugin = plugin
        self.db_manager = db_manager
        self.setup_ui(self)

    def initialise(self):
        """
        Initialise the SongSelectForm
        """
        self.thread = None
        self.worker = None
        self.song_count = 0
        self.song = None
        self.song_select_importer = SongSelectImport(self.db_manager)
        self.save_password_checkbox.toggled.connect(self.on_save_password_checkbox_toggled)
        self.login_button.clicked.connect(self.on_login_button_clicked)
        self.search_button.clicked.connect(self.on_search_button_clicked)
        self.search_combobox.returnPressed.connect(self.on_search_button_clicked)
        self.logout_button.clicked.connect(self.done)
        self.search_results_widget.itemDoubleClicked.connect(self.on_search_results_widget_double_clicked)
        self.search_results_widget.itemSelectionChanged.connect(self.on_search_results_widget_selection_changed)
        self.view_button.clicked.connect(self.on_view_button_clicked)
        self.back_button.clicked.connect(self.on_back_button_clicked)
        self.import_button.clicked.connect(self.on_import_button_clicked)

    def exec_(self):
        """
        Execute the dialog. This method sets everything back to its initial
        values.
        """
        self.stacked_widget.setCurrentIndex(0)
        self.username_edit.setEnabled(True)
        self.password_edit.setEnabled(True)
        self.save_password_checkbox.setEnabled(True)
        self.search_combobox.clearEditText()
        self.search_combobox.clear()
        self.search_results_widget.clear()
        self.view_button.setEnabled(False)
        if Settings().contains(self.plugin.settings_section + '/songselect password'):
            self.username_edit.setText(Settings().value(self.plugin.settings_section + '/songselect username'))
            self.password_edit.setText(Settings().value(self.plugin.settings_section + '/songselect password'))
            self.save_password_checkbox.setChecked(True)
        if Settings().contains(self.plugin.settings_section + '/songselect searches'):
            self.search_combobox.addItems(
                Settings().value(self.plugin.settings_section + '/songselect searches').split('|'))
        self.username_edit.setFocus()
        return QtGui.QDialog.exec_(self)

    def done(self, r):
        """
        Log out of SongSelect.

        :param r: The result of the dialog.
        """
        log.debug('Closing SongSelectForm')
        if self.stacked_widget.currentIndex() > 0:
            progress_dialog = QtGui.QProgressDialog(
                translate('SongsPlugin.SongSelectForm', 'Logging out...'), '', 0, 2, self)
            progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
            progress_dialog.setCancelButton(None)
            progress_dialog.setValue(1)
            progress_dialog.show()
            progress_dialog.setFocus()
            self.application.process_events()
            sleep(0.5)
            self.application.process_events()
            self.song_select_importer.logout()
            self.application.process_events()
            progress_dialog.setValue(2)
        return QtGui.QDialog.done(self, r)

    def _update_login_progress(self):
        self.login_progress_bar.setValue(self.login_progress_bar.value() + 1)
        self.application.process_events()

    def _update_song_progress(self):
        self.song_progress_bar.setValue(self.song_progress_bar.value() + 1)
        self.application.process_events()

    def _view_song(self, current_item):
        if not current_item:
            return
        else:
            current_item = current_item.data(QtCore.Qt.UserRole)
        self.song_progress_bar.setVisible(True)
        self.import_button.setEnabled(False)
        self.back_button.setEnabled(False)
        self.title_edit.setText('')
        self.title_edit.setEnabled(False)
        self.copyright_edit.setText('')
        self.copyright_edit.setEnabled(False)
        self.ccli_edit.setText('')
        self.ccli_edit.setEnabled(False)
        self.author_list_widget.clear()
        self.author_list_widget.setEnabled(False)
        self.lyrics_table_widget.clear()
        self.lyrics_table_widget.setRowCount(0)
        self.lyrics_table_widget.setEnabled(False)
        self.stacked_widget.setCurrentIndex(2)
        song = {}
        for key, value in current_item.items():
            song[key] = value
        self.song_progress_bar.setValue(0)
        self.application.process_events()
        # Get the full song
        song = self.song_select_importer.get_song(song, self._update_song_progress)
        if not song:
            QtGui.QMessageBox.critical(
                self, translate('SongsPlugin.SongSelectForm', 'Incomplete song'),
                translate('SongsPlugin.SongSelectForm', 'This song is missing some information, like the lyrics, '
                                                        'and cannot be imported.'),
                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok), QtGui.QMessageBox.Ok)
            self.stacked_widget.setCurrentIndex(1)
            return
        # Update the UI
        self.title_edit.setText(song['title'])
        self.copyright_edit.setText(song['copyright'])
        self.ccli_edit.setText(song['ccli_number'])
        for author in song['authors']:
            QtGui.QListWidgetItem(author, self.author_list_widget)
        for counter, verse in enumerate(song['verses']):
            self.lyrics_table_widget.setRowCount(self.lyrics_table_widget.rowCount() + 1)
            item = QtGui.QTableWidgetItem(verse['lyrics'])
            item.setData(QtCore.Qt.UserRole, verse['label'])
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.lyrics_table_widget.setItem(counter, 0, item)
        self.lyrics_table_widget.setVerticalHeaderLabels([verse['label'] for verse in song['verses']])
        self.lyrics_table_widget.resizeRowsToContents()
        self.title_edit.setEnabled(True)
        self.copyright_edit.setEnabled(True)
        self.ccli_edit.setEnabled(True)
        self.author_list_widget.setEnabled(True)
        self.lyrics_table_widget.setEnabled(True)
        self.lyrics_table_widget.repaint()
        self.import_button.setEnabled(True)
        self.back_button.setEnabled(True)
        self.song_progress_bar.setVisible(False)
        self.song_progress_bar.setValue(0)
        self.song = song
        self.application.process_events()

    def on_save_password_checkbox_toggled(self, checked):
        """
        Show a warning dialog when the user toggles the save checkbox on or off.

        :param checked: If the combobox is checked or not
        """
        if checked and self.login_page.isVisible():
            answer = QtGui.QMessageBox.question(
                self, translate('SongsPlugin.SongSelectForm', 'Save Username and Password'),
                translate('SongsPlugin.SongSelectForm', 'WARNING: Saving your username and password is INSECURE, your '
                                                        'password is stored in PLAIN TEXT. Click Yes to save your '
                                                        'password or No to cancel this.'),
                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No), QtGui.QMessageBox.No)
            if answer == QtGui.QMessageBox.No:
                self.save_password_checkbox.setChecked(False)

    def on_login_button_clicked(self):
        """
        Log the user in to SongSelect.
        """
        self.username_edit.setEnabled(False)
        self.password_edit.setEnabled(False)
        self.save_password_checkbox.setEnabled(False)
        self.login_button.setEnabled(False)
        self.login_spacer.setVisible(False)
        self.login_progress_bar.setValue(0)
        self.login_progress_bar.setVisible(True)
        self.application.process_events()
        # Log the user in
        if not self.song_select_importer.login(
                self.username_edit.text(), self.password_edit.text(), self._update_login_progress):
            QtGui.QMessageBox.critical(
                self,
                translate('SongsPlugin.SongSelectForm', 'Error Logging In'),
                translate('SongsPlugin.SongSelectForm',
                          'There was a problem logging in, perhaps your username or password is incorrect?')
            )
        else:
            if self.save_password_checkbox.isChecked():
                Settings().setValue(self.plugin.settings_section + '/songselect username', self.username_edit.text())
                Settings().setValue(self.plugin.settings_section + '/songselect password', self.password_edit.text())
            else:
                Settings().remove(self.plugin.settings_section + '/songselect username')
                Settings().remove(self.plugin.settings_section + '/songselect password')
            self.stacked_widget.setCurrentIndex(1)
        self.login_progress_bar.setVisible(False)
        self.login_progress_bar.setValue(0)
        self.login_spacer.setVisible(True)
        self.login_button.setEnabled(True)
        self.username_edit.setEnabled(True)
        self.password_edit.setEnabled(True)
        self.save_password_checkbox.setEnabled(True)
        self.search_combobox.setFocus()
        self.application.process_events()

    def on_search_button_clicked(self):
        """
        Run a search on SongSelect.
        """
        # Set up UI components
        self.view_button.setEnabled(False)
        self.search_button.setEnabled(False)
        self.search_progress_bar.setMinimum(0)
        self.search_progress_bar.setMaximum(0)
        self.search_progress_bar.setValue(0)
        self.search_progress_bar.setVisible(True)
        self.search_results_widget.clear()
        self.result_count_label.setText(translate('SongsPlugin.SongSelectForm', 'Found %s song(s)') % self.song_count)
        self.application.process_events()
        self.song_count = 0
        search_history = self.search_combobox.getItems()
        Settings().setValue(self.plugin.settings_section + '/songselect searches', '|'.join(search_history))
        # Create thread and run search
        self.thread = QtCore.QThread()
        self.worker = SearchWorker(self.song_select_importer, self.search_combobox.currentText())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.start)
        self.worker.show_info.connect(self.on_search_show_info)
        self.worker.found_song.connect(self.on_search_found_song)
        self.worker.finished.connect(self.on_search_finished)
        self.worker.quit.connect(self.thread.quit)
        self.worker.quit.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_search_show_info(self, title, message):
        """
        Show an informational message from the search thread
        :param title:
        :param message:
        """
        QtGui.QMessageBox.information(self, title, message)

    def on_search_found_song(self, song):
        """
        Add a song to the list when one is found.
        :param song:
        """
        self.song_count += 1
        self.result_count_label.setText(translate('SongsPlugin.SongSelectForm', 'Found %s song(s)') % self.song_count)
        item_title = song['title'] + ' (' + ', '.join(song['authors']) + ')'
        song_item = QtGui.QListWidgetItem(item_title, self.search_results_widget)
        song_item.setData(QtCore.Qt.UserRole, song)

    def on_search_finished(self):
        """
        Slot which is called when the search is completed.
        """
        self.application.process_events()
        self.search_progress_bar.setVisible(False)
        self.search_button.setEnabled(True)
        self.application.process_events()

    def on_search_results_widget_selection_changed(self):
        """
        Enable or disable the view button when the selection changes.
        """
        self.view_button.setEnabled(len(self.search_results_widget.selectedItems()) > 0)

    def on_view_button_clicked(self):
        """
        View a song from SongSelect.
        """
        self._view_song(self.search_results_widget.currentItem())

    def on_search_results_widget_double_clicked(self, current_item):
        """
        View a song from SongSelect

        :param current_item:
        """
        self._view_song(current_item)

    def on_back_button_clicked(self):
        """
        Go back to the search page.
        """
        self.stacked_widget.setCurrentIndex(1)
        self.search_combobox.setFocus()

    def on_import_button_clicked(self):
        """
        Import a song from SongSelect.
        """
        self.song_select_importer.save_song(self.song)
        self.song = None
        if QtGui.QMessageBox.question(self, translate('SongsPlugin.SongSelectForm', 'Song Imported'),
                                      translate('SongsPlugin.SongSelectForm', 'Your song has been imported, would you '
                                                                              'like to import more songs?'),
                                      QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                      QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
            self.on_back_button_clicked()
        else:
            self.application.process_events()
            self.done(QtGui.QDialog.Accepted)

    @property
    def application(self):
        """
        Adds the openlp to the class dynamically.
        Windows needs to access the application in a dynamic manner.
        """
        if is_win():
            return Registry().get('application')
        else:
            if not hasattr(self, '_application'):
                self._application = Registry().get('application')
            return self._application
