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
The :mod:`cvsbible` modules provides a facility to import bibles from a set of CSV files.

The module expects two mandatory files containing the books and the verses.

The format of the books file is:

    <book_id>,<testament_id>,<book_name>,<book_abbreviation>

    For example

        1,1,Genesis,Gen
        2,1,Exodus,Exod
        ...
        40,2,Matthew,Matt

There are two acceptable formats of the verses file.  They are:

    <book_id>,<chapter_number>,<verse_number>,<verse_text>
    or
    <book_name>,<chapter_number>,<verse_number>,<verse_text>

    For example:

        1,1,1,"In the beginning God created the heaven and the earth."
        or
        "Genesis",1,2,"And the earth was without form, and void; and...."

All CSV files are expected to use a comma (',') as the delimiter and double quotes ('"') as the quote symbol.
"""
import logging
import chardet
import csv

from openlp.core.common import translate
from openlp.plugins.bibles.lib.db import BibleDB, BiblesResourcesDB


log = logging.getLogger(__name__)


class CSVBible(BibleDB):
    """
    This class provides a specialisation for importing of CSV Bibles.
    """
    log.info('CSVBible loaded')

    def __init__(self, parent, **kwargs):
        """
        Loads a Bible from a set of CSV files. This class assumes the files contain all the information and a clean
        bible is being loaded.
        """
        log.info(self.__class__.__name__)
        BibleDB.__init__(self, parent, **kwargs)
        self.books_file = kwargs['booksfile']
        self.verses_file = kwargs['versefile']

    def do_import(self, bible_name=None):
        """
        Import the bible books and verses.
        """
        self.wizard.progress_bar.setValue(0)
        self.wizard.progress_bar.setMinimum(0)
        self.wizard.progress_bar.setMaximum(66)
        success = True
        language_id = self.get_language(bible_name)
        if not language_id:
            log.error('Importing books from "%s" failed' % self.filename)
            return False
        books_file = None
        book_list = {}
        # Populate the Tables
        try:
            details = get_file_encoding(self.books_file)
            books_file = open(self.books_file, 'r', encoding=details['encoding'])
            books_reader = csv.reader(books_file, delimiter=',', quotechar='"')
            for line in books_reader:
                if self.stop_import_flag:
                    break
                self.wizard.increment_progress_bar(translate('BiblesPlugin.CSVBible', 'Importing books... %s')
                                                   % line[2])
                book_ref_id = self.get_book_ref_id_by_name(line[2], 67, language_id)
                if not book_ref_id:
                    log.error('Importing books from "%s" failed' % self.books_file)
                    return False
                book_details = BiblesResourcesDB.get_book_by_id(book_ref_id)
                self.create_book(line[2], book_ref_id, book_details['testament_id'])
                book_list.update({int(line[0]): line[2]})
            self.application.process_events()
        except (IOError, IndexError):
            log.exception('Loading books from file failed')
            success = False
        finally:
            if books_file:
                books_file.close()
        if self.stop_import_flag or not success:
            return False
        self.wizard.progress_bar.setValue(0)
        self.wizard.progress_bar.setMaximum(67)
        verse_file = None
        try:
            book_ptr = None
            details = get_file_encoding(self.verses_file)
            verse_file = open(self.verses_file, 'r', encoding=details['encoding'])
            verse_reader = csv.reader(verse_file, delimiter=',', quotechar='"')
            for line in verse_reader:
                if self.stop_import_flag:
                    break
                try:
                    line_book = book_list[int(line[0])]
                except ValueError:
                    line_book = line[0]
                if book_ptr != line_book:
                    book = self.get_book(line_book)
                    book_ptr = book.name
                    self.wizard.increment_progress_bar(
                        translate('BiblesPlugin.CSVBible',
                                  'Importing verses from %s...' % book.name, 'Importing verses from <book name>...'))
                    self.session.commit()
                verse_text = line[3]
                self.create_verse(book.id, line[1], line[2], verse_text)
            self.wizard.increment_progress_bar(translate('BiblesPlugin.CSVBible', 'Importing verses... done.'))
            self.application.process_events()
            self.session.commit()
        except IOError:
            log.exception('Loading verses from file failed')
            success = False
        finally:
            if verse_file:
                verse_file.close()
        if self.stop_import_flag:
            return False
        else:
            return success


def get_file_encoding(filename):
    """
    Utility function to get the file encoding.
    """
    detect_file = None
    try:
        detect_file = open(filename, 'rb')
        details = chardet.detect(detect_file.read(1024))
    except IOError:
        log.exception('Error detecting file encoding')
    finally:
        if detect_file:
            detect_file.close()
    return details
