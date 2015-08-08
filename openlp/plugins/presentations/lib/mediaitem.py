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
import os

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, Settings, UiStrings, translate
from openlp.core.lib import MediaManagerItem, ItemCapabilities, ServiceItemContext,\
    build_icon, check_item_selected, create_thumb, validate_thumb
from openlp.core.lib.ui import critical_error_message_box, create_horizontal_adjusting_combo_box
from openlp.core.utils import get_locale_key
from openlp.plugins.presentations.lib import MessageListener
from openlp.plugins.presentations.lib.pdfcontroller import PDF_CONTROLLER_FILETYPES

log = logging.getLogger(__name__)


ERROR_IMAGE = QtGui.QImage(':/general/general_delete.png')


class PresentationMediaItem(MediaManagerItem):
    """
    This is the Presentation media manager item for Presentation Items. It can present files using Openoffice and
    Powerpoint
    """
    log.info('Presentations Media Item loaded')

    def __init__(self, parent, plugin, controllers):
        """
        Constructor. Setup defaults
        """
        self.icon_path = 'presentations/presentation'
        self.controllers = controllers
        super(PresentationMediaItem, self).__init__(parent, plugin)

    def retranslateUi(self):
        """
        The name of the plugin media displayed in UI
        """
        self.on_new_prompt = translate('PresentationPlugin.MediaItem', 'Select Presentation(s)')
        self.automatic = translate('PresentationPlugin.MediaItem', 'Automatic')
        self.display_type_label.setText(translate('PresentationPlugin.MediaItem', 'Present using:'))

    def setup_item(self):
        """
        Do some additional setup.
        """
        self.message_listener = MessageListener(self)
        self.has_search = True
        self.single_service_item = False
        Registry().register_function('mediaitem_presentation_rebuild', self.populate_display_types)
        Registry().register_function('mediaitem_suffixes', self.build_file_mask_string)
        # Allow DnD from the desktop
        self.list_view.activateDnD()

    def build_file_mask_string(self):
        """
        Build the list of file extensions to be used in the Open file dialog.
        """
        file_type_string = ''
        for controller in self.controllers:
            if self.controllers[controller].enabled():
                file_types = self.controllers[controller].supports + self.controllers[controller].also_supports
                for file_type in file_types:
                    if file_type not in file_type_string:
                        file_type_string += '*.%s ' % file_type
                        self.service_manager.supported_suffixes(file_type)
        self.on_new_file_masks = translate('PresentationPlugin.MediaItem', 'Presentations (%s)') % file_type_string

    def required_icons(self):
        """
        Set which icons the media manager tab should show.
        """
        MediaManagerItem.required_icons(self)
        self.has_file_icon = True
        self.has_new_icon = False
        self.has_edit_icon = False

    def add_end_header_bar(self):
        """
        Display custom media manager items for presentations.
        """
        self.presentation_widget = QtGui.QWidget(self)
        self.presentation_widget.setObjectName('presentation_widget')
        self.display_layout = QtGui.QFormLayout(self.presentation_widget)
        self.display_layout.setMargin(self.display_layout.spacing())
        self.display_layout.setObjectName('display_layout')
        self.display_type_label = QtGui.QLabel(self.presentation_widget)
        self.display_type_label.setObjectName('display_type_label')
        self.display_type_combo_box = create_horizontal_adjusting_combo_box(self.presentation_widget,
                                                                            'display_type_combo_box')
        self.display_type_label.setBuddy(self.display_type_combo_box)
        self.display_layout.addRow(self.display_type_label, self.display_type_combo_box)
        # Add the Presentation widget to the page layout.
        self.page_layout.addWidget(self.presentation_widget)

    def initialise(self):
        """
        Populate the media manager tab
        """
        self.list_view.setIconSize(QtCore.QSize(88, 50))
        files = Settings().value(self.settings_section + '/presentations files')
        self.load_list(files, initial_load=True)
        self.populate_display_types()

    def populate_display_types(self):
        """
        Load the combobox with the enabled presentation controllers, allowing user to select a specific app if settings
        allow.
        """
        self.display_type_combo_box.clear()
        for item in self.controllers:
            # For PDF reload backend, since it can have changed
            if self.controllers[item].name == 'Pdf':
                self.controllers[item].check_available()
            # load the drop down selection
            if self.controllers[item].enabled():
                self.display_type_combo_box.addItem(item)
        if self.display_type_combo_box.count() > 1:
            self.display_type_combo_box.insertItem(0, self.automatic, userData='automatic')
            self.display_type_combo_box.setCurrentIndex(0)
        if Settings().value(self.settings_section + '/override app') == QtCore.Qt.Checked:
            self.presentation_widget.show()
        else:
            self.presentation_widget.hide()

    def load_list(self, files, target_group=None, initial_load=False):
        """
        Add presentations into the media manager. This is called both on initial load of the plugin to populate with
        existing files, and when the user adds new files via the media manager.
        """
        current_list = self.get_file_list()
        titles = [os.path.split(file)[1] for file in current_list]
        self.application.set_busy_cursor()
        if not initial_load:
            self.main_window.display_progress_bar(len(files))
        # Sort the presentations by its filename considering language specific characters.
        files.sort(key=lambda filename: get_locale_key(os.path.split(str(filename))[1]))
        for file in files:
            if not initial_load:
                self.main_window.increment_progress_bar()
            if current_list.count(file) > 0:
                continue
            filename = os.path.split(file)[1]
            if not os.path.exists(file):
                item_name = QtGui.QListWidgetItem(filename)
                item_name.setIcon(build_icon(ERROR_IMAGE))
                item_name.setData(QtCore.Qt.UserRole, file)
                item_name.setToolTip(file)
                self.list_view.addItem(item_name)
            else:
                if titles.count(filename) > 0:
                    if not initial_load:
                        critical_error_message_box(translate('PresentationPlugin.MediaItem', 'File Exists'),
                                                   translate('PresentationPlugin.MediaItem',
                                                             'A presentation with that filename already exists.'))
                    continue
                controller_name = self.find_controller_by_type(filename)
                if controller_name:
                    controller = self.controllers[controller_name]
                    doc = controller.add_document(file)
                    thumb = os.path.join(doc.get_thumbnail_folder(), 'icon.png')
                    preview = doc.get_thumbnail_path(1, True)
                    if not preview and not initial_load:
                        doc.load_presentation()
                        preview = doc.get_thumbnail_path(1, True)
                    doc.close_presentation()
                    if not (preview and os.path.exists(preview)):
                        icon = build_icon(':/general/general_delete.png')
                    else:
                        if validate_thumb(preview, thumb):
                            icon = build_icon(thumb)
                        else:
                            icon = create_thumb(preview, thumb)
                else:
                    if initial_load:
                        icon = build_icon(':/general/general_delete.png')
                    else:
                        critical_error_message_box(UiStrings().UnsupportedFile,
                                                   translate('PresentationPlugin.MediaItem',
                                                             'This type of presentation is not supported.'))
                        continue
                item_name = QtGui.QListWidgetItem(filename)
                item_name.setData(QtCore.Qt.UserRole, file)
                item_name.setIcon(icon)
                item_name.setToolTip(file)
                self.list_view.addItem(item_name)
        if not initial_load:
            self.main_window.finished_progress_bar()
        self.application.set_normal_cursor()

    def on_delete_click(self):
        """
        Remove a presentation item from the list.
        """
        if check_item_selected(self.list_view, UiStrings().SelectDelete):
            items = self.list_view.selectedIndexes()
            row_list = [item.row() for item in items]
            row_list.sort(reverse=True)
            self.application.set_busy_cursor()
            self.main_window.display_progress_bar(len(row_list))
            for item in items:
                filepath = str(item.data(QtCore.Qt.UserRole))
                self.clean_up_thumbnails(filepath)
                self.main_window.increment_progress_bar()
            self.main_window.finished_progress_bar()
            for row in row_list:
                self.list_view.takeItem(row)
            Settings().setValue(self.settings_section + '/presentations files', self.get_file_list())
            self.application.set_normal_cursor()

    def clean_up_thumbnails(self, filepath, clean_for_update=False):
        """
        Clean up the files created such as thumbnails

        :param filepath: File path of the presention to clean up after
        :param clean_for_update: Only clean thumbnails if update is needed
        :return: None
        """
        for cidx in self.controllers:
            root, file_ext = os.path.splitext(filepath)
            file_ext = file_ext[1:]
            if file_ext in self.controllers[cidx].supports or file_ext in self.controllers[cidx].also_supports:
                doc = self.controllers[cidx].add_document(filepath)
                if clean_for_update:
                    thumb_path = doc.get_thumbnail_path(1, True)
                    if not thumb_path or not os.path.exists(filepath) or os.path.getmtime(
                            thumb_path) < os.path.getmtime(filepath):
                        doc.presentation_deleted()
                else:
                    doc.presentation_deleted()
                doc.close_presentation()

    def generate_slide_data(self, service_item, item=None, xml_version=False, remote=False,
                            context=ServiceItemContext.Service, presentation_file=None):
        """
        Generate the slide data. Needs to be implemented by the plugin.

        :param service_item: The service item to be built on
        :param item: The Song item to be used
        :param xml_version: The xml version (not used)
        :param remote: Triggered from remote
        :param context: Why is it being generated
        """
        if item:
            items = [item]
        else:
            items = self.list_view.selectedItems()
            if len(items) > 1:
                return False
        filename = presentation_file
        if filename is None:
            filename = items[0].data(QtCore.Qt.UserRole)
        file_type = os.path.splitext(filename.lower())[1][1:]
        if not self.display_type_combo_box.currentText():
            return False
        service_item.add_capability(ItemCapabilities.CanEditTitle)
        if file_type in PDF_CONTROLLER_FILETYPES and context != ServiceItemContext.Service:
            service_item.add_capability(ItemCapabilities.CanMaintain)
            service_item.add_capability(ItemCapabilities.CanPreview)
            service_item.add_capability(ItemCapabilities.CanLoop)
            service_item.add_capability(ItemCapabilities.CanAppend)
            service_item.name = 'images'
            # force a nonexistent theme
            service_item.theme = -1
            for bitem in items:
                filename = presentation_file
                if filename is None:
                    filename = bitem.data(QtCore.Qt.UserRole)
                (path, name) = os.path.split(filename)
                service_item.title = name
                if os.path.exists(filename):
                    processor = self.find_controller_by_type(filename)
                    if not processor:
                        return False
                    controller = self.controllers[processor]
                    service_item.processor = None
                    doc = controller.add_document(filename)
                    if doc.get_thumbnail_path(1, True) is None or not os.path.isfile(
                            os.path.join(doc.get_temp_folder(), 'mainslide001.png')):
                        doc.load_presentation()
                    i = 1
                    image = os.path.join(doc.get_temp_folder(), 'mainslide%03d.png' % i)
                    thumbnail = os.path.join(doc.get_thumbnail_folder(), 'slide%d.png' % i)
                    while os.path.isfile(image):
                        service_item.add_from_image(image, name, thumbnail=thumbnail)
                        i += 1
                        image = os.path.join(doc.get_temp_folder(), 'mainslide%03d.png' % i)
                        thumbnail = os.path.join(doc.get_thumbnail_folder(), 'slide%d.png' % i)
                    service_item.add_capability(ItemCapabilities.HasThumbnails)
                    doc.close_presentation()
                    return True
                else:
                    # File is no longer present
                    if not remote:
                        critical_error_message_box(translate('PresentationPlugin.MediaItem', 'Missing Presentation'),
                                                   translate('PresentationPlugin.MediaItem',
                                                             'The presentation %s no longer exists.') % filename)
                    return False
        else:
            service_item.processor = self.display_type_combo_box.currentText()
            service_item.add_capability(ItemCapabilities.ProvidesOwnDisplay)
            for bitem in items:
                filename = bitem.data(QtCore.Qt.UserRole)
                (path, name) = os.path.split(filename)
                service_item.title = name
                if os.path.exists(filename):
                    if self.display_type_combo_box.itemData(self.display_type_combo_box.currentIndex()) == 'automatic':
                        service_item.processor = self.find_controller_by_type(filename)
                        if not service_item.processor:
                            return False
                    controller = self.controllers[service_item.processor]
                    doc = controller.add_document(filename)
                    if doc.get_thumbnail_path(1, True) is None:
                        doc.load_presentation()
                    i = 1
                    img = doc.get_thumbnail_path(i, True)
                    if img:
                        # Get titles and notes
                        titles, notes = doc.get_titles_and_notes()
                        service_item.add_capability(ItemCapabilities.HasDisplayTitle)
                        if notes.count('') != len(notes):
                            service_item.add_capability(ItemCapabilities.HasNotes)
                        service_item.add_capability(ItemCapabilities.HasThumbnails)
                        while img:
                            # Use title and note if available
                            title = ''
                            if titles and len(titles) >= i:
                                title = titles[i - 1]
                            note = ''
                            if notes and len(notes) >= i:
                                note = notes[i - 1]
                            service_item.add_from_command(path, name, img, title, note)
                            i += 1
                            img = doc.get_thumbnail_path(i, True)
                        doc.close_presentation()
                        return True
                    else:
                        # File is no longer present
                        if not remote:
                            critical_error_message_box(translate('PresentationPlugin.MediaItem',
                                                                 'Missing Presentation'),
                                                       translate('PresentationPlugin.MediaItem',
                                                                 'The presentation %s is incomplete, please reload.')
                                                       % filename)
                        return False
                else:
                    # File is no longer present
                    if not remote:
                        critical_error_message_box(translate('PresentationPlugin.MediaItem', 'Missing Presentation'),
                                                   translate('PresentationPlugin.MediaItem',
                                                             'The presentation %s no longer exists.') % filename)
                    return False

    def find_controller_by_type(self, filename):
        """
        Determine the default application controller to use for the selected file type. This is used if "Automatic" is
        set as the preferred controller. Find the first (alphabetic) enabled controller which "supports" the extension.
        If none found, then look for a controller which "also supports" it instead.

        :param filename: The file name
        """
        file_type = os.path.splitext(filename)[1][1:]
        if not file_type:
            return None
        for controller in self.controllers:
            if self.controllers[controller].enabled():
                if file_type in self.controllers[controller].supports:
                    return controller
        for controller in self.controllers:
            if self.controllers[controller].enabled():
                if file_type in self.controllers[controller].also_supports:
                    return controller
        return None

    def search(self, string, show_error):
        """
        Search in files

        :param string: name to be found
        :param show_error: not used
        :return:
        """
        files = Settings().value(self.settings_section + '/presentations files')
        results = []
        string = string.lower()
        for file in files:
            filename = os.path.split(str(file))[1]
            if filename.lower().find(string) > -1:
                results.append([file, filename])
        return results
