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

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, Settings, UiStrings, translate
from openlp.core.lib import SettingsTab
from openlp.core.lib.ui import find_and_set_in_combo_box
from openlp.plugins.bibles.lib import LayoutStyle, DisplayStyle, update_reference_separators, \
    get_reference_separator, LanguageSelection

log = logging.getLogger(__name__)


class BiblesTab(SettingsTab):
    """
    BiblesTab is the Bibles settings tab in the settings dialog.
    """
    log.info('Bible Tab loaded')

    def _init_(self, parent, title, visible_title, icon_path):
        self.paragraph_style = True
        self.show_new_chapters = False
        self.display_style = 0
        super(BiblesTab, self).__init__(parent, title, visible_title, icon_path)

    def setupUi(self):
        self.setObjectName('BiblesTab')
        super(BiblesTab, self).setupUi()
        self.verse_display_group_box = QtGui.QGroupBox(self.left_column)
        self.verse_display_group_box.setObjectName('verse_display_group_box')
        self.verse_display_layout = QtGui.QFormLayout(self.verse_display_group_box)
        self.verse_display_layout.setObjectName('verse_display_layout')
        self.is_verse_number_visible_check_box = QtGui.QCheckBox(self.verse_display_group_box)
        self.is_verse_number_visible_check_box.setObjectName('is_verse_number_visible_check_box')
        self.verse_display_layout.addRow(self.is_verse_number_visible_check_box)
        self.new_chapters_check_box = QtGui.QCheckBox(self.verse_display_group_box)
        self.new_chapters_check_box.setObjectName('new_chapters_check_box')
        self.verse_display_layout.addRow(self.new_chapters_check_box)
        self.display_style_label = QtGui.QLabel(self.verse_display_group_box)
        self.display_style_label.setObjectName('display_style_label')
        self.display_style_combo_box = QtGui.QComboBox(self.verse_display_group_box)
        self.display_style_combo_box.addItems(['', '', '', ''])
        self.display_style_combo_box.setObjectName('display_style_combo_box')
        self.verse_display_layout.addRow(self.display_style_label, self.display_style_combo_box)
        self.layout_style_label = QtGui.QLabel(self.verse_display_group_box)
        self.layout_style_label.setObjectName('layout_style_label')
        self.layout_style_combo_box = QtGui.QComboBox(self.verse_display_group_box)
        self.layout_style_combo_box.setObjectName('layout_style_combo_box')
        self.layout_style_combo_box.addItems(['', '', ''])
        self.verse_display_layout.addRow(self.layout_style_label, self.layout_style_combo_box)
        self.bible_second_check_box = QtGui.QCheckBox(self.verse_display_group_box)
        self.bible_second_check_box.setObjectName('bible_second_check_box')
        self.verse_display_layout.addRow(self.bible_second_check_box)
        self.bible_theme_label = QtGui.QLabel(self.verse_display_group_box)
        self.bible_theme_label.setObjectName('BibleTheme_label')
        self.bible_theme_combo_box = QtGui.QComboBox(self.verse_display_group_box)
        self.bible_theme_combo_box.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.bible_theme_combo_box.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.bible_theme_combo_box.addItem('')
        self.bible_theme_combo_box.setObjectName('BibleThemecombo_box')
        self.verse_display_layout.addRow(self.bible_theme_label, self.bible_theme_combo_box)
        self.change_note_label = QtGui.QLabel(self.verse_display_group_box)
        self.change_note_label.setWordWrap(True)
        self.change_note_label.setObjectName('change_note_label')
        self.verse_display_layout.addRow(self.change_note_label)
        self.left_layout.addWidget(self.verse_display_group_box)
        self.scripture_reference_group_box = QtGui.QGroupBox(self.left_column)
        self.scripture_reference_group_box.setObjectName('scripture_reference_group_box')
        self.scripture_reference_layout = QtGui.QGridLayout(self.scripture_reference_group_box)
        self.verse_separator_check_box = QtGui.QCheckBox(self.scripture_reference_group_box)
        self.verse_separator_check_box.setObjectName('verse_separator_check_box')
        self.scripture_reference_layout.addWidget(self.verse_separator_check_box, 0, 0)
        self.verse_separator_line_edit = QtGui.QLineEdit(self.scripture_reference_group_box)
        self.verse_separator_line_edit.setObjectName('verse_separator_line_edit')
        self.scripture_reference_layout.addWidget(self.verse_separator_line_edit, 0, 1)
        self.range_separator_check_box = QtGui.QCheckBox(self.scripture_reference_group_box)
        self.range_separator_check_box.setObjectName('range_separator_check_box')
        self.scripture_reference_layout.addWidget(self.range_separator_check_box, 1, 0)
        self.range_separator_line_edit = QtGui.QLineEdit(self.scripture_reference_group_box)
        self.range_separator_line_edit.setObjectName('range_separator_line_edit')
        self.scripture_reference_layout.addWidget(self.range_separator_line_edit, 1, 1)
        self.list_separator_check_box = QtGui.QCheckBox(self.scripture_reference_group_box)
        self.list_separator_check_box.setObjectName('list_separator_check_box')
        self.scripture_reference_layout.addWidget(self.list_separator_check_box, 2, 0)
        self.list_separator_line_edit = QtGui.QLineEdit(self.scripture_reference_group_box)
        self.list_separator_line_edit.setObjectName('list_separator_line_edit')
        self.scripture_reference_layout.addWidget(self.list_separator_line_edit, 2, 1)
        self.end_separator_check_box = QtGui.QCheckBox(self.scripture_reference_group_box)
        self.end_separator_check_box.setObjectName('end_separator_check_box')
        self.scripture_reference_layout.addWidget(self.end_separator_check_box, 3, 0)
        self.end_separator_line_edit = QtGui.QLineEdit(self.scripture_reference_group_box)
        self.end_separator_line_edit.setObjectName('end_separator_line_edit')
        self.end_separator_line_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r'[^0-9]*'),
                                                  self.end_separator_line_edit))
        self.scripture_reference_layout.addWidget(self.end_separator_line_edit, 3, 1)
        self.left_layout.addWidget(self.scripture_reference_group_box)
        self.right_column.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.language_selection_group_box = QtGui.QGroupBox(self.right_column)
        self.language_selection_group_box.setObjectName('language_selection_group_box')
        self.language_selection_layout = QtGui.QVBoxLayout(self.language_selection_group_box)
        self.language_selection_label = QtGui.QLabel(self.language_selection_group_box)
        self.language_selection_label.setObjectName('language_selection_label')
        self.language_selection_combo_box = QtGui.QComboBox(self.language_selection_group_box)
        self.language_selection_combo_box.setObjectName('language_selection_combo_box')
        self.language_selection_combo_box.addItems(['', '', ''])
        self.language_selection_layout.addWidget(self.language_selection_label)
        self.language_selection_layout.addWidget(self.language_selection_combo_box)
        self.right_layout.addWidget(self.language_selection_group_box)
        self.left_layout.addStretch()
        self.right_layout.addStretch()
        # Signals and slots
        self.is_verse_number_visible_check_box.stateChanged.connect(self.on_is_verse_number_visible_check_box_changed)
        self.new_chapters_check_box.stateChanged.connect(self.on_new_chapters_check_box_changed)
        self.display_style_combo_box.activated.connect(self.on_display_style_combo_box_changed)
        self.bible_theme_combo_box.activated.connect(self.on_bible_theme_combo_box_changed)
        self.layout_style_combo_box.activated.connect(self.on_layout_style_combo_box_changed)
        self.bible_second_check_box.stateChanged.connect(self.on_bible_second_check_box)
        self.verse_separator_check_box.clicked.connect(self.on_verse_separator_check_box_clicked)
        self.verse_separator_line_edit.textEdited.connect(self.on_verse_separator_line_edit_edited)
        self.verse_separator_line_edit.editingFinished.connect(self.on_verse_separator_line_edit_finished)
        self.range_separator_check_box.clicked.connect(self.on_range_separator_check_box_clicked)
        self.range_separator_line_edit.textEdited.connect(self.on_range_separator_line_edit_edited)
        self.range_separator_line_edit.editingFinished.connect(self.on_range_separator_line_edit_finished)
        self.list_separator_check_box.clicked.connect(self.on_list_separator_check_box_clicked)
        self.list_separator_line_edit.textEdited.connect(self.on_list_separator_line_edit_edited)
        self.list_separator_line_edit.editingFinished.connect(self.on_list_separator_line_edit_finished)
        self.end_separator_check_box.clicked.connect(self.on_end_separator_check_box_clicked)
        self.end_separator_line_edit.textEdited.connect(self.on_end_separator_line_edit_edited)
        self.end_separator_line_edit.editingFinished.connect(self.on_end_separator_line_edit_finished)
        Registry().register_function('theme_update_list', self.update_theme_list)
        self.language_selection_combo_box.activated.connect(self.on_language_selection_combo_box_changed)

    def retranslateUi(self):
        self.verse_display_group_box.setTitle(translate('BiblesPlugin.BiblesTab', 'Verse Display'))
        self.is_verse_number_visible_check_box.setText(translate('BiblesPlugin.BiblesTab', 'Show verse numbers'))
        self.new_chapters_check_box.setText(translate('BiblesPlugin.BiblesTab', 'Only show new chapter numbers'))
        self.layout_style_label.setText(UiStrings().LayoutStyle)
        self.display_style_label.setText(UiStrings().DisplayStyle)
        self.bible_theme_label.setText(translate('BiblesPlugin.BiblesTab', 'Bible theme:'))
        self.layout_style_combo_box.setItemText(LayoutStyle.VersePerSlide, UiStrings().VersePerSlide)
        self.layout_style_combo_box.setItemText(LayoutStyle.VersePerLine, UiStrings().VersePerLine)
        self.layout_style_combo_box.setItemText(LayoutStyle.Continuous, UiStrings().Continuous)
        self.display_style_combo_box.setItemText(DisplayStyle.NoBrackets,
                                                 translate('BiblesPlugin.BiblesTab', 'No Brackets'))
        self.display_style_combo_box.setItemText(DisplayStyle.Round,
                                                 translate('BiblesPlugin.BiblesTab', '( And )'))
        self.display_style_combo_box.setItemText(DisplayStyle.Curly,
                                                 translate('BiblesPlugin.BiblesTab', '{ And }'))
        self.display_style_combo_box.setItemText(DisplayStyle.Square,
                                                 translate('BiblesPlugin.BiblesTab', '[ And ]'))
        self.change_note_label.setText(translate('BiblesPlugin.BiblesTab',
                                       'Note:\nChanges do not affect verses already in the service.'))
        self.bible_second_check_box.setText(translate('BiblesPlugin.BiblesTab', 'Display second Bible verses'))
        self.scripture_reference_group_box.setTitle(translate('BiblesPlugin.BiblesTab', 'Custom Scripture References'))
        self.verse_separator_check_box.setText(translate('BiblesPlugin.BiblesTab', 'Verse Separator:'))
        self.range_separator_check_box.setText(translate('BiblesPlugin.BiblesTab', 'Range Separator:'))
        self.list_separator_check_box.setText(translate('BiblesPlugin.BiblesTab', 'List Separator:'))
        self.end_separator_check_box.setText(translate('BiblesPlugin.BiblesTab', 'End Mark:'))
        tip_text = translate('BiblesPlugin.BiblesTab',
                             'Multiple alternative verse separators may be defined.\nThey have to be separated by a '
                             'vertical bar "|".\nPlease clear this edit line to use the default value.')
        self.verse_separator_line_edit.setToolTip(tip_text)
        self.range_separator_line_edit.setToolTip(tip_text)
        self.list_separator_line_edit.setToolTip(tip_text)
        self.end_separator_line_edit.setToolTip(tip_text)
        self.language_selection_group_box.setTitle(translate('BiblesPlugin.BiblesTab', 'Default Bible Language'))
        self.language_selection_label.setText(
            translate('BiblesPlugin.BiblesTab', 'Book name language in search field,\nsearch results and on display:'))
        self.language_selection_combo_box.setItemText(
            LanguageSelection.Bible, translate('BiblesPlugin.BiblesTab', 'Bible Language'))
        self.language_selection_combo_box.setItemText(
            LanguageSelection.Application, translate('BiblesPlugin.BiblesTab', 'Application Language'))
        self.language_selection_combo_box.setItemText(
            LanguageSelection.English, translate('BiblesPlugin.BiblesTab', 'English'))

    def on_bible_theme_combo_box_changed(self):
        self.bible_theme = self.bible_theme_combo_box.currentText()

    def on_display_style_combo_box_changed(self):
        self.display_style = self.display_style_combo_box.currentIndex()

    def on_layout_style_combo_box_changed(self):
        self.layout_style = self.layout_style_combo_box.currentIndex()

    def on_language_selection_combo_box_changed(self):
        self.language_selection = self.language_selection_combo_box.currentIndex()

    def on_is_verse_number_visible_check_box_changed(self, check_state):
        """
        Event handler for the 'verse number visible' check box
        """
        self.is_verse_number_visible = (check_state == QtCore.Qt.Checked)
        self.check_is_verse_number_visible()

    def on_new_chapters_check_box_changed(self, check_state):
        self.show_new_chapters = False
        # We have a set value convert to True/False.
        if check_state == QtCore.Qt.Checked:
            self.show_new_chapters = True

    def on_bible_second_check_box(self, check_state):
        self.second_bibles = False
        # We have a set value convert to True/False.
        if check_state == QtCore.Qt.Checked:
            self.second_bibles = True

    def on_verse_separator_check_box_clicked(self, checked):
        if checked:
            self.verse_separator_line_edit.setFocus()
        else:
            self.verse_separator_line_edit.setText(get_reference_separator('sep_v_default'))
        self.verse_separator_line_edit.setPalette(self.get_grey_text_palette(not checked))

    def on_verse_separator_line_edit_edited(self, text):
        self.verse_separator_check_box.setChecked(True)
        self.verse_separator_line_edit.setPalette(self.get_grey_text_palette(False))

    def on_verse_separator_line_edit_finished(self):
        if self.verse_separator_line_edit.isModified():
            text = self.verse_separator_line_edit.text()
            if text == get_reference_separator('sep_v_default') or not text.replace('|', ''):
                self.verse_separator_check_box.setChecked(False)
                self.verse_separator_line_edit.setText(get_reference_separator('sep_v_default'))
                self.verse_separator_line_edit.setPalette(self.get_grey_text_palette(True))

    def on_range_separator_check_box_clicked(self, checked):
        if checked:
            self.range_separator_line_edit.setFocus()
        else:
            self.range_separator_line_edit.setText(get_reference_separator('sep_r_default'))
        self.range_separator_line_edit.setPalette(self.get_grey_text_palette(not checked))

    def on_range_separator_line_edit_edited(self, text):
        self.range_separator_check_box.setChecked(True)
        self.range_separator_line_edit.setPalette(self.get_grey_text_palette(False))

    def on_range_separator_line_edit_finished(self):
        if self.range_separator_line_edit.isModified():
            text = self.range_separator_line_edit.text()
            if text == get_reference_separator('sep_r_default') or not text.replace('|', ''):
                self.range_separator_check_box.setChecked(False)
                self.range_separator_line_edit.setText(get_reference_separator('sep_r_default'))
                self.range_separator_line_edit.setPalette(self.get_grey_text_palette(True))

    def on_list_separator_check_box_clicked(self, checked):
        if checked:
            self.list_separator_line_edit.setFocus()
        else:
            self.list_separator_line_edit.setText(get_reference_separator('sep_l_default'))
        self.list_separator_line_edit.setPalette(self.get_grey_text_palette(not checked))

    def on_list_separator_line_edit_edited(self, text):
        self.list_separator_check_box.setChecked(True)
        self.list_separator_line_edit.setPalette(self.get_grey_text_palette(False))

    def on_list_separator_line_edit_finished(self):
        if self.list_separator_line_edit.isModified():
            text = self.list_separator_line_edit.text()
            if text == get_reference_separator('sep_l_default') or not text.replace('|', ''):
                self.list_separator_check_box.setChecked(False)
                self.list_separator_line_edit.setText(get_reference_separator('sep_l_default'))
                self.list_separator_line_edit.setPalette(self.get_grey_text_palette(True))

    def on_end_separator_check_box_clicked(self, checked):
        if checked:
            self.end_separator_line_edit.setFocus()
        else:
            self.end_separator_line_edit.setText(get_reference_separator('sep_e_default'))
        self.end_separator_line_edit.setPalette(self.get_grey_text_palette(not checked))

    def on_end_separator_line_edit_edited(self, text):
        self.end_separator_check_box.setChecked(True)
        self.end_separator_line_edit.setPalette(self.get_grey_text_palette(False))

    def on_end_separator_line_edit_finished(self):
        if self.end_separator_line_edit.isModified():
            text = self.end_separator_line_edit.text()
            if text == get_reference_separator('sep_e_default') or not text.replace('|', ''):
                self.end_separator_check_box.setChecked(False)
                self.end_separator_line_edit.setText(get_reference_separator('sep_e_default'))
                self.end_separator_line_edit.setPalette(self.get_grey_text_palette(True))

    def load(self):
        settings = Settings()
        settings.beginGroup(self.settings_section)
        self.is_verse_number_visible = settings.value('is verse number visible')
        self.show_new_chapters = settings.value('display new chapter')
        self.display_style = settings.value('display brackets')
        self.layout_style = settings.value('verse layout style')
        self.bible_theme = settings.value('bible theme')
        self.second_bibles = settings.value('second bibles')
        self.is_verse_number_visible_check_box.setChecked(self.is_verse_number_visible)
        self.check_is_verse_number_visible()
        self.new_chapters_check_box.setChecked(self.show_new_chapters)
        self.display_style_combo_box.setCurrentIndex(self.display_style)
        self.layout_style_combo_box.setCurrentIndex(self.layout_style)
        self.bible_second_check_box.setChecked(self.second_bibles)
        verse_separator = settings.value('verse separator')
        if (verse_separator.strip('|') == '') or (verse_separator == get_reference_separator('sep_v_default')):
            self.verse_separator_line_edit.setText(get_reference_separator('sep_v_default'))
            self.verse_separator_line_edit.setPalette(self.get_grey_text_palette(True))
            self.verse_separator_check_box.setChecked(False)
        else:
            self.verse_separator_line_edit.setText(verse_separator)
            self.verse_separator_line_edit.setPalette(self.get_grey_text_palette(False))
            self.verse_separator_check_box.setChecked(True)
        range_separator = settings.value('range separator')
        if (range_separator.strip('|') == '') or (range_separator == get_reference_separator('sep_r_default')):
            self.range_separator_line_edit.setText(get_reference_separator('sep_r_default'))
            self.range_separator_line_edit.setPalette(self.get_grey_text_palette(True))
            self.range_separator_check_box.setChecked(False)
        else:
            self.range_separator_line_edit.setText(range_separator)
            self.range_separator_line_edit.setPalette(self.get_grey_text_palette(False))
            self.range_separator_check_box.setChecked(True)
        list_separator = settings.value('list separator')
        if (list_separator.strip('|') == '') or (list_separator == get_reference_separator('sep_l_default')):
            self.list_separator_line_edit.setText(get_reference_separator('sep_l_default'))
            self.list_separator_line_edit.setPalette(self.get_grey_text_palette(True))
            self.list_separator_check_box.setChecked(False)
        else:
            self.list_separator_line_edit.setText(list_separator)
            self.list_separator_line_edit.setPalette(self.get_grey_text_palette(False))
            self.list_separator_check_box.setChecked(True)
        end_separator = settings.value('end separator')
        if (end_separator.strip('|') == '') or (end_separator == get_reference_separator('sep_e_default')):
            self.end_separator_line_edit.setText(get_reference_separator('sep_e_default'))
            self.end_separator_line_edit.setPalette(self.get_grey_text_palette(True))
            self.end_separator_check_box.setChecked(False)
        else:
            self.end_separator_line_edit.setText(end_separator)
            self.end_separator_line_edit.setPalette(self.get_grey_text_palette(False))
            self.end_separator_check_box.setChecked(True)
        self.language_selection = settings.value('book name language')
        self.language_selection_combo_box.setCurrentIndex(self.language_selection)
        settings.endGroup()

    def save(self):
        settings = Settings()
        settings.beginGroup(self.settings_section)
        settings.setValue('is verse number visible', self.is_verse_number_visible)
        settings.setValue('display new chapter', self.show_new_chapters)
        settings.setValue('display brackets', self.display_style)
        settings.setValue('verse layout style', self.layout_style)
        settings.setValue('second bibles', self.second_bibles)
        settings.setValue('bible theme', self.bible_theme)
        if self.verse_separator_check_box.isChecked():
            settings.setValue('verse separator', self.verse_separator_line_edit.text())
        else:
            settings.remove('verse separator')
        if self.range_separator_check_box.isChecked():
            settings.setValue('range separator', self.range_separator_line_edit.text())
        else:
            settings.remove('range separator')
        if self.list_separator_check_box.isChecked():
            settings.setValue('list separator', self.list_separator_line_edit.text())
        else:
            settings.remove('list separator')
        if self.end_separator_check_box.isChecked():
            settings.setValue('end separator', self.end_separator_line_edit.text())
        else:
            settings.remove('end separator')
        update_reference_separators()
        if self.language_selection != settings.value('book name language'):
            settings.setValue('book name language', self.language_selection)
            self.settings_form.register_post_process('bibles_load_list')
        settings.endGroup()
        if self.tab_visited:
            self.settings_form.register_post_process('bibles_config_updated')
        self.tab_visited = False

    def update_theme_list(self, theme_list):
        """
        Called from ThemeManager when the Themes have changed.

        :param theme_list:
            The list of available themes::

                ['Bible Theme', 'Song Theme']
        """
        self.bible_theme_combo_box.clear()
        self.bible_theme_combo_box.addItem('')
        self.bible_theme_combo_box.addItems(theme_list)
        find_and_set_in_combo_box(self.bible_theme_combo_box, self.bible_theme)

    def get_grey_text_palette(self, greyed):
        """
        Returns a QPalette with greyed out text as used for placeholderText.
        """
        palette = QtGui.QPalette()
        color = self.palette().color(QtGui.QPalette.Active, QtGui.QPalette.Text)
        if greyed:
            color.setAlpha(128)
        palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Text, color)
        return palette

    def check_is_verse_number_visible(self):
        """
        Enables / Disables verse settings dependent on is_verse_number_visible
        """
        self.new_chapters_check_box.setEnabled(self.is_verse_number_visible)
        self.display_style_label.setEnabled(self.is_verse_number_visible)
        self.display_style_combo_box.setEnabled(self.is_verse_number_visible)
