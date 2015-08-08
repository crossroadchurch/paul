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

import logging
import re

from lxml import objectify
from lxml.etree import Error, LxmlError

from openlp.core.common import translate
from openlp.plugins.songs.lib import VerseType
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.plugins.songs.lib.ui import SongStrings

log = logging.getLogger(__name__)


class OpenSongImport(SongImport):
    """
    Import songs exported from OpenSong

    The format is described loosely on the `OpenSong File Format Specification
    <http://www.opensong.org/d/manual/song_file_format_specification>`_ page on the OpenSong web site. However, it
    doesn't describe the <lyrics> section, so here's an attempt:

    If the first character of a line is a space, then the rest of that line is lyrics. If it is not a space the
    following applies.

    Verses can be expressed in one of 2 ways, either in complete verses, or by line grouping, i.e. grouping all line 1's
    of a verse together, all line 2's of a verse together, and so on.

    An example of complete verses::

        <lyrics>
        [v1]
         List of words
         Another Line

        [v2]
         Some words for the 2nd verse
         etc...
        </lyrics>

    The 'v' in the verse specifiers above can be left out, it is implied.

    An example of line grouping::

        <lyrics>
        [V]
        1List of words
        2Some words for the 2nd Verse

        1Another Line
        2etc...
        </lyrics>

    Either or both forms can be used in one song. The number does not necessarily appear at the start of the line.
    Additionally, the [v1] labels can have either upper or lower case Vs.

    Other labels can be used also:

    C
        Chorus

    B
        Bridge

    All verses are imported and tagged appropriately.

    Guitar chords can be provided "above" the lyrics (the line is preceded by a period "."), and one or more "_" can
    be used to signify long-drawn-out words. Chords and "_" are removed by this importer. For example::

        . A7        Bm
        1 Some____ Words

    Lines that contain only whitespace are ignored.
    | indicates a blank line, and || a new slide.

        Slide 1 Line 1|Slide 1 Line 2||Slide 2 Line 1|Slide 2 Line 2

    Lines beginning with ; are comments

    The <presentation> tag is used to populate the OpenLP verse display order field. The Author and Copyright tags are
    also imported to the appropriate places.
    """

    def __init__(self, manager, **kwargs):
        """
        Initialise the class.
        """
        super(OpenSongImport, self).__init__(manager, **kwargs)

    def do_import(self):
        """
        Receive a single file or a list of files to import.
        """
        if not isinstance(self.import_source, list):
            return
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for filename in self.import_source:
            if self.stop_import_flag:
                return
            song_file = open(filename, 'rb')
            self.do_import_file(song_file)
            song_file.close()

    def do_import_file(self, file):
        """
        Process the OpenSong file - pass in a file-like object, not a file path.
        """
        self.set_defaults()
        try:
            tree = objectify.parse(file)
        except (Error, LxmlError):
            self.log_error(file.name, SongStrings.XMLSyntaxError)
            log.exception('Error parsing XML')
            return
        root = tree.getroot()
        if root.tag != 'song':
            self.log_error(file.name, str(
                translate('SongsPlugin.OpenSongImport', 'Invalid OpenSong song file. Missing song tag.')))
            return
        fields = dir(root)
        decode = {
            'copyright': self.add_copyright,
            'ccli': 'ccli_number',
            'author': self.parse_author,
            'title': 'title',
            'aka': 'alternate_title',
            'hymn_number': self.parse_song_book_name_and_number,
            'user1': self.add_comment,
            'user2': self.add_comment,
            'user3': self.add_comment
        }
        for attr, fn_or_string in list(decode.items()):
            if attr in fields:
                ustring = str(root.__getattr__(attr))
                if isinstance(fn_or_string, str):
                    if attr in ['ccli']:
                        if ustring:
                            setattr(self, fn_or_string, int(ustring))
                        else:
                            setattr(self, fn_or_string, None)
                    else:
                        setattr(self, fn_or_string, ustring)
                else:
                    fn_or_string(ustring)
        # Themes look like "God: Awe/Wonder", but we just want
        # "Awe" and "Wonder".  We use a set to ensure each topic
        # is only added once, in case it is already there, which
        # is actually quite likely if the alttheme is set
        topics = set(self.topics)
        if 'theme' in fields:
            theme = str(root.theme)
            subthemes = theme[theme.find(':')+1:].split('/')
            for topic in subthemes:
                topics.add(topic.strip())
        if 'alttheme' in fields:
            theme = str(root.alttheme)
            subthemes = theme[theme.find(':')+1:].split('/')
            for topic in subthemes:
                topics.add(topic.strip())
        self.topics = list(topics)
        self.topics.sort()
        # data storage while importing
        verses = {}
        # keep track of verses appearance order
        our_verse_order = []
        # default verse
        verse_tag = VerseType.tags[VerseType.Verse]
        verse_num = '1'
        # for the case where song has several sections with same marker
        inst = 1
        if 'lyrics' in fields:
            lyrics = str(root.lyrics)
        else:
            lyrics = ''
        for this_line in lyrics.split('\n'):
            if not this_line.strip():
                continue
            # skip this line if it is a comment
            if this_line.startswith(';'):
                continue
            # skip guitar chords and page and column breaks
            if this_line.startswith('.') or this_line.startswith('---') or this_line.startswith('-!!'):
                continue
            # verse/chorus/etc. marker
            if this_line.startswith('['):
                # drop the square brackets
                right_bracket = this_line.find(']')
                content = this_line[1:right_bracket].lower()
                # have we got any digits? If so, verse number is everything from the digits to the end (openlp does not
                # have concept of part verses, so just ignore any non integers on the end (including floats))
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
                inst = 1
                if [verse_tag, verse_num, inst] in our_verse_order and verse_num in verses.get(verse_tag, {}):
                    inst = len(verses[verse_tag][verse_num]) + 1
                continue
            # number at start of line.. it's verse number
            if this_line[0].isdigit():
                verse_num = this_line[0]
                this_line = this_line[1:].strip()
            verses.setdefault(verse_tag, {})
            verses[verse_tag].setdefault(verse_num, {})
            if inst not in verses[verse_tag][verse_num]:
                verses[verse_tag][verse_num][inst] = []
                our_verse_order.append([verse_tag, verse_num, inst])
            # Tidy text and remove the ____s from extended words
            this_line = self.tidy_text(this_line)
            this_line = this_line.replace('_', '')
            this_line = this_line.replace('||', '\n[---]\n')
            this_line = this_line.strip()
            # If the line consists solely of a '|', then just use the implicit newline
            # Otherwise, add a newline for each '|'
            if this_line == '|':
                this_line = ''
            else:
                this_line = this_line.replace('|', '\n')
            verses[verse_tag][verse_num][inst].append(this_line)
        # done parsing
        # add verses in original order
        verse_joints = {}
        for (verse_tag, verse_num, inst) in our_verse_order:
            lines = '\n'.join(verses[verse_tag][verse_num][inst])
            length = 0
            while length < len(verse_num) and verse_num[length].isnumeric():
                length += 1
            verse_def = '%s%s' % (verse_tag, verse_num[:length])
            verse_joints[verse_def] = '%s\n[---]\n%s' % (verse_joints[verse_def], lines) \
                if verse_def in verse_joints else lines
        # Parsing the dictionary produces the elements in a non-intuitive order.  While it "works", it's not a
        # natural layout should the user come back to edit the song.  Instead we sort by the verse type, so that we
        # get all the verses in order (v1, v2, ...), then the chorus(es), bridge(s), pre-chorus(es) etc.  We use a
        # tuple for the key, since tuples naturally sort in this manner.
        verse_defs = sorted(verse_joints.keys(),
                            key=lambda verse_def: (VerseType.from_tag(verse_def[0]), int(verse_def[1:])))
        for verse_def in verse_defs:
            lines = verse_joints[verse_def]
            self.add_verse(lines, verse_def)
        if not self.verses:
            self.add_verse('')
        # figure out the presentation order, if present
        if 'presentation' in fields and root.presentation:
            order = str(root.presentation)
            # We make all the tags in the lyrics lower case, so match that here and then split into a list on the
            # whitespace.
            order = order.lower().split()
            for verse_def in order:
                match = re.match('(\D*)(\d+.*)', verse_def)
                if match is not None:
                    verse_tag = match.group(1)
                    verse_num = match.group(2)
                    if not verse_tag:
                        verse_tag = VerseType.tags[VerseType.Verse]
                else:
                    # Assume it's no.1 if there are no digits
                    verse_tag = verse_def
                    verse_num = '1'
                verse_index = VerseType.from_loose_input(verse_tag)
                verse_tag = VerseType.tags[verse_index]
                verse_def = '%s%s' % (verse_tag, verse_num)
                if verse_num in verses.get(verse_tag, {}):
                    self.verse_order_list.append(verse_def)
                else:
                    log.info('Got order %s but not in verse tags, dropping this item from presentation order',
                             verse_def)
        if not self.finish():
            self.log_error(file.name)
