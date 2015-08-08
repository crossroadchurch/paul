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
The :mod:`mediashout` module provides the functionality for importing
a MediaShout database into the OpenLP database.
"""
import pyodbc

from openlp.core.lib import translate
from openlp.plugins.songs.lib.importers.songimport import SongImport

VERSE_TAGS = ['V', 'C', 'B', 'O', 'P', 'I', 'E']


class MediaShoutImport(SongImport):
    """
    The :class:`MediaShoutImport` class provides the ability to import the
    MediaShout Access Database
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the MediaShout importer.
        """
        SongImport.__init__(self, manager, **kwargs)

    def do_import(self):
        """
        Receive a single file to import.
        """
        try:
            conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s;PWD=6NOZ4eHK7k' %
                                  self.import_source)
        except:
            # Unfortunately no specific exception type
            self.log_error(self.import_source, translate('SongsPlugin.MediaShoutImport',
                                                         'Unable to open the MediaShout database.'))
            return
        cursor = conn.cursor()
        cursor.execute('SELECT Record, Title, Author, Copyright, SongID, CCLI, Notes FROM Songs ORDER BY Title')
        songs = cursor.fetchall()
        self.import_wizard.progress_bar.setMaximum(len(songs))
        for song in songs:
            if self.stop_import_flag:
                break
            cursor.execute('SELECT Type, Number, Text FROM Verses WHERE Record = %s ORDER BY Type, Number'
                           % song.Record)
            verses = cursor.fetchall()
            cursor.execute('SELECT Type, Number, POrder FROM PlayOrder WHERE Record = %s ORDER BY POrder' % song.Record)
            verse_order = cursor.fetchall()
            cursor.execute('SELECT Name FROM Themes INNER JOIN SongThemes ON SongThemes.ThemeId = Themes.ThemeId '
                           'WHERE SongThemes.Record = %s' % song.Record)
            topics = cursor.fetchall()
            cursor.execute('SELECT Name FROM Groups INNER JOIN SongGroups ON SongGroups.GroupId = Groups.GroupId '
                           'WHERE SongGroups.Record = %s' % song.Record)
            topics += cursor.fetchall()
            self.process_song(song, verses, verse_order, topics)

    def process_song(self, song, verses, verse_order, topics):
        """
        Create the song, i.e. title, verse etc.
        """
        self.set_defaults()
        self.title = song.Title
        self.parse_author(song.Author)
        self.add_copyright(song.Copyright)
        self.comments = song.Notes
        for topic in topics:
            self.topics.append(topic.Name)
        if '-' in song.SongID:
            self.song_book_name, self.song_number = song.SongID.split('-', 1)
        else:
            self.song_book_name = song.SongID
        for verse in verses:
            tag = VERSE_TAGS[verse.Type] + str(verse.Number) if verse.Type < len(VERSE_TAGS) else 'O'
            self.add_verse(verse.Text, tag)
        for order in verse_order:
            if order.Type < len(VERSE_TAGS):
                self.verse_order_list.append(VERSE_TAGS[order.Type] + str(order.Number))
        self.finish()
