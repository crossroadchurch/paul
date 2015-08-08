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
The :mod:`easyworship` module provides the functionality for importing EasyWorship song databases into OpenLP.
"""

import os
import struct
import re
import zlib

from openlp.core.lib import translate
from openlp.plugins.songs.lib import VerseType
from openlp.plugins.songs.lib import retrieve_windows_encoding, strip_rtf
from .songimport import SongImport

# regex: at least two newlines, can have spaces between them
SLIDE_BREAK_REGEX = re.compile(r'\n *?\n[\n ]*')
NUMBER_REGEX = re.compile(r'[0-9]+')
NOTE_REGEX = re.compile(r'\(.*?\)')


class FieldDescEntry:
    def __init__(self, name, field_type, size):
        self.name = name
        self.field_type = field_type
        self.size = size


class FieldType(object):
    """
    An enumeration class for different field types that can be expected in an EasyWorship song file.
    """
    String = 1
    Int16 = 3
    Int32 = 4
    Logical = 9
    Memo = 0x0c
    Blob = 0x0d
    Timestamp = 0x15


class EasyWorshipSongImport(SongImport):
    """
    The :class:`EasyWorshipSongImport` class provides OpenLP with the
    ability to import EasyWorship song files.
    """
    def __init__(self, manager, **kwargs):
        super(EasyWorshipSongImport, self).__init__(manager, **kwargs)
        self.entry_error_log = ''

    def do_import(self):
        """
        Determines the type of file to import and calls the appropiate method
        """
        if self.import_source.lower().endswith('ews'):
            self.import_ews()
        else:
            self.import_db()

    def import_ews(self):
        """
        Import the songs from service file
        The full spec of the ews files can be found here:
        https://github.com/meinders/lithium-ews/blob/master/docs/ews%20file%20format.md
        or here: http://wiki.openlp.org/Development:EasyWorship_EWS_Format
        """
        # Open ews file if it exists
        if not os.path.isfile(self.import_source):
            log.debug('Given ews file does not exists.')
            return
        # Make sure there is room for at least a header and one entry
        if os.path.getsize(self.import_source) < 892:
            log.debug('Given ews file is to small to contain valid data.')
            return
        # Take a stab at how text is encoded
        self.encoding = 'cp1252'
        self.encoding = retrieve_windows_encoding(self.encoding)
        if not self.encoding:
            log.debug('No encoding set.')
            return
        self.ews_file = open(self.import_source, 'rb')
        # EWS header, version '1.6'/'  3'/'  5':
        # Offset   Field             Data type    Length    Details
        # --------------------------------------------------------------------------------------------------
        #       0  Filetype           string           38    Specifies the file type and version.
        #                                                   "EasyWorship Schedule File Version  1.6" or
        #                                                   "EasyWorship Schedule File Version    3" or
        #                                                   "EasyWorship Schedule File Version    5"
        # 40/48/56 Entry count        int32le           4    Number of items in the schedule
        # 44/52/60 Entry length       int16le           2    Length of schedule entries: 0x0718 = 1816
        # Get file version
        type, = struct.unpack('<38s', self.ews_file.read(38))
        version = type.decode()[-3:]
        # Set fileposition based on filetype/version
        file_pos = 0
        if version == '  5':
            file_pos = 56
        elif version == '  3':
            file_pos = 48
        elif version == '1.6':
            file_pos = 40
        else:
            log.debug('Given ews file is of unknown version.')
            return
        entry_count = self.get_i32(file_pos)
        entry_length = self.get_i16(file_pos+4)
        file_pos += 6
        self.import_wizard.progress_bar.setMaximum(entry_count)
        # Loop over songs
        for i in range(entry_count):
            # Load EWS entry metadata:
            # Offset  Field                  Data type    Length    Details
            # ------------------------------------------------------------------------------------------------
            #      0  Title                  cstring          50
            #    307  Author                 cstring          50
            #    358  Copyright              cstring         100
            #    459  Administrator          cstring          50
            #    800  Content pointer        int32le           4    Position of the content for this entry.
            #    820  Content type           int32le           4    0x01 = Song, 0x02 = Scripture, 0x03 = Presentation,
            #                                                       0x04 = Video, 0x05 = Live video, 0x07 = Image,
            #                                                       0x08 = Audio, 0x09 = Web
            #   1410  Song number            cstring          10
            self.set_defaults()
            self.title = self.get_string(file_pos + 0, 50)
            authors = self.get_string(file_pos + 307, 50)
            copyright = self.get_string(file_pos + 358, 100)
            admin = self.get_string(file_pos + 459, 50)
            cont_ptr = self.get_i32(file_pos + 800)
            cont_type = self.get_i32(file_pos + 820)
            self.ccli_number = self.get_string(file_pos + 1410, 10)
            # Only handle content type 1 (songs)
            if cont_type != 1:
                file_pos += entry_length
                continue
            # Load song content
            # Offset  Field              Data type    Length    Details
            # ------------------------------------------------------------------------------------------------
            #      0  Length             int32le           4    Length (L) of content, including the compressed content
            #                                                   and the following fields (14 bytes total).
            #      4  Content            string         L-14    Content compressed with deflate.
            #         Checksum           int32be           4    Alder-32 checksum.
            #         (unknown)                            4    0x51 0x4b 0x03 0x04
            #         Content length     int32le           4    Length of content after decompression
            content_length = self.get_i32(cont_ptr)
            deflated_content = self.get_bytes(cont_ptr + 4, content_length - 10)
            deflated_length = self.get_i32(cont_ptr + 4 + content_length - 6)
            inflated_content = zlib.decompress(deflated_content, 15, deflated_length)
            if copyright:
                self.copyright = copyright
            if admin:
                if copyright:
                    self.copyright += ', '
                self.copyright += translate('SongsPlugin.EasyWorshipSongImport',
                                            'Administered by %s') % admin
            # Set the SongImport object members.
            self.set_song_import_object(authors, inflated_content)
            if self.stop_import_flag:
                break
            if self.entry_error_log:
                self.log_error(self.import_source,
                               translate('SongsPlugin.EasyWorshipSongImport', '"%s" could not be imported. %s')
                               % (self.title, self.entry_error_log))
                self.entry_error_log = ''
            elif not self.finish():
                self.log_error(self.import_source)
            # Set file_pos for next entry
            file_pos += entry_length
        self.ews_file.close()

    def import_db(self):
        """
        Import the songs from the database
        """
        # Open the DB and MB files if they exist
        import_source_mb = self.import_source.replace('.DB', '.MB').replace('.db', '.mb')
        if not os.path.isfile(self.import_source):
            self.log_error(self.import_source, translate('SongsPlugin.EasyWorshipSongImport',
                                                         'This file does not exist.'))
            return
        if not os.path.isfile(import_source_mb):
            self.log_error(self.import_source, translate('SongsPlugin.EasyWorshipSongImport',
                                                         'Could not find the "Songs.MB" file. It must be in the same '
                                                         'folder as the "Songs.DB" file.'))
            return
        db_size = os.path.getsize(self.import_source)
        if db_size < 0x800:
            self.log_error(self.import_source, translate('SongsPlugin.EasyWorshipSongImport',
                                                         'This file is not a valid EasyWorship database.'))
            return
        db_file = open(self.import_source, 'rb')
        self.memo_file = open(import_source_mb, 'rb')
        # Don't accept files that are clearly not paradox files
        record_size, header_size, block_size, first_block, num_fields = struct.unpack('<hhxb8xh17xh', db_file.read(35))
        if header_size != 0x800 or block_size < 1 or block_size > 4:
            db_file.close()
            self.memo_file.close()
            self.log_error(self.import_source, translate('SongsPlugin.EasyWorshipSongImport',
                                                         'This file is not a valid EasyWorship database.'))
            return
        # Take a stab at how text is encoded
        self.encoding = 'cp1252'
        db_file.seek(106)
        code_page, = struct.unpack('<h', db_file.read(2))
        if code_page == 852:
            self.encoding = 'cp1250'
        # The following codepage to actual encoding mappings have not been
        # observed, but merely guessed. Actual example files are needed.
        elif code_page == 737:
            self.encoding = 'cp1253'
        elif code_page == 775:
            self.encoding = 'cp1257'
        elif code_page == 855:
            self.encoding = 'cp1251'
        elif code_page == 857:
            self.encoding = 'cp1254'
        elif code_page == 866:
            self.encoding = 'cp1251'
        elif code_page == 869:
            self.encoding = 'cp1253'
        elif code_page == 862:
            self.encoding = 'cp1255'
        elif code_page == 874:
            self.encoding = 'cp874'
        self.encoding = retrieve_windows_encoding(self.encoding)
        if not self.encoding:
            self.log_error(self.import_source, translate('SongsPlugin.EasyWorshipSongImport',
                                                         'Could not retrieve encoding.'))
            return
        # Read the field description information
        db_file.seek(120)
        field_info = db_file.read(num_fields * 2)
        db_file.seek(4 + (num_fields * 4) + 261, os.SEEK_CUR)
        field_names = db_file.read(header_size - db_file.tell()).split(b'\0', num_fields)
        field_names.pop()
        field_descriptions = []
        for i, field_name in enumerate(field_names):
            field_type, field_size = struct.unpack_from('BB', field_info, i * 2)
            field_descriptions.append(FieldDescEntry(field_name, field_type, field_size))
        self.set_record_struct(field_descriptions)
        # Pick out the field description indexes we will need
        try:
            success = True
            fi_title = self.find_field(b'Title')
            fi_author = self.find_field(b'Author')
            fi_copy = self.find_field(b'Copyright')
            fi_admin = self.find_field(b'Administrator')
            fi_words = self.find_field(b'Words')
            fi_ccli = self.find_field(b'Song Number')
        except IndexError:
            # This is the wrong table
            success = False
        # There does not appear to be a _reliable_ way of getting the number of songs/records, so loop through the file
        # blocks and total the number of records. Store the information in a list so we dont have to do all this again.
        cur_block = first_block
        total_count = 0
        block_list = []
        while cur_block != 0 and success:
            cur_block_pos = header_size + ((cur_block - 1) * 1024 * block_size)
            db_file.seek(cur_block_pos)
            cur_block, rec_count = struct.unpack('<h2xh', db_file.read(6))
            rec_count = (rec_count + record_size) // record_size
            block_list.append((cur_block_pos, rec_count))
            total_count += rec_count
        self.import_wizard.progress_bar.setMaximum(total_count)
        for block in block_list:
            cur_block_pos, rec_count = block
            db_file.seek(cur_block_pos + 6)
            # Loop through each record within the current block
            for i in range(rec_count):
                if self.stop_import_flag:
                    break
                raw_record = db_file.read(record_size)
                self.fields = self.record_structure.unpack(raw_record)
                self.set_defaults()
                self.title = self.get_field(fi_title).decode('unicode-escape')
                # Get remaining fields.
                copy = self.get_field(fi_copy)
                admin = self.get_field(fi_admin)
                ccli = self.get_field(fi_ccli)
                authors = self.get_field(fi_author)
                words = self.get_field(fi_words)
                if copy:
                    self.copyright = copy.decode('unicode-escape')
                if admin:
                    if copy:
                        self.copyright += ', '
                    self.copyright += translate('SongsPlugin.EasyWorshipSongImport',
                                                'Administered by %s') % admin.decode('unicode-escape')
                if ccli:
                    self.ccli_number = ccli.decode('unicode-escape')
                if authors:
                    authors = authors.decode('unicode-escape')
                else:
                    authors = ''
                # Set the SongImport object members.
                self.set_song_import_object(authors, words)
                if self.stop_import_flag:
                    break
                if self.entry_error_log:
                    self.log_error(self.import_source,
                                   translate('SongsPlugin.EasyWorshipSongImport', '"%s" could not be imported. %s')
                                   % (self.title, self.entry_error_log))
                    self.entry_error_log = ''
                elif not self.finish():
                    self.log_error(self.import_source)
        db_file.close()
        self.memo_file.close()

    def set_song_import_object(self, authors, words):
        """
        Set the SongImport object members.

        :param authors: String with authons
        :param words: Bytes with rtf-encoding
        """
        if authors:
            # Split up the authors
            author_list = authors.split('/')
            if len(author_list) < 2:
                author_list = authors.split(';')
            if len(author_list) < 2:
                author_list = authors.split(',')
            for author_name in author_list:
                self.add_author(author_name.strip())
        if words:
            # Format the lyrics
            result = None
            decoded_words = None
            try:
                decoded_words = words.decode()
            except UnicodeDecodeError:
                # The unicode chars in the rtf was not escaped in the expected manner
                self.entry_error_log = translate('SongsPlugin.EasyWorshipSongImport',
                                                 'Unexpected data formatting.')
                return
            result = strip_rtf(decoded_words, self.encoding)
            if result is None:
                self.entry_error_log = translate('SongsPlugin.EasyWorshipSongImport',
                                                 'No song text found.')
                return
            words, self.encoding = result
            verse_type = VerseType.tags[VerseType.Verse]
            for verse in SLIDE_BREAK_REGEX.split(words):
                verse = verse.strip()
                if not verse:
                    continue
                verse_split = verse.split('\n', 1)
                first_line_is_tag = False
                # EW tags: verse, chorus, pre-chorus, bridge, tag,
                # intro, ending, slide
                for tag in VerseType.tags + ['tag', 'slide']:
                    tag = tag.lower()
                    ew_tag = verse_split[0].strip().lower()
                    if ew_tag.startswith(tag):
                        verse_type = tag[0]
                        if tag == 'tag' or tag == 'slide':
                            verse_type = VerseType.tags[VerseType.Other]
                        first_line_is_tag = True
                        number_found = False
                        # check if tag is followed by number and/or note
                        if len(ew_tag) > len(tag):
                            match = NUMBER_REGEX.search(ew_tag)
                            if match:
                                number = match.group()
                                verse_type += number
                                number_found = True
                            match = NOTE_REGEX.search(ew_tag)
                            if match:
                                self.comments += ew_tag + '\n'
                        if not number_found:
                            verse_type += '1'
                        break
                self.add_verse(verse_split[-1].strip() if first_line_is_tag else verse, verse_type)
        if len(self.comments) > 5:
            self.comments += str(translate('SongsPlugin.EasyWorshipSongImport',
                                           '\n[above are Song Tags with notes imported from EasyWorship]'))

    def find_field(self, field_name):
        """
        Find a field in the descriptions

        :param field_name: field to find
        """
        return [i for i, x in enumerate(self.field_descriptions) if x.name == field_name][0]

    def set_record_struct(self, field_descriptions):
        """
        Save the record structure

        :param field_descriptions: An array of field descriptions
        """
        # Begin with empty field struct list
        fsl = ['>']
        for field_desc in field_descriptions:
            if field_desc.field_type == FieldType.String:
                fsl.append('%ds' % field_desc.size)
            elif field_desc.field_type == FieldType.Int16:
                fsl.append('H')
            elif field_desc.field_type == FieldType.Int32:
                fsl.append('I')
            elif field_desc.field_type == FieldType.Logical:
                fsl.append('B')
            elif field_desc.field_type == FieldType.Memo:
                fsl.append('%ds' % field_desc.size)
            elif field_desc.field_type == FieldType.Blob:
                fsl.append('%ds' % field_desc.size)
            elif field_desc.field_type == FieldType.Timestamp:
                fsl.append('Q')
            else:
                fsl.append('%ds' % field_desc.size)
        self.record_structure = struct.Struct(''.join(fsl))
        self.field_descriptions = field_descriptions

    def get_field(self, field_desc_index):
        """
        Extract the field

        :param field_desc_index: Field index value
        :return: The field value
        """
        field = self.fields[field_desc_index]
        field_desc = self.field_descriptions[field_desc_index]
        # Return None in case of 'blank' entries
        if isinstance(field, bytes):
            if not field.rstrip(b'\0'):
                return None
        elif field == 0:
            return None
        # Format the field depending on the field type
        if field_desc.field_type == FieldType.String:
            return field.rstrip(b'\0')
        elif field_desc.field_type == FieldType.Int16:
            return field ^ 0x8000
        elif field_desc.field_type == FieldType.Int32:
            return field ^ 0x80000000
        elif field_desc.field_type == FieldType.Logical:
            return field ^ 0x80 == 1
        elif field_desc.field_type == FieldType.Memo or field_desc.field_type == FieldType.Blob:
            block_start, blob_size = struct.unpack_from('<II', field, len(field) - 10)
            sub_block = block_start & 0xff
            block_start &= ~0xff
            self.memo_file.seek(block_start)
            memo_block_type, = struct.unpack('b', self.memo_file.read(1))
            if memo_block_type == 2:
                self.memo_file.seek(8, os.SEEK_CUR)
            elif memo_block_type == 3:
                if sub_block > 63:
                    return b''
                self.memo_file.seek(11 + (5 * sub_block), os.SEEK_CUR)
                sub_block_start, = struct.unpack('B', self.memo_file.read(1))
                self.memo_file.seek(block_start + (sub_block_start * 16))
            else:
                return b''
            return self.memo_file.read(blob_size)
        else:
            return 0

    def get_bytes(self, pos, length):
        """
        Get bytes from ews_file

        :param pos: Position to read from
        :param length: Bytes to read
        :return: Bytes read
        """
        self.ews_file.seek(pos)
        return self.ews_file.read(length)

    def get_string(self, pos, length):
        """
        Get string from ews_file

        :param pos: Position to read from
        :param length: Characters to read
        :return: String read
        """
        bytes = self.get_bytes(pos, length)
        mask = '<' + str(length) + 's'
        byte_str, = struct.unpack(mask, bytes)
        return byte_str.decode('unicode-escape').replace('\0', '').strip()

    def get_i16(self, pos):
        """
        Get short int from ews_file

        :param pos: Position to read from
        :return: Short integer read
        """

        bytes = self.get_bytes(pos, 2)
        mask = '<h'
        number, = struct.unpack(mask, bytes)
        return number

    def get_i32(self, pos):
        """
        Get long int from ews_file

        :param pos: Position to read from
        :return: Long integer read
        """
        bytes = self.get_bytes(pos, 4)
        mask = '<i'
        number, = struct.unpack(mask, bytes)
        return number
