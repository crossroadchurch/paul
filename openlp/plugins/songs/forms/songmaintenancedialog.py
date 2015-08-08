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

from PyQt4 import QtCore, QtGui

from openlp.core.common import UiStrings
from openlp.core.lib import build_icon
from openlp.core.lib.ui import create_button_box
from openlp.plugins.songs.lib.ui import SongStrings


class Ui_SongMaintenanceDialog(object):
    """
    The user interface for the song maintenance dialog
    """
    def setupUi(self, song_maintenance_dialog):
        """
        Set up the user interface for the song maintenance dialog
        """
        song_maintenance_dialog.setObjectName('song_maintenance_dialog')
        song_maintenance_dialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        song_maintenance_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        song_maintenance_dialog.resize(10, 350)
        self.dialog_layout = QtGui.QGridLayout(song_maintenance_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.type_list_widget = QtGui.QListWidget(song_maintenance_dialog)
        self.type_list_widget.setIconSize(QtCore.QSize(32, 32))
        self.type_list_widget.setUniformItemSizes(True)
        self.type_list_widget.setObjectName('type_list_widget')
        self.authors_list_item = QtGui.QListWidgetItem(self.type_list_widget)
        self.authors_list_item.setIcon(build_icon(':/songs/author_maintenance.png'))
        self.topics_list_item = QtGui.QListWidgetItem(self.type_list_widget)
        self.topics_list_item.setIcon(build_icon(':/songs/topic_maintenance.png'))
        self.books_list_item = QtGui.QListWidgetItem(self.type_list_widget)
        self.books_list_item.setIcon(build_icon(':/songs/book_maintenance.png'))
        self.dialog_layout.addWidget(self.type_list_widget, 0, 0)
        self.stacked_layout = QtGui.QStackedLayout()
        self.stacked_layout.setObjectName('stacked_layout')
        # authors page
        self.authors_page = QtGui.QWidget(song_maintenance_dialog)
        self.authors_page.setObjectName('authors_page')
        self.authors_layout = QtGui.QVBoxLayout(self.authors_page)
        self.authors_layout.setObjectName('authors_layout')
        self.authors_list_widget = QtGui.QListWidget(self.authors_page)
        self.authors_list_widget.setObjectName('authors_list_widget')
        self.authors_layout.addWidget(self.authors_list_widget)
        self.authors_buttons_layout = QtGui.QHBoxLayout()
        self.authors_buttons_layout.setObjectName('authors_buttons_layout')
        self.authors_buttons_layout.addStretch()
        self.add_author_button = QtGui.QPushButton(self.authors_page)
        self.add_author_button.setIcon(build_icon(':/songs/author_add.png'))
        self.add_author_button.setObjectName('add_author_button')
        self.authors_buttons_layout.addWidget(self.add_author_button)
        self.edit_author_button = QtGui.QPushButton(self.authors_page)
        self.edit_author_button.setIcon(build_icon(':/songs/author_edit.png'))
        self.edit_author_button.setObjectName('edit_author_button')
        self.authors_buttons_layout.addWidget(self.edit_author_button)
        self.delete_author_button = QtGui.QPushButton(self.authors_page)
        self.delete_author_button.setIcon(build_icon(':/songs/author_delete.png'))
        self.delete_author_button.setObjectName('delete_author_button')
        self.authors_buttons_layout.addWidget(self.delete_author_button)
        self.authors_layout.addLayout(self.authors_buttons_layout)
        self.stacked_layout.addWidget(self.authors_page)
        # topics page
        self.topics_page = QtGui.QWidget(song_maintenance_dialog)
        self.topics_page.setObjectName('topics_page')
        self.topics_layout = QtGui.QVBoxLayout(self.topics_page)
        self.topics_layout.setObjectName('topics_layout')
        self.topics_list_widget = QtGui.QListWidget(self.topics_page)
        self.topics_list_widget.setObjectName('topics_list_widget')
        self.topics_layout.addWidget(self.topics_list_widget)
        self.topics_buttons_layout = QtGui.QHBoxLayout()
        self.topics_buttons_layout.setObjectName('topicsButtonLayout')
        self.topics_buttons_layout.addStretch()
        self.add_topic_button = QtGui.QPushButton(self.topics_page)
        self.add_topic_button.setIcon(build_icon(':/songs/topic_add.png'))
        self.add_topic_button.setObjectName('add_topic_button')
        self.topics_buttons_layout.addWidget(self.add_topic_button)
        self.edit_topic_button = QtGui.QPushButton(self.topics_page)
        self.edit_topic_button.setIcon(build_icon(':/songs/topic_edit.png'))
        self.edit_topic_button.setObjectName('edit_topic_button')
        self.topics_buttons_layout.addWidget(self.edit_topic_button)
        self.delete_topic_button = QtGui.QPushButton(self.topics_page)
        self.delete_topic_button.setIcon(build_icon(':/songs/topic_delete.png'))
        self.delete_topic_button.setObjectName('delete_topic_button')
        self.topics_buttons_layout.addWidget(self.delete_topic_button)
        self.topics_layout.addLayout(self.topics_buttons_layout)
        self.stacked_layout.addWidget(self.topics_page)
        # song books page
        self.books_page = QtGui.QWidget(song_maintenance_dialog)
        self.books_page.setObjectName('books_page')
        self.books_layout = QtGui.QVBoxLayout(self.books_page)
        self.books_layout.setObjectName('books_layout')
        self.song_books_list_widget = QtGui.QListWidget(self.books_page)
        self.song_books_list_widget.setObjectName('song_books_list_widget')
        self.books_layout.addWidget(self.song_books_list_widget)
        self.books_buttons_layout = QtGui.QHBoxLayout()
        self.books_buttons_layout.setObjectName('booksButtonLayout')
        self.books_buttons_layout.addStretch()
        self.add_book_button = QtGui.QPushButton(self.books_page)
        self.add_book_button.setIcon(build_icon(':/songs/book_add.png'))
        self.add_book_button.setObjectName('add_book_button')
        self.books_buttons_layout.addWidget(self.add_book_button)
        self.edit_book_button = QtGui.QPushButton(self.books_page)
        self.edit_book_button.setIcon(build_icon(':/songs/book_edit.png'))
        self.edit_book_button.setObjectName('edit_book_button')
        self.books_buttons_layout.addWidget(self.edit_book_button)
        self.delete_book_button = QtGui.QPushButton(self.books_page)
        self.delete_book_button.setIcon(build_icon(':/songs/book_delete.png'))
        self.delete_book_button.setObjectName('delete_book_button')
        self.books_buttons_layout.addWidget(self.delete_book_button)
        self.books_layout.addLayout(self.books_buttons_layout)
        self.stacked_layout.addWidget(self.books_page)
        #
        self.dialog_layout.addLayout(self.stacked_layout, 0, 1)
        self.button_box = create_button_box(song_maintenance_dialog, 'button_box', ['close'])
        self.dialog_layout.addWidget(self.button_box, 1, 0, 1, 2)
        self.retranslateUi(song_maintenance_dialog)
        self.stacked_layout.setCurrentIndex(0)
        self.type_list_widget.currentRowChanged.connect(self.stacked_layout.setCurrentIndex)

    def retranslateUi(self, song_maintenance_dialog):
        """
        Translate the UI on the fly.
        """
        song_maintenance_dialog.setWindowTitle(SongStrings.SongMaintenance)
        self.authors_list_item.setText(SongStrings.Authors)
        self.topics_list_item.setText(SongStrings.Topics)
        self.books_list_item.setText(SongStrings.SongBooks)
        self.add_author_button.setText(UiStrings().Add)
        self.edit_author_button.setText(UiStrings().Edit)
        self.delete_author_button.setText(UiStrings().Delete)
        self.add_topic_button.setText(UiStrings().Add)
        self.edit_topic_button.setText(UiStrings().Edit)
        self.delete_topic_button.setText(UiStrings().Delete)
        self.add_book_button.setText(UiStrings().Add)
        self.edit_book_button.setText(UiStrings().Edit)
        self.delete_book_button.setText(UiStrings().Delete)
        type_list_width = max(self.fontMetrics().width(SongStrings.Authors),
                              self.fontMetrics().width(SongStrings.Topics),
                              self.fontMetrics().width(SongStrings.SongBooks))
        self.type_list_widget.setFixedWidth(type_list_width + self.type_list_widget.iconSize().width() + 32)
