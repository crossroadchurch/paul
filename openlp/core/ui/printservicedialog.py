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
The UI widgets of the print service dialog.
"""
from PyQt4 import QtCore, QtGui

from openlp.core.common import UiStrings, translate
from openlp.core.lib import SpellTextEdit, build_icon


class ZoomSize(object):
    """
    Type enumeration for Combo Box sizes
    """
    Page = 0
    Width = 1
    OneHundred = 2
    SeventyFive = 3
    Fifty = 4
    TwentyFive = 5


class Ui_PrintServiceDialog(object):
    """
    The UI of the print service dialog
    """
    def setupUi(self, print_service_dialog):
        """
        Set up the UI
        """
        print_service_dialog.setObjectName('print_service_dialog')
        print_service_dialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        print_service_dialog.resize(664, 594)
        self.main_layout = QtGui.QVBoxLayout(print_service_dialog)
        self.main_layout.setSpacing(0)
        self.main_layout.setMargin(0)
        self.main_layout.setObjectName('main_layout')
        self.toolbar = QtGui.QToolBar(print_service_dialog)
        self.toolbar.setIconSize(QtCore.QSize(22, 22))
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.print_button = self.toolbar.addAction(build_icon(':/general/general_print.png'),
                                                   translate('OpenLP.PrintServiceForm', 'Print'))
        self.options_button = QtGui.QToolButton(self.toolbar)
        self.options_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.options_button.setIcon(build_icon(':/system/system_configure.png'))
        self.options_button.setCheckable(True)
        self.toolbar.addWidget(self.options_button)
        self.toolbar.addSeparator()
        self.plain_copy = self.toolbar.addAction(build_icon(':/system/system_edit_copy.png'),
                                                 translate('OpenLP.PrintServiceForm', 'Copy'))
        self.html_copy = self.toolbar.addAction(build_icon(':/system/system_edit_copy.png'),
                                                translate('OpenLP.PrintServiceForm', 'Copy as HTML'))
        self.toolbar.addSeparator()
        self.zoom_in_button = QtGui.QToolButton(self.toolbar)
        self.zoom_in_button.setIcon(build_icon(':/general/general_zoom_in.png'))
        self.zoom_in_button.setObjectName('zoom_in_button')
        self.zoom_in_button.setIconSize(QtCore.QSize(22, 22))
        self.toolbar.addWidget(self.zoom_in_button)
        self.zoom_out_button = QtGui.QToolButton(self.toolbar)
        self.zoom_out_button.setIcon(build_icon(':/general/general_zoom_out.png'))
        self.zoom_out_button.setObjectName('zoom_out_button')
        self.zoom_out_button.setIconSize(QtCore.QSize(22, 22))
        self.toolbar.addWidget(self.zoom_out_button)
        self.zoom_original_button = QtGui.QToolButton(self.toolbar)
        self.zoom_original_button.setIcon(build_icon(':/general/general_zoom_original.png'))
        self.zoom_original_button.setObjectName('zoom_original_button')
        self.zoom_original_button.setIconSize(QtCore.QSize(22, 22))
        self.toolbar.addWidget(self.zoom_original_button)
        self.zoom_combo_box = QtGui.QComboBox(print_service_dialog)
        self.zoom_combo_box.setObjectName('zoom_combo_box')
        self.toolbar.addWidget(self.zoom_combo_box)
        self.main_layout.addWidget(self.toolbar)
        self.preview_widget = QtGui.QPrintPreviewWidget(print_service_dialog)
        self.main_layout.addWidget(self.preview_widget)
        self.options_widget = QtGui.QWidget(print_service_dialog)
        self.options_widget.hide()
        self.options_widget.resize(400, 300)
        self.options_widget.setAutoFillBackground(True)
        self.options_layout = QtGui.QVBoxLayout(self.options_widget)
        self.options_layout.setContentsMargins(8, 8, 8, 8)
        self.title_label = QtGui.QLabel(self.options_widget)
        self.title_label.setObjectName('title_label')
        self.options_layout.addWidget(self.title_label)
        self.title_line_edit = QtGui.QLineEdit(self.options_widget)
        self.title_line_edit.setObjectName('title_line_edit')
        self.options_layout.addWidget(self.title_line_edit)
        self.footer_label = QtGui.QLabel(self.options_widget)
        self.footer_label.setObjectName('footer_label')
        self.options_layout.addWidget(self.footer_label)
        self.footer_text_edit = SpellTextEdit(self.options_widget, False)
        self.footer_text_edit.setObjectName('footer_text_edit')
        self.options_layout.addWidget(self.footer_text_edit)
        self.options_group_box = QtGui.QGroupBox()
        self.group_layout = QtGui.QVBoxLayout()
        self.slide_text_check_box = QtGui.QCheckBox()
        self.group_layout.addWidget(self.slide_text_check_box)
        self.page_break_after_text = QtGui.QCheckBox()
        self.group_layout.addWidget(self.page_break_after_text)
        self.notes_check_box = QtGui.QCheckBox()
        self.group_layout.addWidget(self.notes_check_box)
        self.meta_data_check_box = QtGui.QCheckBox()
        self.group_layout.addWidget(self.meta_data_check_box)
        self.group_layout.addStretch(1)
        self.options_group_box.setLayout(self.group_layout)
        self.options_layout.addWidget(self.options_group_box)

        self.retranslateUi(print_service_dialog)
        self.options_button.toggled.connect(self.toggle_options)

    def retranslateUi(self, print_service_dialog):
        """
        Translate the UI on the fly
        """
        print_service_dialog.setWindowTitle(UiStrings().PrintService)
        self.zoom_out_button.setToolTip(translate('OpenLP.PrintServiceForm', 'Zoom Out'))
        self.zoom_original_button.setToolTip(translate('OpenLP.PrintServiceForm', 'Zoom Original'))
        self.zoom_in_button.setToolTip(translate('OpenLP.PrintServiceForm', 'Zoom In'))
        self.options_button.setText(translate('OpenLP.PrintServiceForm', 'Options'))
        self.title_label.setText(translate('OpenLP.PrintServiceForm', 'Title:'))
        self.footer_label.setText(translate('OpenLP.PrintServiceForm', 'Custom Footer Text:'))
        self.options_group_box.setTitle(translate('OpenLP.PrintServiceForm', 'Other Options'))
        self.slide_text_check_box.setText(translate('OpenLP.PrintServiceForm', 'Include slide text if available'))
        self.page_break_after_text.setText(translate('OpenLP.PrintServiceForm', 'Add page break before each text item'))
        self.notes_check_box.setText(translate('OpenLP.PrintServiceForm', 'Include service item notes'))
        self.meta_data_check_box.setText(translate('OpenLP.PrintServiceForm', 'Include play length of media items'))
        self.title_line_edit.setText(translate('OpenLP.PrintServiceForm', 'Service Sheet'))
        # Do not change the order.
        self.zoom_combo_box.addItems([
            translate('OpenLP.PrintServiceDialog', 'Fit Page'),
            translate('OpenLP.PrintServiceDialog', 'Fit Width'),
            '100%',
            '75%',
            '50%',
            '25%'
        ])
