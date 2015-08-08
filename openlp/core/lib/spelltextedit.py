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
The :mod:`~openlp.core.lib.spelltextedit` module contains a classes to add spell checking to an edit widget.
"""

import logging
import re

try:
    import enchant
    from enchant import DictNotFoundError
    from enchant.errors import Error
    ENCHANT_AVAILABLE = True
except ImportError:
    ENCHANT_AVAILABLE = False

# based on code from http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check

from PyQt4 import QtCore, QtGui

from openlp.core.lib import translate, FormattingTags
from openlp.core.lib.ui import create_action

log = logging.getLogger(__name__)


class SpellTextEdit(QtGui.QPlainTextEdit):
    """
    Spell checking widget based on QPlanTextEdit.
    """
    def __init__(self, parent=None, formatting_tags_allowed=True):
        """
        Constructor.
        """
        global ENCHANT_AVAILABLE
        super(SpellTextEdit, self).__init__(parent)
        self.formatting_tags_allowed = formatting_tags_allowed
        # Default dictionary based on the current locale.
        if ENCHANT_AVAILABLE:
            try:
                self.dictionary = enchant.Dict()
                self.highlighter = Highlighter(self.document())
                self.highlighter.spelling_dictionary = self.dictionary
            except (Error, DictNotFoundError):
                ENCHANT_AVAILABLE = False
                log.debug('Could not load default dictionary')

    def mousePressEvent(self, event):
        """
        Handle mouse clicks within the text edit region.
        """
        if event.button() == QtCore.Qt.RightButton:
            # Rewrite the mouse event to a left button event so the cursor is moved to the location of the pointer.
            event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress,
                                      event.pos(), QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier)
        QtGui.QPlainTextEdit.mousePressEvent(self, event)

    def contextMenuEvent(self, event):
        """
        Provide the context menu for the text edit region.
        """
        popup_menu = self.createStandardContextMenu()
        # Select the word under the cursor.
        cursor = self.textCursor()
        # only select text if not already selected
        if not cursor.hasSelection():
            cursor.select(QtGui.QTextCursor.WordUnderCursor)
        self.setTextCursor(cursor)
        # Add menu with available languages.
        if ENCHANT_AVAILABLE:
            lang_menu = QtGui.QMenu(translate('OpenLP.SpellTextEdit', 'Language:'))
            for lang in enchant.list_languages():
                action = create_action(lang_menu, lang, text=lang, checked=lang == self.dictionary.tag)
                lang_menu.addAction(action)
            popup_menu.insertSeparator(popup_menu.actions()[0])
            popup_menu.insertMenu(popup_menu.actions()[0], lang_menu)
            lang_menu.triggered.connect(self.set_language)
        # Check if the selected word is misspelled and offer spelling suggestions if it is.
        if ENCHANT_AVAILABLE and self.textCursor().hasSelection():
            text = self.textCursor().selectedText()
            if not self.dictionary.check(text):
                spell_menu = QtGui.QMenu(translate('OpenLP.SpellTextEdit', 'Spelling Suggestions'))
                for word in self.dictionary.suggest(text):
                    action = SpellAction(word, spell_menu)
                    action.correct.connect(self.correct_word)
                    spell_menu.addAction(action)
                # Only add the spelling suggests to the menu if there are suggestions.
                if spell_menu.actions():
                    popup_menu.insertMenu(popup_menu.actions()[0], spell_menu)
        tag_menu = QtGui.QMenu(translate('OpenLP.SpellTextEdit', 'Formatting Tags'))
        if self.formatting_tags_allowed:
            for html in FormattingTags.get_html_tags():
                action = SpellAction(html['desc'], tag_menu)
                action.correct.connect(self.html_tag)
                tag_menu.addAction(action)
            popup_menu.insertSeparator(popup_menu.actions()[0])
            popup_menu.insertMenu(popup_menu.actions()[0], tag_menu)
        popup_menu.exec_(event.globalPos())

    def set_language(self, action):
        """
        Changes the language for this spelltextedit.

        :param action: The action.
        """
        self.dictionary = enchant.Dict(action.text())
        self.highlighter.spelling_dictionary = self.dictionary
        self.highlighter.highlightBlock(self.toPlainText())
        self.highlighter.rehighlight()

    def correct_word(self, word):
        """
        Replaces the selected text with word.
        """
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(word)
        cursor.endEditBlock()

    def html_tag(self, tag):
        """
        Replaces the selected text with word.
        """
        for html in FormattingTags.get_html_tags():
            if tag == html['desc']:
                cursor = self.textCursor()
                if self.textCursor().hasSelection():
                    text = cursor.selectedText()
                    cursor.beginEditBlock()
                    cursor.removeSelectedText()
                    cursor.insertText(html['start tag'])
                    cursor.insertText(text)
                    cursor.insertText(html['end tag'])
                    cursor.endEditBlock()
                else:
                    cursor = self.textCursor()
                    cursor.insertText(html['start tag'])
                    cursor.insertText(html['end tag'])


class Highlighter(QtGui.QSyntaxHighlighter):
    """
    Provides a text highlighter for pointing out spelling errors in text.
    """
    WORDS = '(?iu)[\w\']+'

    def __init__(self, *args):
        """
        Constructor
        """
        super(Highlighter, self).__init__(*args)
        self.spelling_dictionary = None

    def highlightBlock(self, text):
        """
        Highlight mis spelt words in a block of text.

        Note, this is a Qt hook.
        """
        if not self.spelling_dictionary:
            return
        text = str(text)
        char_format = QtGui.QTextCharFormat()
        char_format.setUnderlineColor(QtCore.Qt.red)
        char_format.setUnderlineStyle(QtGui.QTextCharFormat.SpellCheckUnderline)
        for word_object in re.finditer(self.WORDS, text):
            if not self.spelling_dictionary.check(word_object.group()):
                self.setFormat(word_object.start(), word_object.end() - word_object.start(), char_format)


class SpellAction(QtGui.QAction):
    """
    A special QAction that returns the text in a signal.
    """
    correct = QtCore.pyqtSignal(str)

    def __init__(self, *args):
        """
        Constructor
        """
        super(SpellAction, self).__init__(*args)
        self.triggered.connect(lambda x: self.correct.emit(self.text()))
