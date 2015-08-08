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
The :mod:`songshowplus` module provides the functionality for importing SongShow Plus songs into the OpenLP
database.
"""
import chardet
import os
import logging
import re
import struct

from openlp.core.ui.wizard import WizardStrings
from openlp.plugins.songs.lib import VerseType, retrieve_windows_encoding
from openlp.plugins.songs.lib.importers.songimport import SongImport

TITLE = 1
AUTHOR = 2
COPYRIGHT = 3
CCLI_NO = 5
VERSE = 12
CHORUS = 20
BRIDGE = 24
TOPIC = 29
COMMENTS = 30
VERSE_ORDER = 31
SONG_BOOK = 35
SONG_NUMBER = 36
CUSTOM_VERSE = 37

log = logging.getLogger(__name__)


class SongShowPlusImport(SongImport):
    """
    The :class:`SongShowPlusImport` class provides the ability to import song files from SongShow Plus.

    **SongShow Plus Song File Format:**

    The SongShow Plus song file format is as follows:

    * Each piece of data in the song file has some information that precedes it.
    * The general format of this data is as follows:
    4 Bytes, forming a 32 bit number, a key if you will, this describes what the data is (see blockKey below)
    4 Bytes, forming a 32 bit number, which is the number of bytes until the next block starts
    1 Byte, which tells how many bytes follows
    1 or 4 Bytes, describes how long the string is, if its 1 byte, the string is less than 255
    The next bytes are the actual data.
    The next block of data follows on.

    This description does differ for verses. Which includes extra bytes stating the verse type or number. In some cases
    a "custom" verse is used, in that case, this block will in include 2 strings, with the associated string length
    descriptors. The first string is the name of the verse, the second is the verse content.

    The file is ended with four null bytes.

    Valid extensions for a SongShow Plus song file are:

    * .sbsong
    """

    other_count = 0
    other_list = {}

    def __init__(self, manager, **kwargs):
        """
        Initialise the SongShow Plus importer.
        """
        super(SongShowPlusImport, self).__init__(manager, **kwargs)

    def do_import(self):
        """
        Receive a single file or a list of files to import.
        """
        if not isinstance(self.import_source, list):
            return
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for file in self.import_source:
            if self.stop_import_flag:
                return
            self.ssp_verse_order_list = []
            self.other_count = 0
            self.other_list = {}
            file_name = os.path.split(file)[1]
            self.import_wizard.increment_progress_bar(WizardStrings.ImportingType % file_name, 0)
            song_data = open(file, 'rb')
            while True:
                block_key, = struct.unpack("I", song_data.read(4))
                # The file ends with 4 NULL's
                if block_key == 0:
                    break
                next_block_starts, = struct.unpack("I", song_data.read(4))
                next_block_starts += song_data.tell()
                if block_key in (VERSE, CHORUS, BRIDGE):
                    null, verse_no, = struct.unpack("BB", song_data.read(2))
                elif block_key == CUSTOM_VERSE:
                    null, verse_name_length, = struct.unpack("BB", song_data.read(2))
                    verse_name = self.decode(song_data.read(verse_name_length))
                length_descriptor_size, = struct.unpack("B", song_data.read(1))
                log.debug(length_descriptor_size)
                # Detect if/how long the length descriptor is
                if length_descriptor_size == 12 or length_descriptor_size == 20:
                    length_descriptor, = struct.unpack("I", song_data.read(4))
                elif length_descriptor_size == 2:
                    length_descriptor = 1
                elif length_descriptor_size == 9:
                    length_descriptor = 0
                else:
                    length_descriptor, = struct.unpack("B", song_data.read(1))
                log.debug(length_descriptor_size)
                data = song_data.read(length_descriptor)
                if block_key == TITLE:
                    self.title = self.decode(data)
                elif block_key == AUTHOR:
                    authors = self.decode(data).split(" / ")
                    for author in authors:
                        if author.find(",") != -1:
                            author_parts = author.split(", ")
                            author = author_parts[1] + " " + author_parts[0]
                        self.parse_author(author)
                elif block_key == COPYRIGHT:
                    self.add_copyright(self.decode(data))
                elif block_key == CCLI_NO:
                    # Try to get the CCLI number even if the field contains additional text
                    match = re.search(r'\d+', self.decode(data))
                    if match:
                        self.ccli_number = int(match.group())
                    else:
                        log.warning("Can't parse CCLI Number from string: %s" % self.decode(data))
                elif block_key == VERSE:
                    self.add_verse(self.decode(data), "%s%s" % (VerseType.tags[VerseType.Verse], verse_no))
                elif block_key == CHORUS:
                    self.add_verse(self.decode(data), "%s%s" % (VerseType.tags[VerseType.Chorus], verse_no))
                elif block_key == BRIDGE:
                    self.add_verse(self.decode(data), "%s%s" % (VerseType.tags[VerseType.Bridge], verse_no))
                elif block_key == TOPIC:
                    self.topics.append(self.decode(data))
                elif block_key == COMMENTS:
                    self.comments = self.decode(data)
                elif block_key == VERSE_ORDER:
                    verse_tag = self.to_openlp_verse_tag(self.decode(data), True)
                    if verse_tag:
                        if not isinstance(verse_tag, str):
                            verse_tag = self.decode(verse_tag)
                        self.ssp_verse_order_list.append(verse_tag)
                elif block_key == SONG_BOOK:
                    self.song_book_name = self.decode(data)
                elif block_key == SONG_NUMBER:
                    self.song_number = ord(data)
                elif block_key == CUSTOM_VERSE:
                    verse_tag = self.to_openlp_verse_tag(verse_name)
                    self.add_verse(self.decode(data), verse_tag)
                else:
                    log.debug("Unrecognised blockKey: %s, data: %s" % (block_key, data))
                    song_data.seek(next_block_starts)
            self.verse_order_list = self.ssp_verse_order_list
            song_data.close()
            if not self.finish():
                self.log_error(file)

    def to_openlp_verse_tag(self, verse_name, ignore_unique=False):
        """
        Handle OpenLP verse tags

        :param verse_name: The verse name
        :param ignore_unique: Ignore if unique
        :return: The verse tags and verse number concatenated
        """
        # Have we got any digits? If so, verse number is everything from the digits to the end (OpenLP does not have
        # concept of part verses, so just ignore any non integers on the end (including floats))
        match = re.match(r'(\D*)(\d+)', verse_name)
        if match:
            verse_type = match.group(1).strip()
            verse_number = match.group(2)
        else:
            # otherwise we assume number 1 and take the whole prefix as the verse tag
            verse_type = verse_name
            verse_number = '1'
        verse_type = verse_type.lower()
        if verse_type == "verse":
            verse_tag = VerseType.tags[VerseType.Verse]
        elif verse_type == "chorus":
            verse_tag = VerseType.tags[VerseType.Chorus]
        elif verse_type == "bridge":
            verse_tag = VerseType.tags[VerseType.Bridge]
        elif verse_type == "pre-chorus":
            verse_tag = VerseType.tags[VerseType.PreChorus]
        else:
            if verse_name not in self.other_list:
                if ignore_unique:
                    return None
                self.other_count += 1
                self.other_list[verse_name] = str(self.other_count)
            verse_tag = VerseType.tags[VerseType.Other]
            verse_number = self.other_list[verse_name]
        return verse_tag + verse_number

    def decode(self, data):
        try:
            return str(data, chardet.detect(data)['encoding'])
        except:
            return str(data, retrieve_windows_encoding())
