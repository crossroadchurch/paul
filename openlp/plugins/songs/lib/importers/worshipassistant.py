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
The :mod:`worshipassistant` module provides the functionality for importing
Worship Assistant songs into the OpenLP database.
"""
import chardet
import csv
import logging
import re

from openlp.core.common import translate
from openlp.plugins.songs.lib import VerseType
from openlp.plugins.songs.lib.importers.songimport import SongImport

log = logging.getLogger(__name__)

EMPTY_STR = 'NULL'


class WorshipAssistantImport(SongImport):
    """
    The :class:`WorshipAssistantImport` class provides the ability to import songs
    from Worship Assistant, via a dump of the database to a CSV file.

    The following fields are in the exported CSV file:

    * ``SONGNR`` Song ID (Discarded by importer)
    * ``TITLE`` Song title
    * ``AUTHOR`` Song author.
    * ``COPYRIGHT`` Copyright information
    * ``FIRSTLINE`` Unknown (Discarded by importer)
    * ``PRIKEY`` Primary chord key (Discarded by importer)
    * ``ALTKEY`` Alternate chord key (Discarded by importer)
    * ``TEMPO`` Tempo (Discarded by importer)
    * ``FOCUS`` Unknown (Discarded by importer)
    * ``THEME`` Theme (Discarded by importer)
    * ``SCRIPTURE`` Associated scripture (Discarded by importer)
    * ``ACTIVE`` Boolean value (Discarded by importer)
    * ``SONGBOOK`` Boolean value (Discarded by importer)
    * ``TIMESIG`` Unknown (Discarded by importer)
    * ``INTRODUCED`` Date the song was created (Discarded by importer)
    * ``LASTUSED`` Date the song was last used (Discarded by importer)
    * ``TIMESUSED`` How many times the song was used (Discarded by importer)
    * ``CCLINR`` CCLI Number
    * ``USER1`` User Field 1 (Discarded by importer)
    * ``USER2`` User Field 2 (Discarded by importer)
    * ``USER3`` User Field 3 (Discarded by importer)
    * ``USER4`` User Field 4 (Discarded by importer)
    * ``USER5`` User Field 5 (Discarded by importer)
    * ``ROADMAP`` Verse order used for the presentation
    * ``FILELINK1`` Associated file 1 (Discarded by importer)
    * ``OVERMAP`` Verse order used for printing (Discarded by importer)
    * ``FILELINK2`` Associated file 2 (Discarded by importer)
    * ``LYRICS`` The song lyrics used for printing (Discarded by importer, LYRICS2 is used instead)
    * ``INFO`` Unknown (Discarded by importer)
    * ``LYRICS2`` The song lyrics used for the presentation
    * ``BACKGROUND`` Custom background (Discarded by importer)
    """
    def do_import(self):
        """
        Receive a CSV file to import.
        """
        # Get encoding
        detect_file = open(self.import_source, 'rb')
        detect_content = detect_file.read()
        details = chardet.detect(detect_content)
        detect_file.close()
        songs_file = open(self.import_source, 'r', encoding=details['encoding'])
        songs_reader = csv.DictReader(songs_file, escapechar='\\')
        try:
            records = list(songs_reader)
        except csv.Error as e:
            self.log_error(translate('SongsPlugin.WorshipAssistantImport', 'Error reading CSV file.'),
                           translate('SongsPlugin.WorshipAssistantImport', 'Line %d: %s') %
                           (songs_reader.line_num, e))
            return
        num_records = len(records)
        log.info('%s records found in CSV file' % num_records)
        self.import_wizard.progress_bar.setMaximum(num_records)
        # Create regex to strip html tags
        re_html_strip = re.compile(r'<[^>]+>')
        for index, record in enumerate(records, 1):
            if self.stop_import_flag:
                return
            # Ensure that all keys are uppercase
            record = dict((field.upper(), value) for field, value in record.items())
            # The CSV file has a line in the middle of the file where the headers are repeated.
            #  We need to skip this line.
            if record['TITLE'] == "TITLE" and record['AUTHOR'] == 'AUTHOR' and record['LYRICS2'] == 'LYRICS2':
                continue
            self.set_defaults()
            verse_order_list = []
            try:
                self.title = record['TITLE']
                if record['AUTHOR'] != EMPTY_STR:
                    self.parse_author(record['AUTHOR'])
                if record['COPYRIGHT'] != EMPTY_STR:
                    self.add_copyright(record['COPYRIGHT'])
                if record['CCLINR'] != EMPTY_STR:
                    self.ccli_number = record['CCLINR']
                if record['ROADMAP'] != EMPTY_STR:
                    verse_order_list = [x.strip() for x in record['ROADMAP'].split(',')]
                lyrics = record['LYRICS2']
            except UnicodeDecodeError as e:
                self.log_error(translate('SongsPlugin.WorshipAssistantImport', 'Record %d' % index),
                               translate('SongsPlugin.WorshipAssistantImport', 'Decoding error: %s') % e)
                continue
            except TypeError as e:
                self.log_error(translate('SongsPlugin.WorshipAssistantImport',
                                         'File not valid WorshipAssistant CSV format.'), 'TypeError: %s' % e)
                return
            verse = ''
            used_verses = []
            verse_id = VerseType.tags[VerseType.Verse] + '1'
            for line in lyrics.splitlines():
                if line.startswith('['):  # verse marker
                    # Add previous verse
                    if verse:
                        # remove trailing linebreak, part of the WA syntax
                        self.add_verse(verse[:-1], verse_id)
                        used_verses.append(verse_id)
                        verse = ''
                    # drop the square brackets
                    right_bracket = line.find(']')
                    content = line[1:right_bracket].lower()
                    match = re.match('(\D*)(\d+)', content)
                    if match is not None:
                        verse_tag = match.group(1)
                        verse_num = match.group(2)
                    else:
                        # otherwise we assume number 1 and take the whole prefix as the verse tag
                        verse_tag = content
                        verse_num = '1'
                    verse_index = VerseType.from_loose_input(verse_tag) if verse_tag else 0
                    verse_tag = VerseType.tags[verse_index]
                    # Update verse order when the verse name has changed
                    verse_id = verse_tag + verse_num
                    # Make sure we've not choosen an id already used
                    while verse_id in verse_order_list and content in verse_order_list:
                        verse_num = str(int(verse_num) + 1)
                        verse_id = verse_tag + verse_num
                    if content != verse_id:
                        for i in range(len(verse_order_list)):
                            if verse_order_list[i].lower() == content.lower():
                                verse_order_list[i] = verse_id
                else:
                    # add line text to verse. Strip out html
                    verse += re_html_strip.sub('', line) + '\n'
            if verse:
                # remove trailing linebreak, part of the WA syntax
                if verse.endswith('\n\n'):
                    verse = verse[:-1]
                self.add_verse(verse, verse_id)
                used_verses.append(verse_id)
            if verse_order_list:
                # Use the verse order in the import, but remove entries that doesn't have a text
                cleaned_verse_order_list = []
                for verse in verse_order_list:
                    if verse in used_verses:
                        cleaned_verse_order_list.append(verse)
                self.verse_order_list = cleaned_verse_order_list
            if not self.finish():
                self.log_error(translate('SongsPlugin.WorshipAssistantImport', 'Record %d') % index +
                               (': "' + self.title + '"' if self.title else ''))
            songs_file.close()
