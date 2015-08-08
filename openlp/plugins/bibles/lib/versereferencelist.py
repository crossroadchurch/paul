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

from openlp.plugins.bibles.lib import get_reference_separator


class VerseReferenceList(object):
    """
    The VerseReferenceList class encapsulates a list of verse references, but maintains the order in which they were
    added.
    """

    def __init__(self):
        self.verse_list = []
        self.version_list = []
        self.current_index = -1

    def add(self, book, chapter, verse, version, copyright, permission):
        self.add_version(version, copyright, permission)
        if not self.verse_list or self.verse_list[self.current_index]['book'] != book:
            self.verse_list.append({'version': version, 'book': book, 'chapter': chapter, 'start': verse, 'end': verse})
            self.current_index += 1
        elif self.verse_list[self.current_index]['chapter'] != chapter:
            self.verse_list.append({'version': version, 'book': book, 'chapter': chapter, 'start': verse, 'end': verse})
            self.current_index += 1
        elif (self.verse_list[self.current_index]['end'] + 1) == verse:
            self.verse_list[self.current_index]['end'] = verse
        else:
            self.verse_list.append({'version': version, 'book': book, 'chapter': chapter, 'start': verse, 'end': verse})
            self.current_index += 1

    def add_version(self, version, copyright, permission):
        for bible_version in self.version_list:
            if bible_version['version'] == version:
                return
        self.version_list.append({'version': version, 'copyright': copyright, 'permission': permission})

    def format_verses(self):
        verse_sep = get_reference_separator('sep_v_display')
        range_sep = get_reference_separator('sep_r_display')
        list_sep = get_reference_separator('sep_l_display')
        result = ''
        for index, verse in enumerate(self.verse_list):
            if index == 0:
                result = '%s %s%s%s' % (verse['book'], verse['chapter'], verse_sep, verse['start'])
                if verse['start'] != verse['end']:
                    result = '%s%s%s' % (result, range_sep, verse['end'])
                continue
            prev = index - 1
            if self.verse_list[prev]['version'] != verse['version']:
                result = '%s (%s)' % (result, self.verse_list[prev]['version'])
            result += '%s ' % list_sep
            if self.verse_list[prev]['book'] != verse['book']:
                result = '%s%s %s%s' % (result, verse['book'], verse['chapter'], verse_sep)
            elif self.verse_list[prev]['chapter'] != verse['chapter']:
                result = '%s%s%s' % (result, verse['chapter'], verse_sep)
            result += str(verse['start'])
            if verse['start'] != verse['end']:
                result = '%s%s%s' % (result, range_sep, verse['end'])
        if len(self.version_list) > 1:
            result = '%s (%s)' % (result, verse['version'])
        return result

    def format_versions(self, copyright=True, permission=True):
        """
        Format a string with the bible versions used

        :param copyright: If the copyright info should be included, default is true.
        :param permission: If the permission info should be included, default is true.
        :return: A formatted string with the bible versions used
        """
        result = ''
        for index, version in enumerate(self.version_list):
            if index > 0:
                if result[-1] not in [';', ',', '.']:
                    result += ';'
                result += ' '
            result += version['version']
            if copyright and version['copyright'].strip():
                result += ', ' + version['copyright']
            if permission and version['permission'].strip():
                result += ', ' + version['permission']
        result = result.rstrip()
        if result.endswith(','):
            return result[:len(result) - 1]
        return result
