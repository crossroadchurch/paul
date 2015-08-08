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
The :mod:`worshipcenterpro` module provides the functionality for importing
a WorshipCenter Pro database into the OpenLP database.
"""
import logging

import pyodbc

from openlp.core.common import translate
from openlp.plugins.songs.lib.importers.songimport import SongImport

log = logging.getLogger(__name__)


class WorshipCenterProImport(SongImport):
    """
    The :class:`WorshipCenterProImport` class provides the ability to import the
    WorshipCenter Pro Access Database
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the WorshipCenter Pro importer.
        """
        super(WorshipCenterProImport, self).__init__(manager, **kwargs)

    def do_import(self):
        """
        Receive a single file to import.
        """
        try:
            conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s' % self.import_source)
        except (pyodbc.DatabaseError, pyodbc.IntegrityError, pyodbc.InternalError, pyodbc.OperationalError) as e:
            log.warning('Unable to connect the WorshipCenter Pro database %s. %s', self.import_source, str(e))
            # Unfortunately no specific exception type
            self.log_error(self.import_source, translate('SongsPlugin.WorshipCenterProImport',
                                                         'Unable to connect the WorshipCenter Pro database.'))
            return
        cursor = conn.cursor()
        cursor.execute('SELECT ID, Field, Value FROM __SONGDATA')
        records = cursor.fetchall()
        songs = {}
        for record in records:
            id = record.ID
            if id not in songs:
                songs[id] = {}
            songs[id][record.Field] = record.Value
        self.import_wizard.progress_bar.setMaximum(len(songs))
        for song in songs:
            if self.stop_import_flag:
                break
            self.set_defaults()
            self.title = songs[song]['TITLE']
            lyrics = songs[song]['LYRICS'].strip('&crlf;&crlf;')
            for verse in lyrics.split('&crlf;&crlf;'):
                verse = verse.replace('&crlf;', '\n')
                self.add_verse(verse)
            self.finish()
