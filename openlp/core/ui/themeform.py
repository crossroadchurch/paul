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
The Theme wizard
"""
import logging
import os

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, RegistryProperties, UiStrings, translate
from openlp.core.lib.theme import BackgroundType, BackgroundGradientType, PositionType
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui import ThemeLayoutForm
from openlp.core.utils import get_images_filter, is_not_image_file
from .themewizard import Ui_ThemeWizard

log = logging.getLogger(__name__)


class ThemeForm(QtGui.QWizard, Ui_ThemeWizard, RegistryProperties):
    """
    This is the Theme Import Wizard, which allows easy creation and editing of
    OpenLP themes.
    """
    log.info('ThemeWizardForm loaded')

    def __init__(self, parent):
        """
        Instantiate the wizard, and run any extra setup we need to.

        :param parent: The QWidget-derived parent of the wizard.
        """
        super(ThemeForm, self).__init__(parent)
        self._setup()

    def _setup(self):
        """
        Set up the class. This method is mocked out by the tests.
        """
        self.setupUi(self)
        self.registerFields()
        self.update_theme_allowed = True
        self.temp_background_filename = ''
        self.theme_layout_form = ThemeLayoutForm(self)
        self.background_combo_box.currentIndexChanged.connect(self.on_background_combo_box_current_index_changed)
        self.gradient_combo_box.currentIndexChanged.connect(self.on_gradient_combo_box_current_index_changed)
        self.color_button.colorChanged.connect(self.on_color_changed)
        self.image_color_button.colorChanged.connect(self.on_image_color_changed)
        self.gradient_start_button.colorChanged.connect(self.on_gradient_start_color_changed)
        self.gradient_end_button.colorChanged.connect(self.on_gradient_end_color_changed)
        self.image_browse_button.clicked.connect(self.on_image_browse_button_clicked)
        self.image_file_edit.editingFinished.connect(self.on_image_file_edit_editing_finished)
        self.main_color_button.colorChanged.connect(self.on_main_color_changed)
        self.outline_color_button.colorChanged.connect(self.on_outline_color_changed)
        self.shadow_color_button.colorChanged.connect(self.on_shadow_color_changed)
        self.outline_check_box.stateChanged.connect(self.on_outline_check_check_box_state_changed)
        self.shadow_check_box.stateChanged.connect(self.on_shadow_check_check_box_state_changed)
        self.footer_color_button.colorChanged.connect(self.on_footer_color_changed)
        self.customButtonClicked.connect(self.on_custom_1_button_clicked)
        self.main_position_check_box.stateChanged.connect(self.on_main_position_check_box_state_changed)
        self.footer_position_check_box.stateChanged.connect(self.on_footer_position_check_box_state_changed)
        self.currentIdChanged.connect(self.on_current_id_changed)
        Registry().register_function('theme_line_count', self.update_lines_text)
        self.main_size_spin_box.valueChanged.connect(self.calculate_lines)
        self.line_spacing_spin_box.valueChanged.connect(self.calculate_lines)
        self.outline_size_spin_box.valueChanged.connect(self.calculate_lines)
        self.shadow_size_spin_box.valueChanged.connect(self.calculate_lines)
        self.main_font_combo_box.activated.connect(self.calculate_lines)
        self.footer_font_combo_box.activated.connect(self.update_theme)
        self.footer_size_spin_box.valueChanged.connect(self.update_theme)
        self.main_position_method.currentIndexChanged.connect(self.on_main_position_method_changed)
        

    def set_defaults(self):
        """
        Set up display at start of theme edit.
        """
        self.restart()
        self.set_background_page_values()
        self.set_main_area_page_values()
        self.set_footer_area_page_values()
        self.set_alignment_page_values()
        self.set_position_page_values()
        self.set_preview_page_values()

    def registerFields(self):
        """
        Map field names to screen names,
        """
        self.background_page.registerField('background_type', self.background_combo_box)
        self.background_page.registerField('color', self.color_button)
        self.background_page.registerField('gradient_start', self.gradient_start_button)
        self.background_page.registerField('gradient_end', self.gradient_end_button)
        self.background_page.registerField('background_image', self.image_file_edit)
        self.background_page.registerField('gradient', self.gradient_combo_box)
        self.main_area_page.registerField('main_color_button', self.main_color_button)
        self.main_area_page.registerField('main_size_spin_box', self.main_size_spin_box)
        self.main_area_page.registerField('line_spacing_spin_box', self.line_spacing_spin_box)
        self.main_area_page.registerField('outline_check_box', self.outline_check_box)
        self.main_area_page.registerField('outline_color_button', self.outline_color_button)
        self.main_area_page.registerField('outline_size_spin_box', self.outline_size_spin_box)
        self.main_area_page.registerField('shadow_check_box', self.shadow_check_box)
        self.main_area_page.registerField('main_bold_check_box', self.main_bold_check_box)
        self.main_area_page.registerField('main_italics_check_box', self.main_italics_check_box)
        self.main_area_page.registerField('shadow_color_button', self.shadow_color_button)
        self.main_area_page.registerField('shadow_size_spin_box', self.shadow_size_spin_box)
        self.main_area_page.registerField('footer_size_spin_box', self.footer_size_spin_box)
        self.area_position_page.registerField('main_position_method', self.main_position_method)
        self.area_position_page.registerField('main_position_x', self.main_x_spin_box)
        self.area_position_page.registerField('main_position_y', self.main_y_spin_box)
        self.area_position_page.registerField('main_position_width', self.main_width_spin_box)
        self.area_position_page.registerField('main_position_height', self.main_height_spin_box)
        self.area_position_page.registerField('footer_position_x', self.footer_x_spin_box)
        self.area_position_page.registerField('footer_position_y', self.footer_y_spin_box)
        self.area_position_page.registerField('footer_position_width', self.footer_width_spin_box)
        self.area_position_page.registerField('footer_position_height', self.footer_height_spin_box)
        self.background_page.registerField('horizontal', self.horizontal_combo_box)
        self.background_page.registerField('vertical', self.vertical_combo_box)
        self.background_page.registerField('slide_transition', self.transitions_check_box)
        self.background_page.registerField('name', self.theme_name_edit)
    
    def calculate_lines(self):
        """
        Calculate the number of lines on a page by rendering text
        """
        # Do not trigger on start up
        if self.currentPage != self.welcome_page:
            self.update_theme()
            self.theme_manager.generate_image(self.theme, True)

    def update_lines_text(self, lines):
        """
        Updates the lines on a page on the wizard
        """
        self.main_line_count_label.setText(
            translate('OpenLP.ThemeForm', '(approximately %d lines per slide)') % int(lines))

    def resizeEvent(self, event=None):
        """
        Rescale the theme preview thumbnail on resize events.
        """
        if not event:
            event = QtGui.QResizeEvent(self.size(), self.size())
        QtGui.QWizard.resizeEvent(self, event)
        if self.currentPage() == self.preview_page:
            frame_width = self.preview_box_label.lineWidth()
            pixmap_width = self.preview_area.width() - 2 * frame_width
            pixmap_height = self.preview_area.height() - 2 * frame_width
            aspect_ratio = float(pixmap_width) / pixmap_height
            if aspect_ratio < self.display_aspect_ratio:
                pixmap_height = int(pixmap_width / self.display_aspect_ratio + 0.5)
            else:
                pixmap_width = int(pixmap_height * self.display_aspect_ratio + 0.5)
            self.preview_box_label.setFixedSize(pixmap_width + 2 * frame_width, pixmap_height + 2 * frame_width)

    def validateCurrentPage(self):
        """
        Validate the current page
        """
        background_image = BackgroundType.to_string(BackgroundType.Image)
        if self.page(self.currentId()) == self.background_page and \
                self.theme.background_type == background_image and is_not_image_file(self.theme.background_filename):
            QtGui.QMessageBox.critical(self, translate('OpenLP.ThemeWizard', 'Background Image Empty'),
                                       translate('OpenLP.ThemeWizard', 'You have not selected a '
                                                 'background image. Please select one before continuing.'))
            return False
        else:
            return True

    def on_current_id_changed(self, page_id):
        """
        Detects Page changes and updates as appropriate.
        """
        enabled = self.page(page_id) == self.area_position_page
        self.setOption(QtGui.QWizard.HaveCustomButton1, enabled)
        if self.page(page_id) == self.preview_page:
            self.update_theme()
            frame = self.theme_manager.generate_image(self.theme)
            self.preview_box_label.setPixmap(frame)
            self.display_aspect_ratio = float(frame.width()) / frame.height()
            self.resizeEvent()

    def on_custom_1_button_clicked(self, number):
        """
        Generate layout preview and display the form.
        """
        self.update_theme()
        width = self.renderer.width
        height = self.renderer.height
        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(QtCore.Qt.white)
        paint = QtGui.QPainter(pixmap)
        paint.setPen(QtGui.QPen(QtCore.Qt.blue, 2))
        paint.drawRect(self.renderer.get_main_rectangle(self.theme))
        paint.setPen(QtGui.QPen(QtCore.Qt.red, 2))
        paint.drawRect(self.renderer.get_footer_rectangle(self.theme))
        paint.end()
        self.theme_layout_form.exec_(pixmap)

    def on_outline_check_check_box_state_changed(self, state):
        """
        Change state as Outline check box changed
        """
        if self.update_theme_allowed:
            self.theme.font_main_outline = state == QtCore.Qt.Checked
            self.outline_color_button.setEnabled(self.theme.font_main_outline)
            self.outline_size_spin_box.setEnabled(self.theme.font_main_outline)
            self.calculate_lines()

    def on_shadow_check_check_box_state_changed(self, state):
        """
        Change state as Shadow check box changed
        """
        if self.update_theme_allowed:
            if state == QtCore.Qt.Checked:
                self.theme.font_main_shadow = True
            else:
                self.theme.font_main_shadow = False
            self.shadow_color_button.setEnabled(self.theme.font_main_shadow)
            self.shadow_size_spin_box.setEnabled(self.theme.font_main_shadow)
            self.calculate_lines()

    def on_main_position_check_box_state_changed(self, value):
        """
        Change state as Main Area _position check box changed
        NOTE the font_main_override is the inverse of the check box value
        """
        if self.update_theme_allowed:
            self.theme.font_main_override = not (value == QtCore.Qt.Checked)

    def on_footer_position_check_box_state_changed(self, value):
        """
        Change state as Footer Area _position check box changed
        NOTE the font_footer_override is the inverse of the check box value
        """
        if self.update_theme_allowed:
            self.theme.font_footer_override = not (value == QtCore.Qt.Checked)
            
    
    def on_main_position_method_changed(self, index):
        """
        Change labels for data fields based on position method chosen
        """
        if self.pos_type != index:
            # Save old values before loading new ones
            self.position_data[self.pos_type][0] = self.field('main_position_x')
            self.position_data[self.pos_type][1] = self.field('main_position_y')
            self.position_data[self.pos_type][2] = self.field('main_position_width')
            self.position_data[self.pos_type][3] = self.field('main_position_height')
        if index == PositionType.Classic:
            self.main_x_label.setText(translate('OpenLP.ThemeWizard', 'X position:'))
            self.main_y_label.setText(translate('OpenLP.ThemeWizard', 'Y position:'))
            self.main_width_label.setText(translate('OpenLP.ThemeWizard', 'Width:'))
            self.main_height_label.setText(translate('OpenLP.ThemeWizard', 'Height:'))
            self.main_x_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
            self.main_y_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
            self.main_width_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
            self.main_height_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        elif index == PositionType.Margins:
            self.main_x_label.setText(translate('OpenLP.ThemeWizard', 'Left margin:'))
            self.main_y_label.setText(translate('OpenLP.ThemeWizard', 'Top margin:'))
            self.main_width_label.setText(translate('OpenLP.ThemeWizard', 'Right margin:'))
            self.main_height_label.setText(translate('OpenLP.ThemeWizard', 'Bottom margin:'))
            self.main_x_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
            self.main_y_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
            self.main_width_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
            self.main_height_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        elif index == PositionType.Proportional:
            self.main_x_label.setText(translate('OpenLP.ThemeWizard', 'Left margin:'))
            self.main_y_label.setText(translate('OpenLP.ThemeWizard', 'Top margin:'))
            self.main_width_label.setText(translate('OpenLP.ThemeWizard', 'Right margin:'))
            self.main_height_label.setText(translate('OpenLP.ThemeWizard', 'Bottom margin:'))
            self.main_x_spin_box.setSuffix(translate('OpenLP.ThemeWizard', '%'))
            self.main_y_spin_box.setSuffix(translate('OpenLP.ThemeWizard', '%'))
            self.main_width_spin_box.setSuffix(translate('OpenLP.ThemeWizard', '%'))
            self.main_height_spin_box.setSuffix(translate('OpenLP.ThemeWizard', '%')) 
        self.setField('main_position_x', self.position_data[index][0])
        self.setField('main_position_y', self.position_data[index][1])
        self.setField('main_position_width', self.position_data[index][2])
        self.setField('main_position_height', self.position_data[index][3])
        self.setField('main_position_method', index)
        self.pos_type = index

    def exec_(self, edit=False):
        """
        Run the wizard.
        """
        log.debug('Editing theme %s' % self.theme.theme_name)
        self.temp_background_filename = ''
        self.update_theme_allowed = False
        self.set_defaults()
        self.update_theme_allowed = True
        self.theme_name_label.setVisible(not edit)
        self.theme_name_edit.setVisible(not edit)
        self.edit_mode = edit
        if edit:
            self.setWindowTitle(translate('OpenLP.ThemeWizard', 'Edit Theme - %s') % self.theme.theme_name)
            self.next()
        else:
            self.setWindowTitle(UiStrings().NewTheme)
        return QtGui.QWizard.exec_(self)

    def initializePage(self, page_id):
        """
        Set up the pages for Initial run through dialog
        """
        log.debug('initializePage %s' % page_id)
        wizard_page = self.page(page_id)
        if wizard_page == self.background_page:
            self.set_background_page_values()
        elif wizard_page == self.main_area_page:
            self.set_main_area_page_values()
        elif wizard_page == self.footer_area_page:
            self.set_footer_area_page_values()
        elif wizard_page == self.alignment_page:
            self.set_alignment_page_values()
        elif wizard_page == self.area_position_page:
            self.set_position_page_values()

    def set_background_page_values(self):
        """
        Handle the display and state of the Background page.
        """
        if self.theme.background_type == BackgroundType.to_string(BackgroundType.Solid):
            self.color_button.color = self.theme.background_color
            self.setField('background_type', 0)
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Gradient):
            self.gradient_start_button.color = self.theme.background_start_color
            self.gradient_end_button.color = self.theme.background_end_color
            self.setField('background_type', 1)
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Image):
            self.image_color_button.color = self.theme.background_border_color
            self.image_file_edit.setText(self.theme.background_filename)
            self.setField('background_type', 2)
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Transparent):
            self.setField('background_type', 3)
        if self.theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.Horizontal):
            self.setField('gradient', 0)
        elif self.theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.Vertical):
            self.setField('gradient', 1)
        elif self.theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.Circular):
            self.setField('gradient', 2)
        elif self.theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.LeftTop):
            self.setField('gradient', 3)
        else:
            self.setField('gradient', 4)

    def set_main_area_page_values(self):
        """
        Handle the display and state of the Main Area page.
        """
        self.main_font_combo_box.setCurrentFont(QtGui.QFont(self.theme.font_main_name))
        self.main_color_button.color = self.theme.font_main_color
        self.setField('main_size_spin_box', self.theme.font_main_size)
        self.setField('line_spacing_spin_box', self.theme.font_main_line_adjustment)
        self.setField('outline_check_box', self.theme.font_main_outline)
        self.outline_color_button.color = self.theme.font_main_outline_color
        self.setField('outline_size_spin_box', self.theme.font_main_outline_size)
        self.setField('shadow_check_box', self.theme.font_main_shadow)
        self.shadow_color_button.color = self.theme.font_main_shadow_color
        self.setField('shadow_size_spin_box', self.theme.font_main_shadow_size)
        self.setField('main_bold_check_box', self.theme.font_main_bold)
        self.setField('main_italics_check_box', self.theme.font_main_italics)

    def set_footer_area_page_values(self):
        """
        Handle the display and state of the Footer Area page.
        """
        self.footer_font_combo_box.setCurrentFont(QtGui.QFont(self.theme.font_footer_name))
        self.footer_color_button.color = self.theme.font_footer_color
        self.setField('footer_size_spin_box', self.theme.font_footer_size)

    def set_position_page_values(self):
        """
        Handle the display and state of the _position page.
        """
        # Main Area
        self.main_position_check_box.setChecked(not self.theme.font_main_override)
        self.position_data = [[20, 20, 940, 680],[20, 20, 20, 20],[5, 5, 5, 5]] # Default values for the different position methods
        if hasattr(self.theme, "font_main_pos_type"):
            # This is the new format of the file, including the position tag
            self.pos_type = PositionType.Names.index(self.theme.font_main_pos_type)
            self.position_data[self.pos_type] = [int(self.theme.font_main_data1),
                                                 int(self.theme.font_main_data2),
                                                 int(self.theme.font_main_data3),
                                                 int(self.theme.font_main_data4)]
            
        else:
            # Old style theme file
            self.pos_type = 0
            self.position_data[0] = [int(self.theme.font_main_x),
                                     int(self.theme.font_main_y),
                                     int(self.theme.font_main_width),
                                     int(self.theme.font_main_height)]
                             
        self.setField('main_position_method', self.pos_type)
        self.setField('main_position_x', self.position_data[self.pos_type][0])
        self.setField('main_position_y', self.position_data[self.pos_type][1])
        self.setField('main_position_width', self.position_data[self.pos_type][2])
        self.setField('main_position_height', self.position_data[self.pos_type][3])
        # Footer
        self.footer_position_check_box.setChecked(not self.theme.font_footer_override)
        self.setField('footer_position_x', self.theme.font_footer_x)
        self.setField('footer_position_y', self.theme.font_footer_y)
        self.setField('footer_position_width', self.theme.font_footer_width)
        self.setField('footer_position_height', self.theme.font_footer_height)


    def set_alignment_page_values(self):
        """
        Handle the display and state of the Alignments page.
        """
        self.setField('horizontal', self.theme.display_horizontal_align)
        self.setField('vertical', self.theme.display_vertical_align)
        self.setField('slide_transition', self.theme.display_slide_transition)

    def set_preview_page_values(self):
        """
        Handle the display and state of the Preview page.
        """
        self.setField('name', self.theme.theme_name)

    def on_background_combo_box_current_index_changed(self, index):
        """
        Background style Combo box has changed.
        """
        # do not allow updates when screen is building for the first time.
        if self.update_theme_allowed:
            self.theme.background_type = BackgroundType.to_string(index)
            if self.theme.background_type != BackgroundType.to_string(BackgroundType.Image) and \
                    self.temp_background_filename == '':
                self.temp_background_filename = self.theme.background_filename
                self.theme.background_filename = ''
            if self.theme.background_type == BackgroundType.to_string(BackgroundType.Image) and \
                    self.temp_background_filename != '':
                self.theme.background_filename = self.temp_background_filename
                self.temp_background_filename = ''
            self.set_background_page_values()

    def on_gradient_combo_box_current_index_changed(self, index):
        """
        Background gradient Combo box has changed.
        """
        if self.update_theme_allowed:
            self.theme.background_direction = BackgroundGradientType.to_string(index)
            self.set_background_page_values()

    def on_color_changed(self, color):
        """
        Background / Gradient 1 _color button pushed.
        """
        self.theme.background_color = color

    def on_image_color_changed(self, color):
        """
        Background / Gradient 1 _color button pushed.
        """
        self.theme.background_border_color = color

    def on_gradient_start_color_changed(self, color):
        """
        Gradient 2 _color button pushed.
        """
        self.theme.background_start_color = color

    def on_gradient_end_color_changed(self, color):
        """
        Gradient 2 _color button pushed.
        """
        self.theme.background_end_color = color

    def on_image_browse_button_clicked(self):
        """
        Background Image button pushed.
        """
        images_filter = get_images_filter()
        images_filter = '%s;;%s (*.*)' % (images_filter, UiStrings().AllFiles)
        filename = QtGui.QFileDialog.getOpenFileName(self, translate('OpenLP.ThemeWizard', 'Select Image'),
                                                     self.image_file_edit.text(), images_filter)
        if filename:
            self.theme.background_filename = filename
        self.set_background_page_values()

    def on_image_file_edit_editing_finished(self):
        """
        Background image path edited
        """
        self.theme.background_filename = str(self.image_file_edit.text())

    def on_main_color_changed(self, color):
        """
        Set the main colour value
        """
        self.theme.font_main_color = color

    def on_outline_color_changed(self, color):
        """
        Set the outline colour value
        """
        self.theme.font_main_outline_color = color

    def on_shadow_color_changed(self, color):
        """
        Set the shadow colour value
        """
        self.theme.font_main_shadow_color = color

    def on_footer_color_changed(self, color):
        """
        Set the footer colour value
        """
        self.theme.font_footer_color = color

    def update_theme(self):
        """
        Update the theme object from the UI for fields not already updated
        when they are changed.
        """
        if not self.update_theme_allowed:
            return
        log.debug('update_theme')
        # main page
        self.theme.font_main_name = self.main_font_combo_box.currentFont().family()
        self.theme.font_main_size = self.field('main_size_spin_box')
        self.theme.font_main_line_adjustment = self.field('line_spacing_spin_box')
        self.theme.font_main_outline_size = self.field('outline_size_spin_box')
        self.theme.font_main_shadow_size = self.field('shadow_size_spin_box')
        self.theme.font_main_bold = self.field('main_bold_check_box')
        self.theme.font_main_italics = self.field('main_italics_check_box')
        # footer page
        self.theme.font_footer_name = self.footer_font_combo_box.currentFont().family()
        self.theme.font_footer_size = self.field('footer_size_spin_box')
        # position page
        self.theme.font_main_pos_type = PositionType.Names[self.field('main_position_method')]
        self.theme.font_main_data1 = self.field('main_position_x')
        self.theme.font_main_data2 = self.field('main_position_y')
        self.theme.font_main_data3 = self.field('main_position_width')
        self.theme.font_main_data4 = self.field('main_position_height')
        self.theme.font_main_x = self.field('main_position_x')
        self.theme.font_main_y = self.field('main_position_y')
        self.theme.font_main_height = self.field('main_position_height')
        self.theme.font_main_width = self.field('main_position_width')
        self.theme.font_footer_x = self.field('footer_position_x')
        self.theme.font_footer_y = self.field('footer_position_y')
        self.theme.font_footer_height = self.field('footer_position_height')
        self.theme.font_footer_width = self.field('footer_position_width')
        # position page
        self.theme.display_horizontal_align = self.horizontal_combo_box.currentIndex()
        self.theme.display_vertical_align = self.vertical_combo_box.currentIndex()
        self.theme.display_slide_transition = self.field('slide_transition')

    def accept(self):
        """
        Lets save the theme as Finish has been triggered
        """
        # Save the theme name
        self.theme.theme_name = self.field('name')
        if not self.theme.theme_name:
            critical_error_message_box(
                translate('OpenLP.ThemeWizard', 'Theme Name Missing'),
                translate('OpenLP.ThemeWizard', 'There is no name for this theme. Please enter one.'))
            return
        if self.theme.theme_name == '-1' or self.theme.theme_name == 'None':
            critical_error_message_box(
                translate('OpenLP.ThemeWizard', 'Theme Name Invalid'),
                translate('OpenLP.ThemeWizard', 'Invalid theme name. Please enter one.'))
            return
        save_from = None
        save_to = None
        if self.theme.background_type == BackgroundType.to_string(BackgroundType.Image):
            filename = os.path.split(str(self.theme.background_filename))[1]
            save_to = os.path.join(self.path, self.theme.theme_name, filename)
            save_from = self.theme.background_filename
        if not self.edit_mode and not self.theme_manager.check_if_theme_exists(self.theme.theme_name):
            return
        self.theme_manager.save_theme(self.theme, save_from, save_to)
        return QtGui.QDialog.accept(self)
