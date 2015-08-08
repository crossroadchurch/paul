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
from lxml import etree, objectify

from openlp.core.common import translate, trace_error_handler
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.bibles.lib.db import BibleDB, BiblesResourcesDB


log = logging.getLogger(__name__)


class OpenSongBible(BibleDB):
    """
    OpenSong Bible format importer class.
    """
    def __init__(self, parent, **kwargs):
        """
        Constructor to create and set up an instance of the OpenSongBible class. This class is used to import Bibles
        from OpenSong's XML format.
        """
        log.debug(self.__class__.__name__)
        BibleDB.__init__(self, parent, **kwargs)
        self.filename = kwargs['filename']

    def get_text(self, element):
        """
        Recursively get all text in an objectify element and its child elements.

        :param element: An objectify element to get the text from
        """
        verse_text = ''
        if element.text:
            verse_text = element.text
        for sub_element in element.iterchildren():
            verse_text += self.get_text(sub_element)
        if element.tail:
            verse_text += element.tail
        return verse_text

    def do_import(self, bible_name=None):
        """
        Loads a Bible from file.
        """
        log.debug('Starting OpenSong import from "%s"' % self.filename)
        if not isinstance(self.filename, str):
            self.filename = str(self.filename, 'utf8')
        import_file = None
        success = True
        try:
            # NOTE: We don't need to do any of the normal encoding detection here, because lxml does it's own encoding
            # detection, and the two mechanisms together interfere with each other.
            import_file = open(self.filename, 'rb')
            opensong = objectify.parse(import_file)
            bible = opensong.getroot()
            # Check that we're not trying to import a Zefania XML bible, it is sometimes refered to as 'OpenSong'
            if bible.tag.upper() == 'XMLBIBLE':
                critical_error_message_box(
                    message=translate('BiblesPlugin.OpenSongImport',
                                      'Incorrect Bible file type supplied. This looks like a Zefania XML bible, '
                                      'please use the Zefania import option.'))
                return False
            # No language info in the opensong format, so ask the user
            language_id = self.get_language(bible_name)
            if not language_id:
                log.error('Importing books from "%s" failed' % self.filename)
                return False
            for book in bible.b:
                if self.stop_import_flag:
                    break
                book_ref_id = self.get_book_ref_id_by_name(str(book.attrib['n']), len(bible.b), language_id)
                if not book_ref_id:
                    log.error('Importing books from "%s" failed' % self.filename)
                    return False
                book_details = BiblesResourcesDB.get_book_by_id(book_ref_id)
                db_book = self.create_book(book.attrib['n'], book_ref_id, book_details['testament_id'])
                chapter_number = 0
                for chapter in book.c:
                    if self.stop_import_flag:
                        break
                    number = chapter.attrib['n']
                    if number:
                        chapter_number = int(number.split()[-1])
                    else:
                        chapter_number += 1
                    verse_number = 0
                    for verse in chapter.v:
                        if self.stop_import_flag:
                            break
                        number = verse.attrib['n']
                        if number:
                            try:
                                number = int(number)
                            except ValueError:
                                verse_parts = number.split('-')
                                if len(verse_parts) > 1:
                                    number = int(verse_parts[0])
                            except TypeError:
                                log.warning('Illegal verse number: %s', str(verse.attrib['n']))
                            verse_number = number
                        else:
                            verse_number += 1
                        self.create_verse(db_book.id, chapter_number, verse_number, self.get_text(verse))
                    self.wizard.increment_progress_bar(
                        translate('BiblesPlugin.Opensong', 'Importing %(bookname)s %(chapter)s...') %
                        {'bookname': db_book.name, 'chapter': chapter_number})
                self.session.commit()
            self.application.process_events()
        except etree.XMLSyntaxError as inst:
            trace_error_handler(log)
            critical_error_message_box(
                message=translate('BiblesPlugin.OpenSongImport',
                                  'Incorrect Bible file type supplied. OpenSong Bibles may be '
                                  'compressed. You must decompress them before import.'))
            log.exception(inst)
            success = False
        except (IOError, AttributeError):
            log.exception('Loading Bible from OpenSong file failed')
            success = False
        finally:
            if import_file:
                import_file.close()
        if self.stop_import_flag:
            return False
        else:
            return success
