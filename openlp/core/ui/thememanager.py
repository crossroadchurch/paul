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
The Theme Manager manages adding, deleteing and modifying of themes.
"""
import os
import zipfile
import shutil

from xml.etree.ElementTree import ElementTree, XML
from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, RegistryProperties, AppLocation, Settings, OpenLPMixin, RegistryMixin, \
    check_directory_exists, UiStrings, translate, is_win
from openlp.core.lib import FileDialog, ImageSource, OpenLPToolbar, ValidationError, get_text_file_string, build_icon, \
    check_item_selected, create_thumb, validate_thumb
from openlp.core.lib.theme import ThemeXML, BackgroundType
from openlp.core.lib.ui import critical_error_message_box, create_widget_action
from openlp.core.ui import FileRenameForm, ThemeForm
from openlp.core.utils import delete_file, get_locale_key, get_filesystem_encoding


class Ui_ThemeManager(object):
    """
    UI part of the Theme Manager
    """
    def setup_ui(self, widget):
        """
        Define the UI
        :param widget: The screen object the the dialog is to be attached to.
        """
        # start with the layout
        self.layout = QtGui.QVBoxLayout(widget)
        self.layout.setSpacing(0)
        self.layout.setMargin(0)
        self.layout.setObjectName('layout')
        self.toolbar = OpenLPToolbar(widget)
        self.toolbar.setObjectName('toolbar')
        self.toolbar.add_toolbar_action('newTheme',
                                        text=UiStrings().NewTheme, icon=':/themes/theme_new.png',
                                        tooltip=translate('OpenLP.ThemeManager', 'Create a new theme.'),
                                        triggers=self.on_add_theme)
        self.toolbar.add_toolbar_action('editTheme',
                                        text=translate('OpenLP.ThemeManager', 'Edit Theme'),
                                        icon=':/themes/theme_edit.png',
                                        tooltip=translate('OpenLP.ThemeManager', 'Edit a theme.'),
                                        triggers=self.on_edit_theme)
        self.delete_toolbar_action = self.toolbar.add_toolbar_action('delete_theme',
                                                                     text=translate('OpenLP.ThemeManager',
                                                                                    'Delete Theme'),
                                                                     icon=':/general/general_delete.png',
                                                                     tooltip=translate('OpenLP.ThemeManager',
                                                                                       'Delete a theme.'),
                                                                     triggers=self.on_delete_theme)
        self.toolbar.addSeparator()
        self.toolbar.add_toolbar_action('importTheme',
                                        text=translate('OpenLP.ThemeManager', 'Import Theme'),
                                        icon=':/general/general_import.png',
                                        tooltip=translate('OpenLP.ThemeManager', 'Import a theme.'),
                                        triggers=self.on_import_theme)
        self.toolbar.add_toolbar_action('exportTheme',
                                        text=translate('OpenLP.ThemeManager', 'Export Theme'),
                                        icon=':/general/general_export.png',
                                        tooltip=translate('OpenLP.ThemeManager', 'Export a theme.'),
                                        triggers=self.on_export_theme)
        self.layout.addWidget(self.toolbar)
        self.theme_widget = QtGui.QWidgetAction(self.toolbar)
        self.theme_widget.setObjectName('theme_widget')
        # create theme manager list
        self.theme_list_widget = QtGui.QListWidget(widget)
        self.theme_list_widget.setAlternatingRowColors(True)
        self.theme_list_widget.setIconSize(QtCore.QSize(88, 50))
        self.theme_list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.theme_list_widget.setObjectName('theme_list_widget')
        self.layout.addWidget(self.theme_list_widget)
        self.theme_list_widget.customContextMenuRequested.connect(self.context_menu)
        # build the context menu
        self.menu = QtGui.QMenu()
        self.edit_action = create_widget_action(self.menu,
                                                text=translate('OpenLP.ThemeManager', '&Edit Theme'),
                                                icon=':/themes/theme_edit.png', triggers=self.on_edit_theme)
        self.copy_action = create_widget_action(self.menu,
                                                text=translate('OpenLP.ThemeManager', '&Copy Theme'),
                                                icon=':/themes/theme_edit.png', triggers=self.on_copy_theme)
        self.rename_action = create_widget_action(self.menu,
                                                  text=translate('OpenLP.ThemeManager', '&Rename Theme'),
                                                  icon=':/themes/theme_edit.png', triggers=self.on_rename_theme)
        self.delete_action = create_widget_action(self.menu,
                                                  text=translate('OpenLP.ThemeManager', '&Delete Theme'),
                                                  icon=':/general/general_delete.png', triggers=self.on_delete_theme)
        self.menu.addSeparator()
        self.global_action = create_widget_action(self.menu,
                                                  text=translate('OpenLP.ThemeManager', 'Set As &Global Default'),
                                                  icon=':/general/general_export.png',
                                                  triggers=self.change_global_from_screen)
        self.export_action = create_widget_action(self.menu,
                                                  text=translate('OpenLP.ThemeManager', '&Export Theme'),
                                                  icon=':/general/general_export.png', triggers=self.on_export_theme)
        # Signals
        self.theme_list_widget.doubleClicked.connect(self.change_global_from_screen)
        self.theme_list_widget.currentItemChanged.connect(self.check_list_state)


class ThemeManager(OpenLPMixin, RegistryMixin, QtGui.QWidget, Ui_ThemeManager, RegistryProperties):
    """
    Manages the orders of Theme.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(ThemeManager, self).__init__(parent)
        self.settings_section = 'themes'
        # Variables
        self.theme_list = []
        self.old_background_image = None

    def bootstrap_initialise(self):
        """
        process the bootstrap initialise setup request
        """
        self.setup_ui(self)
        self.global_theme = Settings().value(self.settings_section + '/global theme')
        self.build_theme_path()
        self.load_first_time_themes()

    def bootstrap_post_set_up(self):
        """
        process the bootstrap post setup request
        """
        self.theme_form = ThemeForm(self)
        self.theme_form.path = self.path
        self.file_rename_form = FileRenameForm()
        Registry().register_function('theme_update_global', self.change_global_from_tab)
        self.load_themes()

    def build_theme_path(self):
        """
        Set up the theme path variables
        """
        self.path = AppLocation.get_section_data_path(self.settings_section)
        check_directory_exists(self.path)
        self.thumb_path = os.path.join(self.path, 'thumbnails')
        check_directory_exists(self.thumb_path)

    def check_list_state(self, item, field=None):
        """
        If Default theme selected remove delete button.
        Note for some reason a dummy field is required.  Nothing is passed!

        :param field:
        :param item: Service Item to process
        """
        if item is None:
            return
        real_theme_name = item.data(QtCore.Qt.UserRole)
        theme_name = item.text()
        # If default theme restrict actions
        if real_theme_name == theme_name:
            self.delete_toolbar_action.setVisible(True)
        else:
            self.delete_toolbar_action.setVisible(False)

    def context_menu(self, point):
        """
        Build the Right Click Context menu and set state depending on the type of theme.

        :param point: The position of the mouse so the correct item can be found.
        """
        item = self.theme_list_widget.itemAt(point)
        if item is None:
            return
        real_theme_name = item.data(QtCore.Qt.UserRole)
        theme_name = str(item.text())
        visible = real_theme_name == theme_name
        self.delete_action.setVisible(visible)
        self.rename_action.setVisible(visible)
        self.global_action.setVisible(visible)
        self.menu.exec_(self.theme_list_widget.mapToGlobal(point))

    def change_global_from_tab(self):
        """
        Change the global theme when it is changed through the Themes settings tab
        """
        self.global_theme = Settings().value(self.settings_section + '/global theme')
        self.log_debug('change_global_from_tab %s' % self.global_theme)
        for count in range(0, self.theme_list_widget.count()):
            # reset the old name
            item = self.theme_list_widget.item(count)
            old_name = item.text()
            new_name = item.data(QtCore.Qt.UserRole)
            if old_name != new_name:
                self.theme_list_widget.item(count).setText(new_name)
            # Set the new name
            if self.global_theme == new_name:
                name = translate('OpenLP.ThemeManager', '%s (default)') % new_name
                self.theme_list_widget.item(count).setText(name)
                self.delete_toolbar_action.setVisible(item not in self.theme_list_widget.selectedItems())

    def change_global_from_screen(self, index=-1):
        """
        Change the global theme when a theme is double clicked upon in the Theme Manager list.

        :param index:
        """
        selected_row = self.theme_list_widget.currentRow()
        for count in range(0, self.theme_list_widget.count()):
            item = self.theme_list_widget.item(count)
            old_name = item.text()
            # reset the old name
            if old_name != item.data(QtCore.Qt.UserRole):
                self.theme_list_widget.item(count).setText(item.data(QtCore.Qt.UserRole))
            # Set the new name
            if count == selected_row:
                self.global_theme = self.theme_list_widget.item(count).text()
                name = translate('OpenLP.ThemeManager', '%s (default)') % self.global_theme
                self.theme_list_widget.item(count).setText(name)
                Settings().setValue(self.settings_section + '/global theme', self.global_theme)
                Registry().execute('theme_update_global')
                self._push_themes()

    def on_add_theme(self, field=None):
        """
        Loads a new theme with the default settings and then launches the theme editing form for the user to make
        their customisations.
        :param field:
        """
        theme = ThemeXML()
        theme.set_default_header_footer()
        self.theme_form.theme = theme
        self.theme_form.exec_()
        self.load_themes()

    def on_rename_theme(self, field=None):
        """
        Renames an existing theme to a new name
        :param field:
        """
        if self._validate_theme_action(translate('OpenLP.ThemeManager', 'You must select a theme to rename.'),
                                       translate('OpenLP.ThemeManager', 'Rename Confirmation'),
                                       translate('OpenLP.ThemeManager', 'Rename %s theme?'), False, False):
            item = self.theme_list_widget.currentItem()
            old_theme_name = item.data(QtCore.Qt.UserRole)
            self.file_rename_form.file_name_edit.setText(old_theme_name)
            if self.file_rename_form.exec_():
                new_theme_name = self.file_rename_form.file_name_edit.text()
                if old_theme_name == new_theme_name:
                    return
                if self.check_if_theme_exists(new_theme_name):
                    old_theme_data = self.get_theme_data(old_theme_name)
                    self.clone_theme_data(old_theme_data, new_theme_name)
                    self.delete_theme(old_theme_name)
                    for plugin in self.plugin_manager.plugins:
                        if plugin.uses_theme(old_theme_name):
                            plugin.rename_theme(old_theme_name, new_theme_name)
                    self.renderer.update_theme(new_theme_name, old_theme_name)
                    self.load_themes()

    def on_copy_theme(self, field=None):
        """
        Copies an existing theme to a new name
        :param field:
        """
        item = self.theme_list_widget.currentItem()
        old_theme_name = item.data(QtCore.Qt.UserRole)
        self.file_rename_form.file_name_edit.setText(translate('OpenLP.ThemeManager',
                                                     'Copy of %s', 'Copy of <theme name>') % old_theme_name)
        if self.file_rename_form.exec_(True):
            new_theme_name = self.file_rename_form.file_name_edit.text()
            if self.check_if_theme_exists(new_theme_name):
                theme_data = self.get_theme_data(old_theme_name)
                self.clone_theme_data(theme_data, new_theme_name)

    def clone_theme_data(self, theme_data, new_theme_name):
        """
        Takes a theme and makes a new copy of it as well as saving it.

        :param theme_data: The theme to be used
        :param new_theme_name: The new theme name to save the data to
        """
        save_to = None
        save_from = None
        if theme_data.background_type == 'image':
            save_to = os.path.join(self.path, new_theme_name, os.path.split(str(theme_data.background_filename))[1])
            save_from = theme_data.background_filename
        theme_data.theme_name = new_theme_name
        theme_data.extend_image_filename(self.path)
        self.save_theme(theme_data, save_from, save_to)
        self.load_themes()

    def on_edit_theme(self, field=None):
        """
        Loads the settings for the theme that is to be edited and launches the
        theme editing form so the user can make their changes.
        :param field:
        """
        if check_item_selected(self.theme_list_widget,
                               translate('OpenLP.ThemeManager', 'You must select a theme to edit.')):
            item = self.theme_list_widget.currentItem()
            theme = self.get_theme_data(item.data(QtCore.Qt.UserRole))
            if theme.background_type == 'image':
                self.old_background_image = theme.background_filename
            self.theme_form.theme = theme
            self.theme_form.exec_(True)
            self.old_background_image = None
            self.renderer.update_theme(theme.theme_name)
            self.load_themes()

    def on_delete_theme(self, field=None):
        """
        Delete a theme triggered by the UI.
        :param field:
        """
        if self._validate_theme_action(translate('OpenLP.ThemeManager', 'You must select a theme to delete.'),
                                       translate('OpenLP.ThemeManager', 'Delete Confirmation'),
                                       translate('OpenLP.ThemeManager', 'Delete %s theme?')):
            item = self.theme_list_widget.currentItem()
            theme = item.text()
            row = self.theme_list_widget.row(item)
            self.theme_list_widget.takeItem(row)
            self.delete_theme(theme)
            self.renderer.update_theme(theme, only_delete=True)
            # As we do not reload the themes, push out the change. Reload the
            # list as the internal lists and events need to be triggered.
            self._push_themes()

    def delete_theme(self, theme):
        """
        Delete a theme.

        :param theme: The theme to delete.
        """
        self.theme_list.remove(theme)
        thumb = '%s.png' % theme
        delete_file(os.path.join(self.path, thumb))
        delete_file(os.path.join(self.thumb_path, thumb))
        try:
            # Windows is always unicode, so no need to encode filenames
            if is_win():
                shutil.rmtree(os.path.join(self.path, theme))
            else:
                encoding = get_filesystem_encoding()
                shutil.rmtree(os.path.join(self.path, theme).encode(encoding))
        except OSError as os_error:
            shutil.Error = os_error
            self.log_exception('Error deleting theme %s' % theme)

    def on_export_theme(self, field=None):
        """
        Export the theme in a zip file
        :param field:
        """
        item = self.theme_list_widget.currentItem()
        if item is None:
            critical_error_message_box(message=translate('OpenLP.ThemeManager', 'You have not selected a theme.'))
            return
        theme = item.data(QtCore.Qt.UserRole)
        path = QtGui.QFileDialog.getExistingDirectory(self,
                                                      translate('OpenLP.ThemeManager', 'Save Theme - (%s)') % theme,
                                                      Settings().value(self.settings_section +
                                                                       '/last directory export'))
        self.application.set_busy_cursor()
        if path:
            Settings().setValue(self.settings_section + '/last directory export', path)
            if self._export_theme(path, theme):
                QtGui.QMessageBox.information(self,
                                              translate('OpenLP.ThemeManager', 'Theme Exported'),
                                              translate('OpenLP.ThemeManager',
                                                        'Your theme has been successfully exported.'))
        self.application.set_normal_cursor()

    def _export_theme(self, path, theme):
        """
        Create the zipfile with the theme contents.
        :param path: Location where the zip file will be placed
        :param theme: The name of the theme to be exported
        """
        theme_path = os.path.join(path, theme + '.otz')
        theme_zip = None
        try:
            theme_zip = zipfile.ZipFile(theme_path, 'w')
            source = os.path.join(self.path, theme)
            for files in os.walk(source):
                for name in files[2]:
                    theme_zip.write(os.path.join(source, name), os.path.join(theme, name))
            theme_zip.close()
            return True
        except OSError as ose:
            self.log_exception('Export Theme Failed')
            critical_error_message_box(translate('OpenLP.ThemeManager', 'Theme Export Failed'),
                                       translate('OpenLP.ThemeManager', 'The theme export failed because this error '
                                                                        'occurred: %s') % ose.strerror)
            if theme_zip:
                theme_zip.close()
                shutil.rmtree(theme_path, True)
            return False

    def on_import_theme(self, field=None):
        """
        Opens a file dialog to select the theme file(s) to import before attempting to extract OpenLP themes from
        those files. This process will only load version 2 themes.
        :param field:
        """
        files = FileDialog.getOpenFileNames(self,
                                            translate('OpenLP.ThemeManager', 'Select Theme Import File'),
                                            Settings().value(self.settings_section + '/last directory import'),
                                            translate('OpenLP.ThemeManager', 'OpenLP Themes (*.otz)'))
        self.log_info('New Themes %s' % str(files))
        if not files:
            return
        self.application.set_busy_cursor()
        for file_name in files:
            Settings().setValue(self.settings_section + '/last directory import', str(file_name))
            self.unzip_theme(file_name, self.path)
        self.load_themes()
        self.application.set_normal_cursor()

    def load_first_time_themes(self):
        """
        Imports any themes on start up and makes sure there is at least one theme
        """
        self.application.set_busy_cursor()
        files = AppLocation.get_files(self.settings_section, '.otz')
        for theme_file in files:
            theme_file = os.path.join(self.path, theme_file)
            self.unzip_theme(theme_file, self.path)
            delete_file(theme_file)
        files = AppLocation.get_files(self.settings_section, '.png')
        # No themes have been found so create one
        if not files:
            theme = ThemeXML()
            theme.theme_name = UiStrings().Default
            self._write_theme(theme, None, None)
            Settings().setValue(self.settings_section + '/global theme', theme.theme_name)
        self.application.set_normal_cursor()

    def load_themes(self):
        """
        Loads the theme lists and triggers updates across the whole system using direct calls or core functions and
        events for the plugins.
        The plugins will call back in to get the real list if they want it.
        """
        self.theme_list = []
        self.theme_list_widget.clear()
        files = AppLocation.get_files(self.settings_section, '.png')
        # Sort the themes by its name considering language specific
        files.sort(key=lambda file_name: get_locale_key(str(file_name)))
        # now process the file list of png files
        for name in files:
            # check to see file is in theme root directory
            theme = os.path.join(self.path, name)
            if os.path.exists(theme):
                text_name = os.path.splitext(name)[0]
                if text_name == self.global_theme:
                    name = translate('OpenLP.ThemeManager', '%s (default)') % text_name
                else:
                    name = text_name
                thumb = os.path.join(self.thumb_path, '%s.png' % text_name)
                item_name = QtGui.QListWidgetItem(name)
                if validate_thumb(theme, thumb):
                    icon = build_icon(thumb)
                else:
                    icon = create_thumb(theme, thumb)
                item_name.setIcon(icon)
                item_name.setData(QtCore.Qt.UserRole, text_name)
                self.theme_list_widget.addItem(item_name)
                self.theme_list.append(text_name)
        self._push_themes()

    def _push_themes(self):
        """
        Notify listeners that the theme list has been updated
        """
        Registry().execute('theme_update_list', self.get_themes())

    def get_themes(self):
        """
        Return the list of loaded themes
        """
        return self.theme_list

    def get_theme_data(self, theme_name):
        """
        Returns a theme object from an XML file

        :param theme_name: Name of the theme to load from file
        :return The theme object.
        """
        self.log_debug('get theme data for theme %s' % theme_name)
        xml_file = os.path.join(self.path, str(theme_name), str(theme_name) + '.xml')
        xml = get_text_file_string(xml_file)
        if not xml:
            self.log_debug('No theme data - using default theme')
            return ThemeXML()
        else:
            return self._create_theme_from_xml(xml, self.path)

    def over_write_message_box(self, theme_name):
        """
        Display a warning box to the user that a theme already exists

        :param theme_name: Name of the theme.
        :return Confirm if the theme is to be overwritten.
        """
        ret = QtGui.QMessageBox.question(self, translate('OpenLP.ThemeManager', 'Theme Already Exists'),
                                         translate('OpenLP.ThemeManager',
                                                   'Theme %s already exists. Do you want to replace it?')
                                         .replace('%s', theme_name),
                                         QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes |
                                                                           QtGui.QMessageBox.No),
                                         QtGui.QMessageBox.No)
        return ret == QtGui.QMessageBox.Yes

    def unzip_theme(self, file_name, directory):
        """
        Unzip the theme, remove the preview file if stored. Generate a new preview file. Check the XML theme version
        and upgrade if necessary.
        :param file_name:
        :param directory:
        """
        self.log_debug('Unzipping theme %s' % file_name)
        theme_zip = None
        out_file = None
        file_xml = None
        abort_import = True
        try:
            theme_zip = zipfile.ZipFile(file_name)
            xml_file = [name for name in theme_zip.namelist() if os.path.splitext(name)[1].lower() == '.xml']
            if len(xml_file) != 1:
                self.log_error('Theme contains "%s" XML files' % len(xml_file))
                raise ValidationError
            xml_tree = ElementTree(element=XML(theme_zip.read(xml_file[0]))).getroot()
            theme_version = xml_tree.get('version', default=None)
            if not theme_version or float(theme_version) < 2.0:
                self.log_error('Theme version is less than 2.0')
                raise ValidationError
            theme_name = xml_tree.find('name').text.strip()
            theme_folder = os.path.join(directory, theme_name)
            theme_exists = os.path.exists(theme_folder)
            if theme_exists and not self.over_write_message_box(theme_name):
                abort_import = True
                return
            else:
                abort_import = False
            for name in theme_zip.namelist():
                out_name = name.replace('/', os.path.sep)
                split_name = out_name.split(os.path.sep)
                if split_name[-1] == '' or len(split_name) == 1:
                    # is directory or preview file
                    continue
                full_name = os.path.join(directory, out_name)
                check_directory_exists(os.path.dirname(full_name))
                if os.path.splitext(name)[1].lower() == '.xml':
                    file_xml = str(theme_zip.read(name), 'utf-8')
                    out_file = open(full_name, 'w', encoding='utf-8')
                    out_file.write(file_xml)
                else:
                    out_file = open(full_name, 'wb')
                    out_file.write(theme_zip.read(name))
                out_file.close()
        except (IOError, zipfile.BadZipfile):
            self.log_exception('Importing theme from zip failed %s' % file_name)
            raise ValidationError
        except ValidationError:
            critical_error_message_box(translate('OpenLP.ThemeManager', 'Validation Error'),
                                       translate('OpenLP.ThemeManager', 'File is not a valid theme.'))
        finally:
            # Close the files, to be able to continue creating the theme.
            if theme_zip:
                theme_zip.close()
            if out_file:
                out_file.close()
            if not abort_import:
                # As all files are closed, we can create the Theme.
                if file_xml:
                    theme = self._create_theme_from_xml(file_xml, self.path)
                    self.generate_and_save_image(theme_name, theme)
                # Only show the error message, when IOError was not raised (in
                # this case the error message has already been shown).
                elif theme_zip is not None:
                    critical_error_message_box(
                        translate('OpenLP.ThemeManager', 'Validation Error'),
                        translate('OpenLP.ThemeManager', 'File is not a valid theme.'))
                    self.log_error('Theme file does not contain XML data %s' % file_name)

    def check_if_theme_exists(self, theme_name):
        """
        Check if theme already exists and displays error message

        :param theme_name:  Name of the Theme to test
        :return True or False if theme exists
        """
        theme_dir = os.path.join(self.path, theme_name)
        if os.path.exists(theme_dir):
            critical_error_message_box(
                translate('OpenLP.ThemeManager', 'Validation Error'),
                translate('OpenLP.ThemeManager', 'A theme with this name already exists.'))
            return False
        return True

    def save_theme(self, theme, image_from, image_to):
        """
        Called by theme maintenance Dialog to save the theme and to trigger the reload of the theme list

        :param theme: The theme data object.
        :param image_from: Where the theme image is currently located.
        :param image_to: Where the Theme Image is to be saved to
        """
        self._write_theme(theme, image_from, image_to)
        if theme.background_type == BackgroundType.to_string(BackgroundType.Image):
            self.image_manager.update_image_border(theme.background_filename,
                                                   ImageSource.Theme,
                                                   QtGui.QColor(theme.background_border_color))
            self.image_manager.process_updates()

    def _write_theme(self, theme, image_from, image_to):
        """
        Writes the theme to the disk and handles the background image if necessary

        :param theme: The theme data object.
        :param image_from: Where the theme image is currently located.
        :param image_to: Where the Theme Image is to be saved to
        """
        name = theme.theme_name
        theme_pretty_xml = theme.extract_formatted_xml()
        theme_dir = os.path.join(self.path, name)
        check_directory_exists(theme_dir)
        theme_file = os.path.join(theme_dir, name + '.xml')
        if self.old_background_image and image_to != self.old_background_image:
            delete_file(self.old_background_image)
        out_file = None
        try:
            out_file = open(theme_file, 'w', encoding='utf-8')
            out_file.write(theme_pretty_xml.decode('utf-8'))
        except IOError:
            self.log_exception('Saving theme to file failed')
        finally:
            if out_file:
                out_file.close()
        if image_from and os.path.abspath(image_from) != os.path.abspath(image_to):
            try:
                # Windows is always unicode, so no need to encode filenames
                if is_win():
                    shutil.copyfile(image_from, image_to)
                else:
                    encoding = get_filesystem_encoding()
                    shutil.copyfile(image_from.encode(encoding), image_to.encode(encoding))
            except IOError as xxx_todo_changeme:
                shutil.Error = xxx_todo_changeme
                self.log_exception('Failed to save theme image')
        self.generate_and_save_image(name, theme)

    def generate_and_save_image(self, name, theme):
        """
        Generate and save a preview image

        :param name: The name of the theme.
        :param theme: The theme data object.
        """
        frame = self.generate_image(theme)
        sample_path_name = os.path.join(self.path, name + '.png')
        if os.path.exists(sample_path_name):
            os.unlink(sample_path_name)
        frame.save(sample_path_name, 'png')
        thumb = os.path.join(self.thumb_path, '%s.png' % name)
        create_thumb(sample_path_name, thumb, False)

    def update_preview_images(self):
        """
        Called to update the themes' preview images.
        """
        self.main_window.display_progress_bar(len(self.theme_list))
        for theme in self.theme_list:
            self.main_window.increment_progress_bar()
            self.generate_and_save_image(theme, self.get_theme_data(theme))
        self.main_window.finished_progress_bar()
        self.load_themes()

    def generate_image(self, theme_data, force_page=False):
        """
        Call the renderer to build a Sample Image

        :param theme_data: The theme to generated a preview for.
        :param force_page: Flag to tell message lines per page need to be generated.
        """
        return self.renderer.generate_preview(theme_data, force_page)

    def get_preview_image(self, theme):
        """
        Return an image representing the look of the theme

        :param theme: The theme to return the image for.
        """
        return os.path.join(self.path, theme + '.png')

    def _create_theme_from_xml(self, theme_xml, image_path):
        """
        Return a theme object using information parsed from XML

        :param theme_xml: The Theme data object.
        :param image_path: Where the theme image is stored
        :return Theme data.
        """
        theme = ThemeXML()
        theme.parse(theme_xml)
        theme.extend_image_filename(image_path)
        return theme

    def _validate_theme_action(self, select_text, confirm_title, confirm_text, test_plugin=True, confirm=True):
        """
        Check to see if theme has been selected and the destructive action is allowed.

        :param select_text: Text for message box if no item selected.
        :param confirm_title: Confirm message title to be displayed.
        :param confirm_text: Confirm message text to be displayed.
        :param test_plugin: Do we check the plugins for theme usage.
        :param confirm: Do we display a confirm box before run checks.
        :return True or False depending on the validity.
        """
        self.global_theme = Settings().value(self.settings_section + '/global theme')
        if check_item_selected(self.theme_list_widget, select_text):
            item = self.theme_list_widget.currentItem()
            theme = item.text()
            # confirm deletion
            if confirm:
                answer = QtGui.QMessageBox.question(self, confirm_title, confirm_text % theme,
                                                    QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes |
                                                                                      QtGui.QMessageBox.No),
                                                    QtGui.QMessageBox.No)
                if answer == QtGui.QMessageBox.No:
                    return False
            # should be the same unless default
            if theme != item.data(QtCore.Qt.UserRole):
                critical_error_message_box(
                    message=translate('OpenLP.ThemeManager', 'You are unable to delete the default theme.'))
                return False
            # check for use in the system else where.
            if test_plugin:
                for plugin in self.plugin_manager.plugins:
                    if plugin.uses_theme(theme):
                        critical_error_message_box(translate('OpenLP.ThemeManager', 'Validation Error'),
                                                   translate('OpenLP.ThemeManager',
                                                             'Theme %s is used in the %s plugin.')
                                                   % (theme, plugin.name))
                        return False
            return True
        return False
