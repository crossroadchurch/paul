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
The duplicate song removal logic for OpenLP.
"""

import logging
import multiprocessing
import os

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, RegistryProperties, translate
from openlp.core.ui.wizard import OpenLPWizard, WizardStrings
from openlp.plugins.songs.lib import delete_song
from openlp.plugins.songs.lib.db import Song, MediaFile
from openlp.plugins.songs.forms.songreviewwidget import SongReviewWidget
from openlp.plugins.songs.lib.songcompare import songs_probably_equal

log = logging.getLogger(__name__)


def song_generator(songs):
    """
    This is a generator function to return tuples of tuple with two songs and their position in the song array.
    When completed then all songs have once been returned combined with any other songs.

    :param songs: All songs in the database.
    """
    for outer_song_counter in range(len(songs) - 1):
        for inner_song_counter in range(outer_song_counter + 1, len(songs)):
            yield ((outer_song_counter, songs[outer_song_counter].search_lyrics),
                   (inner_song_counter, songs[inner_song_counter].search_lyrics))


class DuplicateSongRemovalForm(OpenLPWizard, RegistryProperties):
    """
    This is the Duplicate Song Removal Wizard. It provides functionality to search for and remove duplicate songs
    in the database.
    """
    log.info('DuplicateSongRemovalForm loaded')

    def __init__(self, plugin):
        """
        Instantiate the wizard, and run any extra setup we need to.

        :param plugin: The songs plugin.
        """
        self.duplicate_song_list = []
        self.review_current_count = 0
        self.review_total_count = 0
        # Used to interrupt ongoing searches when cancel is clicked.
        self.break_search = False
        super(DuplicateSongRemovalForm, self).__init__(
            Registry().get('main_window'), plugin, 'duplicateSongRemovalWizard',
            ':/wizards/wizard_duplicateremoval.bmp', False)
        self.setMinimumWidth(730)

    def custom_signals(self):
        """
        Song wizard specific signals.
        """
        self.finish_button.clicked.connect(self.on_wizard_exit)
        self.cancel_button.clicked.connect(self.on_wizard_exit)

    def add_custom_pages(self):
        """
        Add song wizard specific pages.
        """
        # Add custom pages.
        self.searching_page = QtGui.QWizardPage()
        self.searching_page.setObjectName('searching_page')
        self.searching_vertical_layout = QtGui.QVBoxLayout(self.searching_page)
        self.searching_vertical_layout.setObjectName('searching_vertical_layout')
        self.duplicate_search_progress_bar = QtGui.QProgressBar(self.searching_page)
        self.duplicate_search_progress_bar.setObjectName('duplicate_search_progress_bar')
        self.duplicate_search_progress_bar.setFormat(WizardStrings.PercentSymbolFormat)
        self.searching_vertical_layout.addWidget(self.duplicate_search_progress_bar)
        self.found_duplicates_edit = QtGui.QPlainTextEdit(self.searching_page)
        self.found_duplicates_edit.setUndoRedoEnabled(False)
        self.found_duplicates_edit.setReadOnly(True)
        self.found_duplicates_edit.setObjectName('found_duplicates_edit')
        self.searching_vertical_layout.addWidget(self.found_duplicates_edit)
        self.searching_page_id = self.addPage(self.searching_page)
        self.review_page = QtGui.QWizardPage()
        self.review_page.setObjectName('review_page')
        self.review_layout = QtGui.QVBoxLayout(self.review_page)
        self.review_layout.setObjectName('review_layout')
        self.review_scroll_area = QtGui.QScrollArea(self.review_page)
        self.review_scroll_area.setObjectName('review_scroll_area')
        self.review_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.review_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.review_scroll_area.setWidgetResizable(True)
        self.review_scroll_area_widget = QtGui.QWidget(self.review_scroll_area)
        self.review_scroll_area_widget.setObjectName('review_scroll_area_widget')
        self.review_scroll_area_layout = QtGui.QHBoxLayout(self.review_scroll_area_widget)
        self.review_scroll_area_layout.setObjectName('review_scroll_area_layout')
        self.review_scroll_area_layout.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        self.review_scroll_area_layout.setMargin(0)
        self.review_scroll_area_layout.setSpacing(0)
        self.review_scroll_area.setWidget(self.review_scroll_area_widget)
        self.review_layout.addWidget(self.review_scroll_area)
        self.review_page_id = self.addPage(self.review_page)
        # Add a dummy page to the end, to prevent the finish button to appear and the next button do disappear on the
        # review page.
        self.dummy_page = QtGui.QWizardPage()
        self.dummy_page_id = self.addPage(self.dummy_page)

    def retranslateUi(self):
        """
        Song wizard localisation.
        """
        self.setWindowTitle(translate('Wizard', 'Wizard'))
        self.title_label.setText(WizardStrings.HeaderStyle % translate('OpenLP.Ui',
                                                                       'Welcome to the Duplicate Song Removal Wizard'))
        self.information_label.setText(
            translate("Wizard",
                      'This wizard will help you to remove duplicate songs from the song database. You will have a '
                      'chance to review every potential duplicate song before it is deleted. So no songs will be '
                      'deleted without your explicit approval.'))
        self.searching_page.setTitle(translate('Wizard', 'Searching for duplicate songs.'))
        self.searching_page.setSubTitle(translate('Wizard', 'Please wait while your songs database is analyzed.'))
        self.update_review_counter_text()
        self.review_page.setSubTitle(translate('Wizard',
                                               'Here you can decide which songs to remove and which ones to keep.'))

    def update_review_counter_text(self):
        """
        Set the wizard review page header text.
        """
        self.review_page.setTitle(
            translate('Wizard', 'Review duplicate songs (%s/%s)') %
                     (self.review_current_count, self.review_total_count))

    def custom_page_changed(self, page_id):
        """
        Called when changing the wizard page.

        :param page_id: ID of the page the wizard changed to.
        """
        # Hide back button.
        self.button(QtGui.QWizard.BackButton).hide()
        if page_id == self.searching_page_id:
            self.application.set_busy_cursor()
            try:
                self.button(QtGui.QWizard.NextButton).hide()
                # Search duplicate songs.
                max_songs = self.plugin.manager.get_object_count(Song)
                if max_songs == 0 or max_songs == 1:
                    self.duplicate_search_progress_bar.setMaximum(1)
                    self.duplicate_search_progress_bar.setValue(1)
                    self.notify_no_duplicates()
                    return
                # With x songs we have x*(x - 1) / 2 comparisons.
                max_progress_count = max_songs * (max_songs - 1) // 2
                self.duplicate_search_progress_bar.setMaximum(max_progress_count)
                songs = self.plugin.manager.get_all_objects(Song)
                # Create a worker/process pool to check the songs.
                process_number = max(1, multiprocessing.cpu_count() - 1)
                pool = multiprocessing.Pool(process_number)
                result = pool.imap_unordered(songs_probably_equal, song_generator(songs), 30)
                # Do not accept any further tasks. Also this closes the processes if all tasks are done.
                pool.close()
                # While the processes are still working, start to look at the results.
                for pos_tuple in result:
                    self.duplicate_search_progress_bar.setValue(self.duplicate_search_progress_bar.value() + 1)
                    # The call to process_events() will keep the GUI responsive.
                    self.application.process_events()
                    if self.break_search:
                        pool.terminate()
                        return
                    if pos_tuple is None:
                        continue
                    song1 = songs[pos_tuple[0]]
                    song2 = songs[pos_tuple[1]]
                    duplicate_added = self.add_duplicates_to_song_list(song1, song2)
                    if duplicate_added:
                        self.found_duplicates_edit.appendPlainText(song1.title + "  =  " + song2.title)
                self.review_total_count = len(self.duplicate_song_list)
                if self.duplicate_song_list:
                    self.button(QtGui.QWizard.NextButton).show()
                else:
                    self.notify_no_duplicates()
            finally:
                self.application.set_normal_cursor()
        elif page_id == self.review_page_id:
            self.process_current_duplicate_entry()

    def notify_no_duplicates(self):
        """
        Notifies the user, that there were no duplicates found in the database.
        """
        self.button(QtGui.QWizard.FinishButton).show()
        self.button(QtGui.QWizard.FinishButton).setEnabled(True)
        self.button(QtGui.QWizard.NextButton).hide()
        self.button(QtGui.QWizard.CancelButton).hide()
        QtGui.QMessageBox.information(
            self, translate('Wizard', 'Information'),
            translate('Wizard', 'No duplicate songs have been found in the database.'),
            QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))

    def add_duplicates_to_song_list(self, search_song, duplicate_song):
        """
        Inserts a song duplicate (two similar songs) to the duplicate song list.
        If one of the two songs is already part of the duplicate song list, don't add another duplicate group but
        add the other song to that group.
        Returns True if at least one of the songs was added, False if both were already member of a group.

        :param search_song: The song we searched the duplicate for.
        :param duplicate_song: The duplicate song.
        """
        duplicate_group_found = False
        duplicate_added = False
        for duplicate_group in self.duplicate_song_list:
            # Skip the first song in the duplicate lists, since the first one has to be an earlier song.
            if search_song in duplicate_group and duplicate_song not in duplicate_group:
                duplicate_group.append(duplicate_song)
                duplicate_group_found = True
                duplicate_added = True
                break
            elif search_song not in duplicate_group and duplicate_song in duplicate_group:
                duplicate_group.append(search_song)
                duplicate_group_found = True
                duplicate_added = True
                break
            elif search_song in duplicate_group and duplicate_song in duplicate_group:
                duplicate_group_found = True
                duplicate_added = False
                break
        if not duplicate_group_found:
            self.duplicate_song_list.append([search_song, duplicate_song])
            duplicate_added = True
        return duplicate_added

    def on_wizard_exit(self):
        """
        Once the wizard is finished, refresh the song list,
        since we potentially removed songs from it.
        """
        self.break_search = True
        self.plugin.media_item.on_search_text_button_clicked()

    def set_defaults(self):
        """
        Set default form values for the song import wizard.
        """
        self.restart()
        self.duplicate_search_progress_bar.setValue(0)
        self.found_duplicates_edit.clear()

    def validateCurrentPage(self):
        """
        Controls whether we should switch to the next wizard page. This method loops on the review page as long as
        there are more song duplicates to review.
        """
        if self.currentId() == self.review_page_id:
            # As long as it's not the last duplicate list entry we revisit the review page.
            if len(self.duplicate_song_list) == 1:
                return True
            else:
                self.proceed_to_next_review()
                return False
        return super(DuplicateSongRemovalForm, self).validateCurrentPage()

    def remove_button_clicked(self, song_review_widget):
        """
        Removes a song from the database, removes the GUI element representing the song on the review page, and
        disable the remove button if only one duplicate is left.

        :param song_review_widget: The SongReviewWidget whose song we should delete.
        """
        # Remove song from duplicate song list.
        self.duplicate_song_list[-1].remove(song_review_widget.song)
        # Remove song from the database.
        delete_song(song_review_widget.song.id, self.plugin)
        # Remove GUI elements for the song.
        self.review_scroll_area_layout.removeWidget(song_review_widget)
        song_review_widget.setParent(None)
        # Check if we only have one duplicate left:
        # 2 stretches + 1 SongReviewWidget = 3
        # The SongReviewWidget is then at position 1.
        if len(self.duplicate_song_list[-1]) == 1:
            self.review_scroll_area_layout.itemAt(1).widget().song_remove_button.setEnabled(False)

    def proceed_to_next_review(self):
        """
        Removes the previous review UI elements and calls process_current_duplicate_entry.
        """
        # Remove last duplicate group.
        self.duplicate_song_list.pop()
        # Remove all previous elements.
        for i in reversed(list(range(self.review_scroll_area_layout.count()))):
            item = self.review_scroll_area_layout.itemAt(i)
            if isinstance(item, QtGui.QWidgetItem):
                # The order is important here, if the .setParent(None) call is done
                # before the .removeItem() call, a segfault occurs.
                widget = item.widget()
                self.review_scroll_area_layout.removeItem(item)
                widget.setParent(None)
            else:
                self.review_scroll_area_layout.removeItem(item)
        # Process next set of duplicates.
        self.process_current_duplicate_entry()

    def process_current_duplicate_entry(self):
        """
        Update the review counter in the wizard header, add song widgets for the current duplicate group to review,
        if it's the last duplicate song group, hide the "next" button and show the "finish" button.
        """
        # Update the counter.
        self.review_current_count = self.review_total_count - (len(self.duplicate_song_list) - 1)
        self.update_review_counter_text()
        # Add song elements to the UI.
        if len(self.duplicate_song_list) > 0:
            self.review_scroll_area_layout.addStretch(1)
            for duplicate in self.duplicate_song_list[-1]:
                song_review_widget = SongReviewWidget(self.review_page, duplicate)
                song_review_widget.song_remove_button_clicked.connect(self.remove_button_clicked)
                self.review_scroll_area_layout.addWidget(song_review_widget)
            self.review_scroll_area_layout.addStretch(1)
        # Change next button to finish button on last review.
        if len(self.duplicate_song_list) == 1:
            self.button(QtGui.QWizard.FinishButton).show()
            self.button(QtGui.QWizard.FinishButton).setEnabled(True)
            self.button(QtGui.QWizard.NextButton).hide()
            self.button(QtGui.QWizard.CancelButton).hide()
