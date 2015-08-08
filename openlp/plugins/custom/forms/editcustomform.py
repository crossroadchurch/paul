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

from PyQt4 import QtGui

from openlp.core.common import Registry, translate
from openlp.core.lib.ui import critical_error_message_box, find_and_set_in_combo_box
from openlp.plugins.custom.lib import CustomXMLBuilder, CustomXMLParser
from openlp.plugins.custom.lib.db import CustomSlide
from .editcustomdialog import Ui_CustomEditDialog
from .editcustomslideform import EditCustomSlideForm

log = logging.getLogger(__name__)


class EditCustomForm(QtGui.QDialog, Ui_CustomEditDialog):
    """
    Class documentation goes here.
    """
    log.info('Custom Editor loaded')

    def __init__(self, media_item, parent, manager):
        """
        Constructor
        """
        super(EditCustomForm, self).__init__(parent)
        self.manager = manager
        self.media_item = media_item
        self.setupUi(self)
        # Create other objects and forms.
        self.edit_slide_form = EditCustomSlideForm(self)
        # Connecting signals and slots
        self.preview_button.clicked.connect(self.on_preview_button_clicked)
        self.add_button.clicked.connect(self.on_add_button_clicked)
        self.edit_button.clicked.connect(self.on_edit_button_clicked)
        self.edit_all_button.clicked.connect(self.on_edit_all_button_clicked)
        self.slide_list_view.currentRowChanged.connect(self.on_current_row_changed)
        self.slide_list_view.doubleClicked.connect(self.on_edit_button_clicked)
        Registry().register_function('theme_update_list', self.load_themes)

    def load_themes(self, theme_list):
        """
        Load a list of themes into the themes combo box.

        :param theme_list: The list of themes to load.
        """
        self.theme_combo_box.clear()
        self.theme_combo_box.addItem('')
        self.theme_combo_box.addItems(theme_list)

    def load_custom(self, id, preview=False):
        """
        Called when editing or creating a new custom.

        :param id: The custom's id. If zero, then a new custom is created.
        :param preview: States whether the custom is edited while being previewed in the preview panel.
        """
        self.slide_list_view.clear()
        if id == 0:
            self.custom_slide = CustomSlide()
            self.title_edit.setText('')
            self.credit_edit.setText('')
            self.theme_combo_box.setCurrentIndex(0)
        else:
            self.custom_slide = self.manager.get_object(CustomSlide, id)
            self.title_edit.setText(self.custom_slide.title)
            self.credit_edit.setText(self.custom_slide.credits)
            custom_xml = CustomXMLParser(self.custom_slide.text)
            slide_list = custom_xml.get_verses()
            self.slide_list_view.addItems([slide[1] for slide in slide_list])
            theme = self.custom_slide.theme_name
            find_and_set_in_combo_box(self.theme_combo_box, theme)
        self.title_edit.setFocus()
        # If not preview hide the preview button.
        self.preview_button.setVisible(preview)

    def accept(self):
        """
        Override the QDialog method to check if the custom slide has been saved before closing the dialog.
        """
        log.debug('accept')
        if self.save_custom():
            QtGui.QDialog.accept(self)

    def save_custom(self):
        """
        Saves the custom.
        """
        if not self._validate():
            return False
        sxml = CustomXMLBuilder()
        for count in range(self.slide_list_view.count()):
            sxml.add_verse_to_lyrics('custom', str(count + 1), self.slide_list_view.item(count).text())
        self.custom_slide.title = self.title_edit.text()
        self.custom_slide.text = str(sxml.extract_xml(), 'utf-8')
        self.custom_slide.credits = self.credit_edit.text()
        self.custom_slide.theme_name = self.theme_combo_box.currentText()
        success = self.manager.save_object(self.custom_slide)
        self.media_item.auto_select_id = self.custom_slide.id
        return success

    def on_up_button_clicked(self):
        """
        Move a slide up in the list when the "Up" button is clicked.
        """
        selected_row = self.slide_list_view.currentRow()
        if selected_row != 0:
            qw = self.slide_list_view.takeItem(selected_row)
            self.slide_list_view.insertItem(selected_row - 1, qw)
            self.slide_list_view.setCurrentRow(selected_row - 1)

    def on_down_button_clicked(self):
        """
        Move a slide down in the list when the "Down" button is clicked.
        """
        selected_row = self.slide_list_view.currentRow()
        # zero base arrays
        if selected_row != self.slide_list_view.count() - 1:
            qw = self.slide_list_view.takeItem(selected_row)
            self.slide_list_view.insertItem(selected_row + 1, qw)
            self.slide_list_view.setCurrentRow(selected_row + 1)

    def on_add_button_clicked(self):
        """
        Add a new blank slide.
        """
        self.edit_slide_form.set_text('')
        if self.edit_slide_form.exec_():
            self.slide_list_view.addItems(self.edit_slide_form.get_text())

    def on_edit_button_clicked(self):
        """
        Edit the currently selected slide.
        """
        self.edit_slide_form.set_text(self.slide_list_view.currentItem().text())
        if self.edit_slide_form.exec_():
            self.update_slide_list(self.edit_slide_form.get_text())

    def on_edit_all_button_clicked(self):
        """
        Edits all slides.
        """
        slide_text = ''
        for row in range(self.slide_list_view.count()):
            item = self.slide_list_view.item(row)
            slide_text += item.text()
            if row != self.slide_list_view.count() - 1:
                slide_text += '\n[===]\n'
        self.edit_slide_form.set_text(slide_text)
        if self.edit_slide_form.exec_():
            self.update_slide_list(self.edit_slide_form.get_text(), True)

    def on_preview_button_clicked(self):
        """
        Save the custom item and preview it.
        """
        log.debug('onPreview')
        if self.save_custom():
            Registry().execute('custom_preview')

    def update_slide_list(self, slides, edit_all=False):
        """
        Updates the slide list after editing slides.

        :param slides: A list of all slides which have been edited.
        :param edit_all:  Indicates if all slides or only one slide has been edited.
        """
        if edit_all:
            self.slide_list_view.clear()
            self.slide_list_view.addItems(slides)
        else:
            old_row = self.slide_list_view.currentRow()
            # Create a list with all (old/unedited) slides.
            old_slides = [self.slide_list_view.item(row).text() for row in range(self.slide_list_view.count())]
            self.slide_list_view.clear()
            old_slides.pop(old_row)
            # Insert all slides to make the old_slides list complete.
            for slide in slides:
                old_slides.insert(old_row, slide)
            self.slide_list_view.addItems(old_slides)
        self.slide_list_view.repaint()

    def on_delete_button_clicked(self):
        """
        Removes the current row from the list.
        """
        self.slide_list_view.takeItem(self.slide_list_view.currentRow())
        self.on_current_row_changed(self.slide_list_view.currentRow())

    def on_current_row_changed(self, row):
        """
        Called when the *slide_list_view*'s current row has been changed. This
        enables or disables buttons which require an slide to act on.

        :param row: The row (int). If there is no current row, the value is -1.
        """
        if row == -1:
            self.delete_button.setEnabled(False)
            self.edit_button.setEnabled(False)
            self.up_button.setEnabled(False)
            self.down_button.setEnabled(False)
        else:
            self.delete_button.setEnabled(True)
            self.edit_button.setEnabled(True)
            # Decide if the up/down buttons should be enabled or not.
            self.down_button.setEnabled(self.slide_list_view.count() - 1 != row)
            self.up_button.setEnabled(row != 0)

    def _validate(self):
        """
        Checks whether a custom is valid or not.
        """
        # We must have a title.
        if not self.title_edit.displayText():
            self.title_edit.setFocus()
            critical_error_message_box(message=translate('CustomPlugin.EditCustomForm', 'You need to type in a title.'))
            return False
        # We must have at least one slide.
        if self.slide_list_view.count() == 0:
            critical_error_message_box(message=translate('CustomPlugin.EditCustomForm',
                                                         'You need to add at least one slide.'))
            return False
        return True
