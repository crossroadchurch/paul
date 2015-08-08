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
The :mod:`formattingtagform` provides an Tag Edit facility. The Base set are protected and included each time loaded.
Custom tags can be defined and saved. The Custom Tag arrays are saved in a pickle so QSettings works on them. Base Tags
cannot be changed.
"""

import re
from openlp.core.common import translate
from openlp.core.lib import FormattingTags


class FormattingTagController(object):
    """
    The :class:`FormattingTagController` manages the non UI functions .
    """
    def __init__(self):
        """
        Initiator
        """
        self.html_tag_regex = re.compile(
            r'<(?:(?P<close>/(?=[^\s/>]+>))?'
            r'(?P<tag>[^\s/!\?>]+)(?:\s+[^\s=]+="[^"]*")*\s*(?P<empty>/)?'
            r'|(?P<cdata>!\[CDATA\[(?:(?!\]\]>).)*\]\])'
            r'|(?P<procinst>\?(?:(?!\?>).)*\?)'
            r'|(?P<comment>!--(?:(?!-->).)*--))>', re.UNICODE)
        self.html_regex = re.compile(r'^(?:[^<>]*%s)*[^<>]*$' % self.html_tag_regex.pattern)

    def pre_save(self):
        """
        Cleanup the array before save validation runs
        """
        self.protected_tags = [tag for tag in FormattingTags.html_expands if tag.get('protected')]
        self.custom_tags = []

    def validate_for_save(self, desc, tag, start_html, end_html):
        """
        Validate a custom tag and add to the tags array if valid..

        `desc`
            Explanation of the tag.

        `tag`
            The tag in the song used to mark the text.

        `start_html`
            The start html tag.

        `end_html`
            The end html tag.

        """
        for line_number, html1 in enumerate(self.protected_tags):
            if self._strip(html1['start tag']) == tag:
                return translate('OpenLP.FormattingTagForm', 'Tag %s already defined.') % tag
            if self._strip(html1['desc']) == desc:
                return translate('OpenLP.FormattingTagForm', 'Description %s already defined.') % tag
        for line_number, html1 in enumerate(self.custom_tags):
            if self._strip(html1['start tag']) == tag:
                return translate('OpenLP.FormattingTagForm', 'Tag %s already defined.') % tag
            if self._strip(html1['desc']) == desc:
                return translate('OpenLP.FormattingTagForm', 'Description %s already defined.') % tag
        tag = {
            'desc': desc,
            'start tag': '{%s}' % tag,
            'start html': start_html,
            'end tag': '{/%s}' % tag,
            'end html': end_html,
            'protected': False,
            'temporary': False
        }
        self.custom_tags.append(tag)

    def save_tags(self):
        """
        Save the new tags if they are valid.
        """
        FormattingTags.save_html_tags(self.custom_tags)
        FormattingTags.load_tags()

    def _strip(self, tag):
        """
        Remove tag wrappers for editing.

        `tag`
            Tag to be stripped
        """
        tag = tag.replace('{', '')
        tag = tag.replace('}', '')
        return tag

    def start_html_to_end_html(self, start_html):
        """
        Return the end HTML for a given start HTML or None if invalid.

        `start_html`
            The start html tag.

        """
        end_tags = []
        match = self.html_regex.match(start_html)
        if match:
            match = self.html_tag_regex.search(start_html)
            while match:
                if match.group('tag'):
                    tag = match.group('tag').lower()
                    if match.group('close'):
                        if match.group('empty') or not end_tags or end_tags.pop() != tag:
                            return
                    elif not match.group('empty'):
                        end_tags.append(tag)
                match = self.html_tag_regex.search(start_html, match.end())
            return ''.join(map(lambda tag: '</%s>' % tag, reversed(end_tags)))

    def start_tag_changed(self, start_html, end_html):
        """
        Validate the HTML tags when the start tag has been changed.

        `start_html`
            The start html tag.

        `end_html`
            The end html tag.

        """
        end = self.start_html_to_end_html(start_html)
        if not end_html:
            if not end:
                return translate('OpenLP.FormattingTagForm', 'Start tag %s is not valid HTML') % start_html, None
            return None, end
        return None, None

    def end_tag_changed(self, start_html, end_html):
        """
        Validate the HTML tags when the end tag has been changed.

        `start_html`
            The start html tag.

        `end_html`
            The end html tag.

        """
        end = self.start_html_to_end_html(start_html)
        if not end_html:
            return None, end
        if end and end != end_html:
            return translate('OpenLP.FormattingTagForm',
                             'End tag %s does not match end tag for start tag %s') % (end, start_html), None
        return None, None
