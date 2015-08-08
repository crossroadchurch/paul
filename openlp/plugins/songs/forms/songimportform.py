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
The song import functions for OpenLP.
"""
import codecs
import logging
import os

from PyQt4 import QtCore, QtGui

from openlp.core.common import RegistryProperties, Settings, UiStrings, translate
from openlp.core.lib import FileDialog
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.wizard import OpenLPWizard, WizardStrings
from openlp.plugins.songs.lib.importer import SongFormat, SongFormatSelect

log = logging.getLogger(__name__)


class SongImportForm(OpenLPWizard, RegistryProperties):
    """
    This is the Song Import Wizard, which allows easy importing of Songs
    into OpenLP from other formats like OpenLyrics, OpenSong and CCLI.
    """
    log.info('SongImportForm loaded')

    def __init__(self, parent, plugin):
        """
        Instantiate the wizard, and run any extra setup we need to.

        :param parent: The QWidget-derived parent of the wizard.
        :param plugin: The songs plugin.
        """
        super(SongImportForm, self).__init__(parent, plugin, 'songImportWizard', ':/wizards/wizard_importsong.bmp')
        self.clipboard = self.main_window.clipboard

    def setupUi(self, image):
        """
        Set up the song wizard UI.
        """
        self.format_widgets = dict([(song_format, {}) for song_format in SongFormat.get_format_list()])
        super(SongImportForm, self).setupUi(image)
        self.current_format = SongFormat.OpenLyrics
        self.format_stack.setCurrentIndex(self.current_format)
        self.format_combo_box.currentIndexChanged.connect(self.on_current_index_changed)

    def on_current_index_changed(self, index):
        """
        Called when the format combo box's index changed.
        """
        self.current_format = index
        self.format_stack.setCurrentIndex(index)
        self.source_page.emit(QtCore.SIGNAL('completeChanged()'))

    def custom_init(self):
        """
        Song wizard specific initialisation.
        """
        for song_format in SongFormat.get_format_list():
            if not SongFormat.get(song_format, 'availability'):
                self.format_widgets[song_format]['disabled_widget'].setVisible(True)
                self.format_widgets[song_format]['import_widget'].setVisible(False)

    def custom_signals(self):
        """
        Song wizard specific signals.
        """
        for song_format in SongFormat.get_format_list():
            select_mode = SongFormat.get(song_format, 'selectMode')
            if select_mode == SongFormatSelect.MultipleFiles:
                self.format_widgets[song_format]['addButton'].clicked.connect(self.on_add_button_clicked)
                self.format_widgets[song_format]['removeButton'].clicked.connect(self.on_remove_button_clicked)
            else:
                self.format_widgets[song_format]['browseButton'].clicked.connect(self.on_browse_button_clicked)
                self.format_widgets[song_format]['file_path_edit'].textChanged.\
                    connect(self.on_filepath_edit_text_changed)

    def add_custom_pages(self):
        """
        Add song wizard specific pages.
        """
        # Source Page
        self.source_page = SongImportSourcePage()
        self.source_page.setObjectName('source_page')
        self.source_layout = QtGui.QVBoxLayout(self.source_page)
        self.source_layout.setObjectName('source_layout')
        self.format_layout = QtGui.QFormLayout()
        self.format_layout.setObjectName('format_layout')
        self.format_label = QtGui.QLabel(self.source_page)
        self.format_label.setObjectName('format_label')
        self.format_combo_box = QtGui.QComboBox(self.source_page)
        self.format_combo_box.setObjectName('format_combo_box')
        self.format_layout.addRow(self.format_label, self.format_combo_box)
        self.format_spacer = QtGui.QSpacerItem(10, 0, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.format_layout.setItem(1, QtGui.QFormLayout.LabelRole, self.format_spacer)
        self.source_layout.addLayout(self.format_layout)
        self.format_h_spacing = self.format_layout.horizontalSpacing()
        self.format_v_spacing = self.format_layout.verticalSpacing()
        self.format_layout.setVerticalSpacing(0)
        self.stack_spacer = QtGui.QSpacerItem(10, 0, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        self.format_stack = QtGui.QStackedLayout()
        self.format_stack.setObjectName('format_stack')
        self.disablable_formats = []
        for self.current_format in SongFormat.get_format_list():
            self.add_file_select_item()
        self.source_layout.addLayout(self.format_stack)
        self.addPage(self.source_page)

    def retranslateUi(self):
        """
        Song wizard localisation.
        """
        self.setWindowTitle(translate('SongsPlugin.ImportWizardForm', 'Song Import Wizard'))
        self.title_label.setText(WizardStrings.HeaderStyle % translate('OpenLP.Ui',
                                                                       'Welcome to the Song Import Wizard'))
        self.information_label.setText(
            translate('SongsPlugin.ImportWizardForm',
                      'This wizard will help you to import songs from a variety of formats. Click the next button '
                      'below to start the process by selecting a format to import from.'))
        self.source_page.setTitle(WizardStrings.ImportSelect)
        self.source_page.setSubTitle(WizardStrings.ImportSelectLong)
        self.format_label.setText(WizardStrings.FormatLabel)
        for format_list in SongFormat.get_format_list():
            format_name, custom_combo_text, description_text, select_mode = \
                SongFormat.get(format_list, 'name', 'comboBoxText', 'descriptionText', 'selectMode')
            combo_box_text = (custom_combo_text if custom_combo_text else format_name)
            self.format_combo_box.setItemText(format_list, combo_box_text)
            if description_text is not None:
                self.format_widgets[format_list]['description_label'].setText(description_text)
            if select_mode == SongFormatSelect.MultipleFiles:
                self.format_widgets[format_list]['addButton'].setText(
                    translate('SongsPlugin.ImportWizardForm', 'Add Files...'))
                self.format_widgets[format_list]['removeButton'].setText(
                    translate('SongsPlugin.ImportWizardForm', 'Remove File(s)'))
            else:
                self.format_widgets[format_list]['browseButton'].setText(UiStrings().Browse)
                f_label = 'Filename:'
                if select_mode == SongFormatSelect.SingleFolder:
                    f_label = 'Folder:'
                self.format_widgets[format_list]['filepathLabel'].setText(
                    translate('SongsPlugin.ImportWizardForm', f_label))
        for format_list in self.disablable_formats:
            self.format_widgets[format_list]['disabled_label'].setText(SongFormat.get(format_list, 'disabledLabelText'))
        self.progress_page.setTitle(WizardStrings.Importing)
        self.progress_page.setSubTitle(
            translate('SongsPlugin.ImportWizardForm', 'Please wait while your songs are imported.'))
        self.progress_label.setText(WizardStrings.Ready)
        self.progress_bar.setFormat(WizardStrings.PercentSymbolFormat)
        self.error_copy_to_button.setText(translate('SongsPlugin.ImportWizardForm', 'Copy'))
        self.error_save_to_button.setText(translate('SongsPlugin.ImportWizardForm', 'Save to File'))
        # Align all QFormLayouts towards each other.
        formats = [f for f in SongFormat.get_format_list() if 'filepathLabel' in self.format_widgets[f]]
        labels = [self.format_widgets[f]['filepathLabel'] for f in formats]
        # Get max width of all labels
        max_label_width = max(self.format_label.minimumSizeHint().width(),
                              max([label.minimumSizeHint().width() for label in labels]))
        self.format_spacer.changeSize(max_label_width, 0, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        spacers = [self.format_widgets[f]['filepathSpacer'] for f in formats]
        for index, spacer in enumerate(spacers):
            spacer.changeSize(
                max_label_width - labels[index].minimumSizeHint().width(), 0,
                QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        # Align descriptionLabels with rest of layout
        for format_list in SongFormat.get_format_list():
            if SongFormat.get(format_list, 'descriptionText') is not None:
                self.format_widgets[format_list]['descriptionSpacer'].changeSize(
                    max_label_width + self.format_h_spacing, 0, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    def custom_page_changed(self, page_id):
        """
        Called when changing to a page other than the progress page.
        """
        if self.page(page_id) == self.source_page:
            self.on_current_index_changed(self.format_stack.currentIndex())

    def validateCurrentPage(self):
        """
        Re-implement the validateCurrentPage() method. Validate the current page before moving on to the next page.
        Provide each song format class with a chance to validate its input by overriding is_valid_source().
        """
        if self.currentPage() == self.welcome_page:
            return True
        elif self.currentPage() == self.source_page:
            this_format = self.current_format
            Settings().setValue('songs/last import type', this_format)
            select_mode, class_, error_msg = SongFormat.get(this_format, 'selectMode', 'class', 'invalidSourceMsg')
            if select_mode == SongFormatSelect.MultipleFiles:
                import_source = self.get_list_of_files(self.format_widgets[this_format]['file_list_widget'])
                error_title = UiStrings().IFSp
                focus_button = self.format_widgets[this_format]['addButton']
            else:
                import_source = self.format_widgets[this_format]['file_path_edit'].text()
                error_title = (UiStrings().IFSs if select_mode == SongFormatSelect.SingleFile else UiStrings().IFdSs)
                focus_button = self.format_widgets[this_format]['browseButton']
            if not class_.is_valid_source(import_source):
                critical_error_message_box(error_title, error_msg)
                focus_button.setFocus()
                return False
            return True
        elif self.currentPage() == self.progress_page:
            return True

    def get_files(self, title, listbox, filters=''):
        """
        Opens a QFileDialog and writes the filenames to the given listbox.

        :param title: The title of the dialog (str).
        :param listbox: A listbox (QListWidget).
        :param filters: The file extension filters. It should contain the file descriptions as well as the file
            extensions. For example::
                'SongBeamer Files (*.sng)'
        """
        if filters:
            filters += ';;'
        filters += '%s (*)' % UiStrings().AllFiles
        file_names = FileDialog.getOpenFileNames(
            self, title,
            Settings().value(self.plugin.settings_section + '/last directory import'), filters)
        if file_names:
            listbox.addItems(file_names)
            Settings().setValue(self.plugin.settings_section + '/last directory import',
                                os.path.split(str(file_names[0]))[0])

    def get_list_of_files(self, list_box):
        """
        Return a list of file from the list_box

        :param list_box: The source list box
        """
        return [list_box.item(i).text() for i in range(list_box.count())]

    def remove_selected_items(self, list_box):
        """
        Remove selected list_box items

        :param list_box: the source list box
        """
        for item in list_box.selectedItems():
            item = list_box.takeItem(list_box.row(item))
            del item

    def on_browse_button_clicked(self):
        """
        Browse for files or a directory.
        """
        this_format = self.current_format
        select_mode, format_name, ext_filter = SongFormat.get(this_format, 'selectMode', 'name', 'filter')
        file_path_edit = self.format_widgets[this_format]['file_path_edit']
        if select_mode == SongFormatSelect.SingleFile:
            self.get_file_name(
                WizardStrings.OpenTypeFile % format_name, file_path_edit, 'last directory import', ext_filter)
        elif select_mode == SongFormatSelect.SingleFolder:
            self.get_folder(WizardStrings.OpenTypeFolder % format_name, file_path_edit, 'last directory import')

    def on_add_button_clicked(self):
        """
        Add a file or directory.
        """
        this_format = self.current_format
        select_mode, format_name, ext_filter, custom_title = \
            SongFormat.get(this_format, 'selectMode', 'name', 'filter', 'getFilesTitle')
        title = custom_title if custom_title else WizardStrings.OpenTypeFile % format_name
        if select_mode == SongFormatSelect.MultipleFiles:
            self.get_files(title, self.format_widgets[this_format]['file_list_widget'], ext_filter)
            self.source_page.emit(QtCore.SIGNAL('completeChanged()'))

    def on_remove_button_clicked(self):
        """
        Remove a file from the list.
        """
        self.remove_selected_items(self.format_widgets[self.current_format]['file_list_widget'])
        self.source_page.emit(QtCore.SIGNAL('completeChanged()'))

    def on_filepath_edit_text_changed(self):
        """
        Called when the content of the Filename/Folder edit box changes.
        """
        self.source_page.emit(QtCore.SIGNAL('completeChanged()'))

    def set_defaults(self):
        """
        Set default form values for the song import wizard.
        """
        self.restart()
        self.finish_button.setVisible(False)
        self.cancel_button.setVisible(True)
        last_import_type = Settings().value('songs/last import type')
        if last_import_type < 0 or last_import_type >= self.format_combo_box.count():
            last_import_type = 0
        self.format_combo_box.setCurrentIndex(last_import_type)
        for format_list in SongFormat.get_format_list():
            select_mode = SongFormat.get(format_list, 'selectMode')
            if select_mode == SongFormatSelect.MultipleFiles:
                self.format_widgets[format_list]['file_list_widget'].clear()
            else:
                self.format_widgets[format_list]['file_path_edit'].setText('')
        self.error_report_text_edit.clear()
        self.error_report_text_edit.setHidden(True)
        self.error_copy_to_button.setHidden(True)
        self.error_save_to_button.setHidden(True)

    def pre_wizard(self):
        """
        Perform pre import tasks
        """
        super(SongImportForm, self).pre_wizard()
        self.progress_label.setText(WizardStrings.StartingImport)
        self.application.process_events()

    def perform_wizard(self):
        """
        Perform the actual import. This method pulls in the correct importer class, and then runs the ``do_import``
        method of the importer to do the actual importing.
        """
        source_format = self.current_format
        select_mode = SongFormat.get(source_format, 'selectMode')
        if select_mode == SongFormatSelect.SingleFile:
            importer = self.plugin.import_songs(source_format,
                                                filename=self.format_widgets[source_format]['file_path_edit'].text())
        elif select_mode == SongFormatSelect.SingleFolder:
            importer = self.plugin.import_songs(source_format,
                                                folder=self.format_widgets[source_format]['file_path_edit'].text())
        else:
            importer = self.plugin.import_songs(
                source_format,
                filenames=self.get_list_of_files(self.format_widgets[source_format]['file_list_widget']))
        importer.do_import()
        self.progress_label.setText(WizardStrings.FinishedImport)

    def on_error_copy_to_button_clicked(self):
        """
        Copy the error report to the clipboard.
        """
        self.clipboard.setText(self.error_report_text_edit.toPlainText())

    def on_error_save_to_button_clicked(self):
        """
        Save the error report to a file.
        """
        filename = QtGui.QFileDialog.getSaveFileName(
            self, Settings().value(self.plugin.settings_section + '/last directory import'))
        if not filename:
            return
        report_file = codecs.open(filename, 'w', 'utf-8')
        report_file.write(self.error_report_text_edit.toPlainText())
        report_file.close()

    def add_file_select_item(self):
        """
        Add a file selection page.
        """
        this_format = self.current_format
        prefix, can_disable, description_text, select_mode = \
            SongFormat.get(this_format, 'prefix', 'canDisable', 'descriptionText', 'selectMode')
        page = QtGui.QWidget()
        page.setObjectName(prefix + 'Page')
        if can_disable:
            import_widget = self.disablable_widget(page, prefix)
        else:
            import_widget = page
        import_layout = QtGui.QVBoxLayout(import_widget)
        import_layout.setMargin(0)
        import_layout.setObjectName(prefix + 'ImportLayout')
        if description_text is not None:
            description_layout = QtGui.QHBoxLayout()
            description_layout.setObjectName(prefix + 'DescriptionLayout')
            description_spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
            description_layout.addSpacerItem(description_spacer)
            description_label = QtGui.QLabel(import_widget)
            description_label.setWordWrap(True)
            description_label.setOpenExternalLinks(True)
            description_label.setObjectName(prefix + '_description_label')
            description_layout.addWidget(description_label)
            import_layout.addLayout(description_layout)
            self.format_widgets[this_format]['description_label'] = description_label
            self.format_widgets[this_format]['descriptionSpacer'] = description_spacer
        if select_mode == SongFormatSelect.SingleFile or select_mode == SongFormatSelect.SingleFolder:
            file_path_layout = QtGui.QHBoxLayout()
            file_path_layout.setObjectName(prefix + '_file_path_layout')
            file_path_layout.setContentsMargins(0, self.format_v_spacing, 0, 0)
            file_path_label = QtGui.QLabel(import_widget)
            file_path_label.setObjectName(prefix + 'FilepathLabel')
            file_path_layout.addWidget(file_path_label)
            file_path_spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
            file_path_layout.addSpacerItem(file_path_spacer)
            file_path_edit = QtGui.QLineEdit(import_widget)
            file_path_edit.setObjectName(prefix + '_file_path_edit')
            file_path_layout.addWidget(file_path_edit)
            browse_button = QtGui.QToolButton(import_widget)
            browse_button.setIcon(self.open_icon)
            browse_button.setObjectName(prefix + 'BrowseButton')
            file_path_layout.addWidget(browse_button)
            import_layout.addLayout(file_path_layout)
            import_layout.addSpacerItem(self.stack_spacer)
            self.format_widgets[this_format]['filepathLabel'] = file_path_label
            self.format_widgets[this_format]['filepathSpacer'] = file_path_spacer
            self.format_widgets[this_format]['file_path_layout'] = file_path_layout
            self.format_widgets[this_format]['file_path_edit'] = file_path_edit
            self.format_widgets[this_format]['browseButton'] = browse_button
        elif select_mode == SongFormatSelect.MultipleFiles:
            file_list_widget = QtGui.QListWidget(import_widget)
            file_list_widget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
            file_list_widget.setObjectName(prefix + 'FileListWidget')
            import_layout.addWidget(file_list_widget)
            button_layout = QtGui.QHBoxLayout()
            button_layout.setObjectName(prefix + '_button_layout')
            add_button = QtGui.QPushButton(import_widget)
            add_button.setIcon(self.open_icon)
            add_button.setObjectName(prefix + 'AddButton')
            button_layout.addWidget(add_button)
            button_layout.addStretch()
            remove_button = QtGui.QPushButton(import_widget)
            remove_button.setIcon(self.delete_icon)
            remove_button.setObjectName(prefix + 'RemoveButton')
            button_layout.addWidget(remove_button)
            import_layout.addLayout(button_layout)
            self.format_widgets[this_format]['file_list_widget'] = file_list_widget
            self.format_widgets[this_format]['button_layout'] = button_layout
            self.format_widgets[this_format]['addButton'] = add_button
            self.format_widgets[this_format]['removeButton'] = remove_button
        self.format_stack.addWidget(page)
        self.format_widgets[this_format]['page'] = page
        self.format_widgets[this_format]['importLayout'] = import_layout
        self.format_combo_box.addItem('')

    def disablable_widget(self, page, prefix):
        """
        Disable a widget.
        """
        this_format = self.current_format
        self.disablable_formats.append(this_format)
        layout = QtGui.QVBoxLayout(page)
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.setObjectName(prefix + '_layout')
        disabled_widget = QtGui.QWidget(page)
        disabled_widget.setVisible(False)
        disabled_widget.setObjectName(prefix + '_disabled_widget')
        disabled_layout = QtGui.QVBoxLayout(disabled_widget)
        disabled_layout.setMargin(0)
        disabled_layout.setObjectName(prefix + '_disabled_layout')
        disabled_label = QtGui.QLabel(disabled_widget)
        disabled_label.setWordWrap(True)
        disabled_label.setObjectName(prefix + '_disabled_label')
        disabled_layout.addWidget(disabled_label)
        disabled_layout.addSpacerItem(self.stack_spacer)
        layout.addWidget(disabled_widget)
        import_widget = QtGui.QWidget(page)
        import_widget.setObjectName(prefix + '_import_widget')
        layout.addWidget(import_widget)
        self.format_widgets[this_format]['layout'] = layout
        self.format_widgets[this_format]['disabled_widget'] = disabled_widget
        self.format_widgets[this_format]['disabled_layout'] = disabled_layout
        self.format_widgets[this_format]['disabled_label'] = disabled_label
        self.format_widgets[this_format]['import_widget'] = import_widget
        return import_widget


class SongImportSourcePage(QtGui.QWizardPage):
    """
    Subclass of QtGui.QWizardPage to override isComplete() for Source Page.
    """
    def isComplete(self):
        """
        Return True if:

        * an available format is selected, and
        * if MultipleFiles mode, at least one file is selected
        * or if SingleFile mode, the specified file exists
        * or if SingleFolder mode, the specified folder exists

        When this method returns True, the wizard's Next button is enabled.
        """
        wizard = self.wizard()
        this_format = wizard.current_format
        select_mode, format_available = SongFormat.get(this_format, 'selectMode', 'availability')
        if format_available:
            if select_mode == SongFormatSelect.MultipleFiles:
                if wizard.format_widgets[this_format]['file_list_widget'].count() > 0:
                    return True
            else:
                file_path = str(wizard.format_widgets[this_format]['file_path_edit'].text())
                if file_path:
                    if select_mode == SongFormatSelect.SingleFile and os.path.isfile(file_path):
                        return True
                    elif select_mode == SongFormatSelect.SingleFolder and os.path.isdir(file_path):
                        return True
        return False
