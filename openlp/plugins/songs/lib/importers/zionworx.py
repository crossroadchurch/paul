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
The :mod:`zionworx` module provides the functionality for importing ZionWorx songs into the OpenLP database.
"""
import csv
import logging

from openlp.core.common import translate
from openlp.plugins.songs.lib.importers.songimport import SongImport

log = logging.getLogger(__name__)

# Used to strip control chars (except 10=LF, 13=CR)
CONTROL_CHARS_MAP = dict.fromkeys(list(range(10)) + [11, 12] + list(range(14, 32)) + [127])


class ZionWorxImport(SongImport):
    """
    The :class:`ZionWorxImport` class provides the ability to import songs
    from ZionWorx, via a dump of the ZionWorx database to a CSV file.

    ZionWorx song database fields:

    * ``SongNum`` Song ID. (Discarded by importer)
    * ``Title1`` Main Title.
    * ``Title2`` Alternate Title.
    * ``Lyrics`` Song verses, separated by blank lines.
    * ``Writer`` Song author(s).
    * ``Copyright`` Copyright information
    * ``Keywords`` (Discarded by importer)
    * ``DefaultStyle`` (Discarded by importer)

    ZionWorx has no native export function; it uses the proprietary TurboDB
    database engine. The TurboDB vendor, dataWeb, provides tools which can
    export TurboDB tables to other formats, such as freeware console tool
    TurboDB Data Exchange which is available for Windows and Linux. This command
    exports the ZionWorx songs table to a CSV file:

    ``tdbdatax MainTable.dat songstable.csv -fsdf -s, -qd``

    * -f  Table format: ``sdf`` denotes text file.
    * -s  Separator character between fields.
    * -q  Quote character surrounding fields. ``d`` denotes double-quote.

    CSV format expected by importer:

    * Field separator character is comma ``,``
    * Fields surrounded by double-quotes ``"``. This enables fields (such as
      Lyrics) to include new-lines and commas. Double-quotes within a field
      are denoted by two double-quotes ``""``
    * Note: This is the default format of the Python ``csv`` module.

    """
    def do_import(self):
        """
        Receive a CSV file (from a ZionWorx database dump) to import.
        """
        with open(self.import_source, 'rb') as songs_file:
            field_names = ['SongNum', 'Title1', 'Title2', 'Lyrics', 'Writer', 'Copyright', 'Keywords',
                           'DefaultStyle']
            songs_reader = csv.DictReader(songs_file, field_names)
            try:
                records = list(songs_reader)
            except csv.Error as e:
                self.log_error(translate('SongsPlugin.ZionWorxImport', 'Error reading CSV file.'),
                               translate('SongsPlugin.ZionWorxImport', 'Line %d: %s') % (songs_reader.line_num, e))
                return
            num_records = len(records)
            log.info('%s records found in CSV file' % num_records)
            self.import_wizard.progress_bar.setMaximum(num_records)
            for index, record in enumerate(records, 1):
                if self.stop_import_flag:
                    return
                self.set_defaults()
                try:
                    self.title = self._decode(record['Title1'])
                    if record['Title2']:
                        self.alternate_title = self._decode(record['Title2'])
                    self.parse_author(self._decode(record['Writer']))
                    self.add_copyright(self._decode(record['Copyright']))
                    lyrics = self._decode(record['Lyrics'])
                except UnicodeDecodeError as e:
                    self.log_error(translate('SongsPlugin.ZionWorxImport', 'Record %d' % index),
                                   translate('SongsPlugin.ZionWorxImport', 'Decoding error: %s') % e)
                    continue
                except TypeError as e:
                    self.log_error(translate(
                        'SongsPlugin.ZionWorxImport', 'File not valid ZionWorx CSV format.'), 'TypeError: %s' % e)
                    return
                verse = ''
                for line in lyrics.splitlines():
                    if line and not line.isspace():
                        verse += line + '\n'
                    elif verse:
                        self.add_verse(verse)
                        verse = ''
                if verse:
                    self.add_verse(verse)
                title = self.title
                if not self.finish():
                    self.log_error(translate('SongsPlugin.ZionWorxImport', 'Record %d') % index +
                                   (': "' + title + '"' if title else ''))

    def _decode(self, str):
        """
        Decodes CSV input to unicode, stripping all control characters (except new lines).
        """
        # This encoding choice seems OK. ZionWorx has no option for setting the
        # encoding for its songs, so we assume encoding is always the same.
        return str(str, 'cp1252').translate(CONTROL_CHARS_MAP)
