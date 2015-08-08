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

# OOo API documentation:
# http://wiki.services.openoffice.org/wiki/Documentation/BASIC_Guide/Structure_of_Text_Documents
# http://wiki.services.openoffice.org/wiki/Documentation/DevGuide/Text/Iterating_over_Text
# http://www.oooforum.org/forum/viewtopic.phtml?t=14409
# http://wiki.services.openoffice.org/wiki/Python

import logging
import os
import re

from openlp.core.common import is_win
from .openoffice import OpenOfficeImport


log = logging.getLogger(__name__)

if is_win():
    from .openoffice import PAGE_BEFORE, PAGE_AFTER, PAGE_BOTH
    RuntimeException = Exception
else:
    try:
        from com.sun.star.style.BreakType import PAGE_BEFORE, PAGE_AFTER, \
            PAGE_BOTH
        from com.sun.star.uno import RuntimeException
    except ImportError:
        pass
try:
    from com.sun.star.awt.FontWeight import BOLD
except ImportError:
    BOLD = 150.0
try:
    from com.sun.star.awt.FontSlant import ITALIC
except ImportError:
    ITALIC = 2


class SongsOfFellowshipImport(OpenOfficeImport):
    """
    Import songs provided on disks with the Songs of Fellowship music books
    VOLS1_2.RTF, sof3words.rtf and sof4words.rtf

    Use OpenOffice.org Writer for processing the rtf file

    The three books are not only inconsistent with each other, they are
    inconsistent in themselves too with their formatting. Not only this, but
    the 1+2 book does not space out verses correctly. This script attempts
    to sort it out, but doesn't get it 100% right. But better than having to
    type them all out!

    It attempts to detect italiced verses, and treats these as choruses in
    the verse ordering. Again not perfect, but a start.
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the class. Requires a songmanager class which is passed
        to SongImport for writing song to disk
        """
        OpenOfficeImport.__init__(self, manager, **kwargs)
        self.song = False

    def process_ooo_document(self):
        """
        Handle the import process for SoF files.
        """
        self.process_sof_file()

    def process_sof_file(self):
        """
        Process the RTF file, a paragraph at a time
        """
        self.blank_lines = 0
        self.new_song()
        try:
            paragraphs = self.document.getText().createEnumeration()
            while paragraphs.hasMoreElements():
                if self.stop_import_flag:
                    return
                paragraph = paragraphs.nextElement()
                if paragraph.supportsService("com.sun.star.text.Paragraph"):
                    self.process_paragraph(paragraph)
        except RuntimeException as exc:
            log.exception('Error processing file: %s', exc)
        if not self.finish():
            self.log_error(self.file_path)

    def process_paragraph(self, paragraph):
        """
        Process a paragraph.
        In the first book, a paragraph is a single line. In the latter ones they may contain multiple lines.
        Each paragraph contains textportions. Each textportion has it's own styling, e.g. italics, bold etc.
        Also check for page breaks, which indicates a new song in books 1+2.
        In later books, there may not be line breaks, so check for 3 or more newlines

        :param paragraph: The paragraph text
        """
        text = ''
        text_portions = paragraph.createEnumeration()
        while text_portions.hasMoreElements():
            text_portion = text_portions.nextElement()
            if text_portion.BreakType in (PAGE_BEFORE, PAGE_BOTH):
                self.process_paragraph_text(text)
                self.new_song()
                text = ''
            text += self.process_text_portion(text_portion)
            if text_portion.BreakType in (PAGE_AFTER, PAGE_BOTH):
                self.process_paragraph_text(text)
                self.new_song()
                text = ''
        self.process_paragraph_text(text)

    def process_paragraph_text(self, text):
        """
        Split the paragraph text into multiple lines and process

        :param text: The text
        """
        for line in text.split('\n'):
            self.process_paragraph_line(line)
        if self.blank_lines > 2:
            self.new_song()

    def process_paragraph_line(self, text):
        """
        Process a single line. Throw away that text which isn't relevant, i.e.
        stuff that appears at the end of the song.
        Anything that is OK, append to the current verse

        :param text: The text
        """
        text = text.strip()
        if text == '':
            self.blank_lines += 1
            if self.blank_lines > 1:
                return
            if self.title != '':
                self.finish_verse()
            return
        self.blank_lines = 0
        if self.skip_to_close_bracket:
            if text.endswith(')'):
                self.skip_to_close_bracket = False
            return
        if text.startswith('CCL Licence'):
            self.italics = False
            return
        if text == 'A Songs of Fellowship Worship Resource':
            return
        if text.startswith('(NB.') or text.startswith('(Regrettably') or text.startswith('(From'):
            self.skip_to_close_bracket = True
            return
        if text.startswith('Copyright'):
            self.add_copyright(text)
            return
        if text == '(Repeat)':
            self.finish_verse()
            self.repeat_verse()
            return
        if self.title == '':
            if self.copyright == '':
                self.add_sof_author(text)
            else:
                self.add_copyright(text)
            return
        self.add_verse_line(text)

    def process_text_portion(self, text_portion):
        """
        Process a text portion. Here we just get the text and detect if it's bold or italics. If it's bold then its a
        song number or song title.
        Song titles are in all capitals, so we must bring the capitalization into line

        :param text_portion: A Piece of text
        """
        text = text_portion.getString()
        text = self.tidy_text(text)
        if text.strip() == '':
            return text
        if text_portion.CharWeight == BOLD:
            bold_text = text.strip()
            if bold_text.isdigit() and self.song_number == '':
                self.add_song_number(bold_text)
                return ''
            text = self.uncap_text(text)
            if self.title == '':
                self.add_title(text)
            return text
        if text.strip().startswith('('):
            return text
        self.italics = (text_portion.CharPosture == ITALIC)
        return text

    def new_song(self):
        """
        A change of song. Store the old, create a new
        ... but only if the last song was complete. If not, stick with it
        """
        if self.song:
            self.finish_verse()
            if not self.check_complete():
                return
            self.finish()
        self.song = True
        self.set_defaults()
        self.skip_to_close_bracket = False
        self.is_chorus = False
        self.italics = False
        self.current__verse = ''

    def add_song_number(self, song_no):
        """
        Add a song number, store as alternate title. Also use the song number to work out which songbook we're in

        :param song_no: The Song number
        """
        self.song_number = song_no
        self.alternate_title = song_no + '.'
        self.song_book_pub = 'Kingsway Publications'
        if int(song_no) <= 640:
            self.song_book = 'Songs of Fellowship 1'
        elif int(song_no) <= 1150:
            self.song_book = 'Songs of Fellowship 2'
        elif int(song_no) <= 1690:
            self.song_book = 'Songs of Fellowship 3'
        elif int(song_no) <= 2200:
            self.song_book = 'Songs of Fellowship 4'
        elif int(song_no) <= 2710:
            self.song_book = 'Songs of Fellowship 5'
        else:
            self.song_book = 'Songs of Fellowship Other'

    def add_title(self, text):
        """
        Add the title to the song. Strip some leading/trailing punctuation that we don't want in a title

        :param text: Title text
        """
        title = text.strip()
        if title.startswith('\''):
            title = title[1:]
        if title.endswith(','):
            title = title[:-1]
        self.title = title
        self.import_wizard.increment_progress_bar('Processing song ' + title, 0)

    def add_sof_author(self, text):
        """
        Add the author. OpenLP stores them individually so split by 'and', '&' and comma.
        However need to check for "Mr and Mrs Smith" and turn it to "Mr Smith" and "Mrs Smith".

        :param text: Author text
        """
        text = text.replace(' and ', ' & ')
        self.parse_author(text)

    def add_verse_line(self, text):
        """
        Add a line to the current verse. If the formatting has changed and we're beyond the second line of first verse,
        then this indicates a change of verse. Italics are a chorus

        :param text: The verse text
        """
        if self.italics != self.is_chorus and ((len(self.verses) > 0) or (self.current__verse.count('\n') > 1)):
            self.finish_verse()
        if self.italics:
            self.is_chorus = True
        self.current__verse += text + '\n'

    def finish_verse(self):
        """
        Verse is finished, store it. Note in book 1+2, some songs are formatted incorrectly. Here we try and split
        songs with missing line breaks into the correct number of verses.
        """
        if self.current__verse.strip() == '':
            return
        if self.is_chorus:
            versetag = 'C'
            splitat = None
        else:
            versetag = 'V'
            splitat = self.verse_splits(self.song_number)
        if splitat:
            ln = 0
            verse = ''
            for line in self.current__verse.split('\n'):
                ln += 1
                if line == '' or ln > splitat:
                    self.add_sof_verse(verse, versetag)
                    ln = 0
                    if line:
                        verse = line + '\n'
                    else:
                        verse = ''
                else:
                    verse += line + '\n'
            if verse:
                self.add_sof_verse(verse, versetag)
        else:
            self.add_sof_verse(self.current__verse, versetag)
        self.current__verse = ''
        self.is_chorus = False

    def add_sof_verse(self, lyrics, tag):
        self.add_verse(lyrics, tag)
        if not self.is_chorus and 'C1' in self.verse_order_list_generated:
            self.verse_order_list_generated.append('C1')
            self.verse_order_list_generated_useful = True

    def uncap_text(self, text):
        """
        Words in the title are in all capitals, so we lowercase them.
        However some of these words, e.g. referring to God need a leading
        capital letter.

        There is a complicated word "One", which is sometimes lower and
        sometimes upper depending on context. Never mind, keep it lower.
        """
        text_arr = re.split('(\W+)', text)
        text_arr[0] = text_arr[0].capitalize()
        for i in range(1, len(text_arr)):
            # Do not translate these. Fixed strings in SOF song file
            if text_arr[i] in ('JESUS', 'CHRIST', 'KING', 'ALMIGHTY', 'REDEEMER', 'SHEPHERD', 'SON', 'GOD', 'LORD',
                               'FATHER', 'HOLY', 'SPIRIT', 'LAMB', 'YOU', 'YOUR', 'I', 'I\'VE', 'I\'M', 'I\'LL',
                               'SAVIOUR', 'O', 'YOU\'RE', 'HE', 'HIS', 'HIM', 'ZION', 'EMMANUEL', 'MAJESTY', 'JESUS\'',
                               'JIREH', 'JUDAH', 'LION', 'LORD\'S', 'ABRAHAM', 'GOD\'S', 'FATHER\'S',
                               'ELIJAH' 'MARTHA', 'CHRISTMAS', 'ALPHA', 'OMEGA'):
                text_arr[i] = text_arr[i].capitalize()
            else:
                text_arr[i] = text_arr[i].lower()
        text = ''.join(text_arr)
        return text

    def verse_splits(self, song_number):
        """
        Because someone at Kingsway forgot to check the 1+2 RTF file, some verses were not formatted correctly.

        :param song_number: The Song number
        """
        if song_number == 11:
            return 8
        if song_number == 18:
            return 5
        if song_number == 21:
            return 6
        if song_number == 23:
            return 4
        if song_number == 24:
            return 7
        if song_number == 27:
            return 4
        if song_number == 31:
            return 6
        if song_number == 49:
            return 4
        if song_number == 50:
            return 8
        if song_number == 70:
            return 4
        if song_number == 75:
            return 8
        if song_number == 79:
            return 6
        if song_number == 97:
            return 7
        if song_number == 107:
            return 4
        if song_number == 109:
            return 4
        if song_number == 133:
            return 4
        if song_number == 155:
            return 10
        if song_number == 156:
            return 8
        if song_number == 171:
            return 4
        if song_number == 188:
            return 7
        if song_number == 192:
            return 4
        if song_number == 208:
            return 8
        if song_number == 215:
            return 8
        if song_number == 220:
            return 4
        if song_number == 247:
            return 6
        if song_number == 248:
            return 6
        if song_number == 251:
            return 8
        if song_number == 295:
            return 8
        if song_number == 307:
            return 5
        if song_number == 314:
            return 6
        if song_number == 325:
            return 8
        if song_number == 386:
            return 6
        if song_number == 415:
            return 4
        if song_number == 426:
            return 4
        if song_number == 434:
            return 5
        if song_number == 437:
            return 4
        if song_number == 438:
            return 6
        if song_number == 456:
            return 8
        if song_number == 461:
            return 4
        if song_number == 469:
            return 4
        if song_number == 470:
            return 5
        if song_number == 476:
            return 6
        if song_number == 477:
            return 7
        if song_number == 480:
            return 8
        if song_number == 482:
            return 4
        if song_number == 512:
            return 4
        if song_number == 513:
            return 8
        if song_number == 518:
            return 5
        if song_number == 520:
            return 4
        if song_number == 523:
            return 6
        if song_number == 526:
            return 8
        if song_number == 527:
            return 4
        if song_number == 529:
            return 4
        if song_number == 537:
            return 4
        if song_number == 555:
            return 6
        if song_number == 581:
            return 4
        if song_number == 589:
            return 6
        if song_number == 590:
            return 4
        if song_number == 593:
            return 8
        if song_number == 596:
            return 4
        if song_number == 610:
            return 6
        if song_number == 611:
            return 6
        if song_number == 619:
            return 8
        if song_number == 645:
            return 5
        if song_number == 653:
            return 6
        if song_number == 683:
            return 7
        if song_number == 686:
            return 4
        if song_number == 697:
            return 8
        if song_number == 698:
            return 4
        if song_number == 704:
            return 6
        if song_number == 716:
            return 4
        if song_number == 717:
            return 6
        if song_number == 730:
            return 4
        if song_number == 731:
            return 8
        if song_number == 732:
            return 8
        if song_number == 738:
            return 4
        if song_number == 756:
            return 9
        if song_number == 815:
            return 6
        if song_number == 830:
            return 8
        if song_number == 831:
            return 4
        if song_number == 876:
            return 6
        if song_number == 877:
            return 6
        if song_number == 892:
            return 4
        if song_number == 894:
            return 6
        if song_number == 902:
            return 8
        if song_number == 905:
            return 8
        if song_number == 921:
            return 6
        if song_number == 940:
            return 7
        if song_number == 955:
            return 9
        if song_number == 968:
            return 8
        if song_number == 972:
            return 7
        if song_number == 974:
            return 4
        if song_number == 988:
            return 6
        if song_number == 991:
            return 5
        if song_number == 1002:
            return 8
        if song_number == 1024:
            return 8
        if song_number == 1044:
            return 9
        if song_number == 1088:
            return 6
        if song_number == 1117:
            return 6
        if song_number == 1119:
            return 7
        return None
