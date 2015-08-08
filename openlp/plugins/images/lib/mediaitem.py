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

from openlp.core.common import Registry, AppLocation, Settings, UiStrings, check_directory_exists, translate
from openlp.core.lib import ItemCapabilities, MediaManagerItem, ServiceItemContext, StringContent, TreeWidgetWithDnD,\
    build_icon, check_item_selected, create_thumb, validate_thumb
from openlp.core.lib.ui import create_widget_action, critical_error_message_box
from openlp.core.utils import delete_file, get_locale_key, get_images_filter
from openlp.plugins.images.forms import AddGroupForm, ChooseGroupForm
from openlp.plugins.images.lib.db import ImageFilenames, ImageGroups


log = logging.getLogger(__name__)


class ImageMediaItem(MediaManagerItem):
    """
    This is the custom media manager item for images.
    """
    log.info('Image Media Item loaded')

    def __init__(self, parent, plugin):
        self.icon_path = 'images/image'
        self.manager = None
        self.choose_group_form = None
        self.add_group_form = None
        super(ImageMediaItem, self).__init__(parent, plugin)

    def setup_item(self):
        """
        Do some additional setup.
        """
        self.quick_preview_allowed = True
        self.has_search = True
        self.manager = self.plugin.manager
        self.choose_group_form = ChooseGroupForm(self)
        self.add_group_form = AddGroupForm(self)
        self.fill_groups_combobox(self.choose_group_form.group_combobox)
        self.fill_groups_combobox(self.add_group_form.parent_group_combobox)
        Registry().register_function('live_theme_changed', self.live_theme_changed)
        # Allow DnD from the desktop.
        self.list_view.activateDnD()

    def retranslateUi(self):
        self.on_new_prompt = translate('ImagePlugin.MediaItem', 'Select Image(s)')
        file_formats = get_images_filter()
        self.on_new_file_masks = '%s;;%s (*)' % (file_formats, UiStrings().AllFiles)
        self.add_group_action.setText(UiStrings().AddGroup)
        self.add_group_action.setToolTip(UiStrings().AddGroup)
        self.replace_action.setText(UiStrings().ReplaceBG)
        self.replace_action.setToolTip(UiStrings().ReplaceLiveBG)
        self.reset_action.setText(UiStrings().ResetBG)
        self.reset_action.setToolTip(UiStrings().ResetLiveBG)

    def required_icons(self):
        """
        Set which icons the media manager tab should show.
        """
        MediaManagerItem.required_icons(self)
        self.has_file_icon = True
        self.has_new_icon = False
        self.has_edit_icon = False
        self.add_to_service_item = True

    def initialise(self):
        log.debug('initialise')
        self.list_view.clear()
        self.list_view.setIconSize(QtCore.QSize(88, 50))
        self.list_view.setIndentation(self.list_view.default_indentation)
        self.list_view.allow_internal_dnd = True
        self.service_path = os.path.join(AppLocation.get_section_data_path(self.settings_section), 'thumbnails')
        check_directory_exists(self.service_path)
        # Load images from the database
        self.load_full_list(
            self.manager.get_all_objects(ImageFilenames, order_by_ref=ImageFilenames.filename), initial_load=True)

    def add_list_view_to_toolbar(self):
        """
        Creates the main widget for listing items the media item is tracking. This method overloads
        MediaManagerItem.add_list_view_to_toolbar.
        """
        # Add the List widget
        self.list_view = TreeWidgetWithDnD(self, self.plugin.name)
        self.list_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setObjectName('%sTreeView' % self.plugin.name)
        # Add to pageLayout
        self.page_layout.addWidget(self.list_view)
        # define and add the context menu
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        if self.has_edit_icon:
            create_widget_action(
                self.list_view,
                text=self.plugin.get_string(StringContent.Edit)['title'],
                icon=':/general/general_edit.png',
                triggers=self.on_edit_click)
            create_widget_action(self.list_view, separator=True)
        if self.has_delete_icon:
            create_widget_action(
                self.list_view,
                'listView%s%sItem' % (self.plugin.name.title(), StringContent.Delete.title()),
                text=self.plugin.get_string(StringContent.Delete)['title'],
                icon=':/general/general_delete.png',
                can_shortcuts=True, triggers=self.on_delete_click)
            create_widget_action(self.list_view, separator=True)
        create_widget_action(
            self.list_view,
            'listView%s%sItem' % (self.plugin.name.title(), StringContent.Preview.title()),
            text=self.plugin.get_string(StringContent.Preview)['title'],
            icon=':/general/general_preview.png',
            can_shortcuts=True,
            triggers=self.on_preview_click)
        create_widget_action(
            self.list_view,
            'listView%s%sItem' % (self.plugin.name.title(), StringContent.Live.title()),
            text=self.plugin.get_string(StringContent.Live)['title'],
            icon=':/general/general_live.png',
            can_shortcuts=True,
            triggers=self.on_live_click)
        create_widget_action(
            self.list_view,
            'listView%s%sItem' % (self.plugin.name.title(), StringContent.Service.title()),
            can_shortcuts=True,
            text=self.plugin.get_string(StringContent.Service)['title'],
            icon=':/general/general_add.png',
            triggers=self.on_add_click)
        if self.add_to_service_item:
            create_widget_action(self.list_view, separator=True)
            create_widget_action(
                self.list_view,
                text=translate('OpenLP.MediaManagerItem', '&Add to selected Service Item'),
                icon=':/general/general_add.png',
                triggers=self.on_add_edit_click)
        self.add_custom_context_actions()
        # Create the context menu and add all actions from the list_view.
        self.menu = QtGui.QMenu()
        self.menu.addActions(self.list_view.actions())
        self.list_view.doubleClicked.connect(self.on_double_clicked)
        self.list_view.itemSelectionChanged.connect(self.on_selection_change)
        self.list_view.customContextMenuRequested.connect(self.context_menu)
        self.list_view.addAction(self.replace_action)

    def add_custom_context_actions(self):
        """
        Add custom actions to the context menu.
        """
        create_widget_action(self.list_view, separator=True)
        create_widget_action(
            self.list_view,
            text=UiStrings().AddGroup, icon=':/images/image_new_group.png', triggers=self.on_add_group_click)
        create_widget_action(
            self.list_view,
            text=self.plugin.get_string(StringContent.Load)['tooltip'],
            icon=':/general/general_open.png', triggers=self.on_file_click)

    def add_start_header_bar(self):
        """
        Add custom buttons to the start of the toolbar.
        """
        self.add_group_action = self.toolbar.add_toolbar_action('add_group_action',
                                                                icon=':/images/image_new_group.png',
                                                                triggers=self.on_add_group_click)

    def add_end_header_bar(self):
        """
        Add custom buttons to the end of the toolbar
        """
        self.replace_action = self.toolbar.add_toolbar_action('replace_action',
                                                              icon=':/slides/slide_blank.png',
                                                              triggers=self.on_replace_click)
        self.reset_action = self.toolbar.add_toolbar_action('reset_action',
                                                            icon=':/system/system_close.png',
                                                            visible=False, triggers=self.on_reset_click)

    def recursively_delete_group(self, image_group):
        """
        Recursively deletes a group and all groups and images in it.

        :param image_group: The ImageGroups instance of the group that will be deleted.
        """
        images = self.manager.get_all_objects(ImageFilenames, ImageFilenames.group_id == image_group.id)
        for image in images:
            delete_file(os.path.join(self.service_path, os.path.split(image.filename)[1]))
            delete_file(self.generate_thumbnail_path(image))
            self.manager.delete_object(ImageFilenames, image.id)
        image_groups = self.manager.get_all_objects(ImageGroups, ImageGroups.parent_id == image_group.id)
        for group in image_groups:
            self.recursively_delete_group(group)
            self.manager.delete_object(ImageGroups, group.id)

    def on_delete_click(self):
        """
        Remove an image item from the list.
        """
        # Turn off auto preview triggers.
        self.list_view.blockSignals(True)
        if check_item_selected(self.list_view, translate('ImagePlugin.MediaItem',
                                                         'You must select an image or group to delete.')):
            item_list = self.list_view.selectedItems()
            self.application.set_busy_cursor()
            self.main_window.display_progress_bar(len(item_list))
            for row_item in item_list:
                if row_item:
                    item_data = row_item.data(0, QtCore.Qt.UserRole)
                    if isinstance(item_data, ImageFilenames):
                        delete_file(os.path.join(self.service_path, row_item.text(0)))
                        delete_file(self.generate_thumbnail_path(item_data))
                        if item_data.group_id == 0:
                            self.list_view.takeTopLevelItem(self.list_view.indexOfTopLevelItem(row_item))
                        else:
                            row_item.parent().removeChild(row_item)
                        self.manager.delete_object(ImageFilenames, row_item.data(0, QtCore.Qt.UserRole).id)
                    elif isinstance(item_data, ImageGroups):
                        if QtGui.QMessageBox.question(
                                self.list_view.parent(),
                                translate('ImagePlugin.MediaItem', 'Remove group'),
                                translate('ImagePlugin.MediaItem',
                                          'Are you sure you want to remove "%s" and everything in it?') %
                                item_data.group_name,
                                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes |
                                                                  QtGui.QMessageBox.No)) == QtGui.QMessageBox.Yes:
                            self.recursively_delete_group(item_data)
                            self.manager.delete_object(ImageGroups, row_item.data(0, QtCore.Qt.UserRole).id)
                            if item_data.parent_id == 0:
                                self.list_view.takeTopLevelItem(self.list_view.indexOfTopLevelItem(row_item))
                            else:
                                row_item.parent().removeChild(row_item)
                            self.fill_groups_combobox(self.choose_group_form.group_combobox)
                            self.fill_groups_combobox(self.add_group_form.parent_group_combobox)
                self.main_window.increment_progress_bar()
            self.main_window.finished_progress_bar()
            self.application.set_normal_cursor()
        self.list_view.blockSignals(False)

    def add_sub_groups(self, group_list, parent_group_id):
        """
        Recursively add subgroups to the given parent group in a QTreeWidget.

        :param group_list: The List object that contains all QTreeWidgetItems.
        :param parent_group_id: The ID of the group that will be added recursively.
        """
        image_groups = self.manager.get_all_objects(ImageGroups, ImageGroups.parent_id == parent_group_id)
        image_groups.sort(key=lambda group_object: get_locale_key(group_object.group_name))
        folder_icon = build_icon(':/images/image_group.png')
        for image_group in image_groups:
            group = QtGui.QTreeWidgetItem()
            group.setText(0, image_group.group_name)
            group.setData(0, QtCore.Qt.UserRole, image_group)
            group.setIcon(0, folder_icon)
            if parent_group_id == 0:
                self.list_view.addTopLevelItem(group)
            else:
                group_list[parent_group_id].addChild(group)
            group_list[image_group.id] = group
            self.add_sub_groups(group_list, image_group.id)

    def fill_groups_combobox(self, combobox, parent_group_id=0, prefix=''):
        """
        Recursively add groups to the combobox in the 'Add group' dialog.

        :param combobox: The QComboBox to add the options to.
        :param parent_group_id: The ID of the group that will be added.
        :param prefix: A string containing the prefix that will be added in front of the groupname for each level of
        the tree.
        """
        if parent_group_id == 0:
            combobox.clear()
            combobox.top_level_group_added = False
        image_groups = self.manager.get_all_objects(ImageGroups, ImageGroups.parent_id == parent_group_id)
        image_groups.sort(key=lambda group_object: get_locale_key(group_object.group_name))
        for image_group in image_groups:
            combobox.addItem(prefix + image_group.group_name, image_group.id)
            self.fill_groups_combobox(combobox, image_group.id, prefix + '   ')

    def expand_group(self, group_id, root_item=None):
        """
        Expand groups in the widget recursively.

        :param group_id: The ID of the group that will be expanded.
        :param root_item: This option is only used for recursion purposes.
        """
        return_value = False
        if root_item is None:
            root_item = self.list_view.invisibleRootItem()
        for i in range(root_item.childCount()):
            child = root_item.child(i)
            if self.expand_group(group_id, child):
                child.setExpanded(True)
                return_value = True
        if isinstance(root_item.data(0, QtCore.Qt.UserRole), ImageGroups):
            if root_item.data(0, QtCore.Qt.UserRole).id == group_id:
                return True
        return return_value

    def generate_thumbnail_path(self, image):
        """
        Generate a path to the thumbnail

        :param image: An instance of ImageFileNames
        :return: A path to the thumbnail of type str
        """
        ext = os.path.splitext(image.filename)[1].lower()
        return os.path.join(self.service_path, '{}{}'.format(str(image.id), ext))

    def load_full_list(self, images, initial_load=False, open_group=None):
        """
        Replace the list of images and groups in the interface.

        :param images: A List of Image Filenames objects that will be used to reload the mediamanager list.
        :param initial_load: When set to False, the busy cursor and progressbar will be shown while loading images.
        :param open_group: ImageGroups object of the group that must be expanded after reloading the list in the
        interface.
        """
        if not initial_load:
            self.application.set_busy_cursor()
            self.main_window.display_progress_bar(len(images))
        self.list_view.clear()
        # Load the list of groups and add them to the treeView.
        group_items = {}
        self.add_sub_groups(group_items, parent_group_id=0)
        if open_group is not None:
            self.expand_group(open_group.id)
        # Sort the images by its filename considering language specific.
        # characters.
        images.sort(key=lambda image_object: get_locale_key(os.path.split(str(image_object.filename))[1]))
        for image_file in images:
            log.debug('Loading image: %s', image_file.filename)
            filename = os.path.split(image_file.filename)[1]
            thumb = self.generate_thumbnail_path(image_file)
            if not os.path.exists(image_file.filename):
                icon = build_icon(':/general/general_delete.png')
            else:
                if validate_thumb(image_file.filename, thumb):
                    icon = build_icon(thumb)
                else:
                    icon = create_thumb(image_file.filename, thumb)
            item_name = QtGui.QTreeWidgetItem([filename])
            item_name.setText(0, filename)
            item_name.setIcon(0, icon)
            item_name.setToolTip(0, image_file.filename)
            item_name.setData(0, QtCore.Qt.UserRole, image_file)
            if image_file.group_id == 0:
                self.list_view.addTopLevelItem(item_name)
            else:
                group_items[image_file.group_id].addChild(item_name)
            if not initial_load:
                self.main_window.increment_progress_bar()
        if not initial_load:
            self.main_window.finished_progress_bar()
        self.application.set_normal_cursor()

    def validate_and_load(self, files, target_group=None):
        """
        Process a list for files either from the File Dialog or from Drag and Drop.
        This method is overloaded from MediaManagerItem.

        :param files: A List of strings containing the filenames of the files to be loaded
        :param target_group: The QTreeWidgetItem of the group that will be the parent of the added files
        """
        self.application.set_normal_cursor()
        self.load_list(files, target_group)
        last_dir = os.path.split(files[0])[0]
        Settings().setValue(self.settings_section + '/last directory', last_dir)

    def load_list(self, images, target_group=None, initial_load=False):
        """
        Add new images to the database. This method is called when adding images using the Add button or DnD.

        :param images: A List of strings containing the filenames of the files to be loaded
        :param target_group: The QTreeWidgetItem of the group that will be the parent of the added files
        :param initial_load: When set to False, the busy cursor and progressbar will be shown while loading images
        """
        parent_group = None
        if target_group is None:
            # Find out if a group must be pre-selected
            preselect_group = None
            selected_items = self.list_view.selectedItems()
            if selected_items:
                selected_item = selected_items[0]
                if isinstance(selected_item.data(0, QtCore.Qt.UserRole), ImageFilenames):
                    selected_item = selected_item.parent()
                if isinstance(selected_item, QtGui.QTreeWidgetItem):
                    if isinstance(selected_item.data(0, QtCore.Qt.UserRole), ImageGroups):
                        preselect_group = selected_item.data(0, QtCore.Qt.UserRole).id
            # Enable and disable parts of the 'choose group' form
            if preselect_group is None:
                self.choose_group_form.nogroup_radio_button.setChecked(True)
                self.choose_group_form.nogroup_radio_button.setFocus()
                self.choose_group_form.existing_radio_button.setChecked(False)
                self.choose_group_form.new_radio_button.setChecked(False)
            else:
                self.choose_group_form.nogroup_radio_button.setChecked(False)
                self.choose_group_form.existing_radio_button.setChecked(True)
                self.choose_group_form.new_radio_button.setChecked(False)
                self.choose_group_form.group_combobox.setFocus()
            if self.manager.get_object_count(ImageGroups) == 0:
                self.choose_group_form.existing_radio_button.setDisabled(True)
                self.choose_group_form.group_combobox.setDisabled(True)
            else:
                self.choose_group_form.existing_radio_button.setDisabled(False)
                self.choose_group_form.group_combobox.setDisabled(False)
            # Ask which group the images should be saved in
            if self.choose_group_form.exec_(selected_group=preselect_group):
                if self.choose_group_form.nogroup_radio_button.isChecked():
                    # User chose 'No group'
                    parent_group = ImageGroups()
                    parent_group.id = 0
                elif self.choose_group_form.existing_radio_button.isChecked():
                    # User chose 'Existing group'
                    group_id = self.choose_group_form.group_combobox.itemData(
                        self.choose_group_form.group_combobox.currentIndex(), QtCore.Qt.UserRole)
                    parent_group = self.manager.get_object_filtered(ImageGroups, ImageGroups.id == group_id)
                elif self.choose_group_form.new_radio_button.isChecked():
                    # User chose 'New group'
                    parent_group = ImageGroups()
                    parent_group.parent_id = 0
                    parent_group.group_name = self.choose_group_form.new_group_edit.text()
                    self.manager.save_object(parent_group)
                    self.fill_groups_combobox(self.choose_group_form.group_combobox)
                    self.fill_groups_combobox(self.add_group_form.parent_group_combobox)
        else:
            parent_group = target_group.data(0, QtCore.Qt.UserRole)
            if isinstance(parent_group, ImageFilenames):
                if parent_group.group_id == 0:
                    parent_group = ImageGroups()
                    parent_group.id = 0
                else:
                    parent_group = target_group.parent().data(0, QtCore.Qt.UserRole)
        # If no valid parent group is found, do nothing
        if not isinstance(parent_group, ImageGroups):
            return
        # Initialize busy cursor and progress bar
        self.application.set_busy_cursor()
        self.main_window.display_progress_bar(len(images))
        # Save the new images in the database
        self.save_new_images_list(images, group_id=parent_group.id, reload_list=False)
        self.load_full_list(self.manager.get_all_objects(ImageFilenames, order_by_ref=ImageFilenames.filename),
                            initial_load=initial_load, open_group=parent_group)
        self.application.set_normal_cursor()

    def save_new_images_list(self, images_list, group_id=0, reload_list=True):
        """
        Convert a list of image filenames to ImageFilenames objects and save them in the database.

        :param images_list: A List of strings containing image filenames
        :param group_id: The ID of the group to save the images in
        :param reload_list: This boolean is set to True when the list in the interface should be reloaded after saving
        the new images
        """
        for filename in images_list:
            if not isinstance(filename, str):
                continue
            log.debug('Adding new image: %s', filename)
            image_file = ImageFilenames()
            image_file.group_id = group_id
            image_file.filename = str(filename)
            self.manager.save_object(image_file)
            self.main_window.increment_progress_bar()
        if reload_list and images_list:
            self.load_full_list(self.manager.get_all_objects(ImageFilenames, order_by_ref=ImageFilenames.filename))

    def dnd_move_internal(self, target):
        """
        Handle drag-and-drop moving of images within the media manager

        :param target: This contains the QTreeWidget that is the target of the DnD action
        """
        items_to_move = self.list_view.selectedItems()
        # Determine group to move images to
        target_group = target
        if target_group is not None and isinstance(target_group.data(0, QtCore.Qt.UserRole), ImageFilenames):
            target_group = target.parent()
        # Move to toplevel
        if target_group is None:
            target_group = self.list_view.invisibleRootItem()
            target_group.setData(0, QtCore.Qt.UserRole, ImageGroups())
            target_group.data(0, QtCore.Qt.UserRole).id = 0
        # Move images in the treeview
        items_to_save = []
        for item in items_to_move:
            if isinstance(item.data(0, QtCore.Qt.UserRole), ImageFilenames):
                if isinstance(item.parent(), QtGui.QTreeWidgetItem):
                    item.parent().removeChild(item)
                else:
                    self.list_view.invisibleRootItem().removeChild(item)
                target_group.addChild(item)
                item.setSelected(True)
                item_data = item.data(0, QtCore.Qt.UserRole)
                item_data.group_id = target_group.data(0, QtCore.Qt.UserRole).id
                items_to_save.append(item_data)
        target_group.setExpanded(True)
        # Update the group ID's of the images in the database
        self.manager.save_objects(items_to_save)
        # Sort the target group
        group_items = []
        image_items = []
        for item in target_group.takeChildren():
            if isinstance(item.data(0, QtCore.Qt.UserRole), ImageGroups):
                group_items.append(item)
            if isinstance(item.data(0, QtCore.Qt.UserRole), ImageFilenames):
                image_items.append(item)
        group_items.sort(key=lambda item: get_locale_key(item.text(0)))
        target_group.addChildren(group_items)
        image_items.sort(key=lambda item: get_locale_key(item.text(0)))
        target_group.addChildren(image_items)

    def generate_slide_data(self, service_item, item=None, xml_version=False, remote=False,
                            context=ServiceItemContext.Service):
        """
        Generate the slide data. Needs to be implemented by the plugin.

        :param service_item: The service item to be built on
        :param item: The Song item to be used
        :param xml_version: The xml version (not used)
        :param remote: Triggered from remote
        :param context: Why is it being generated
        """
        background = QtGui.QColor(Settings().value(self.settings_section + '/background color'))
        if item:
            items = [item]
        else:
            items = self.list_view.selectedItems()
            if not items:
                return False
        # Determine service item title
        if isinstance(items[0].data(0, QtCore.Qt.UserRole), ImageGroups) or len(items) == 1:
            service_item.title = items[0].text(0)
        else:
            service_item.title = str(self.plugin.name_strings['plural'])

        service_item.add_capability(ItemCapabilities.CanMaintain)
        service_item.add_capability(ItemCapabilities.CanPreview)
        service_item.add_capability(ItemCapabilities.CanLoop)
        service_item.add_capability(ItemCapabilities.CanAppend)
        service_item.add_capability(ItemCapabilities.CanEditTitle)
        service_item.add_capability(ItemCapabilities.HasThumbnails)
        # force a nonexistent theme
        service_item.theme = -1
        missing_items_file_names = []
        images = []
        # Expand groups to images
        for bitem in items:
            if isinstance(bitem.data(0, QtCore.Qt.UserRole), ImageGroups) or bitem.data(0, QtCore.Qt.UserRole) is None:
                for index in range(0, bitem.childCount()):
                    if isinstance(bitem.child(index).data(0, QtCore.Qt.UserRole), ImageFilenames):
                        images.append(bitem.child(index).data(0, QtCore.Qt.UserRole))
            elif isinstance(bitem.data(0, QtCore.Qt.UserRole), ImageFilenames):
                images.append(bitem.data(0, QtCore.Qt.UserRole))
        # Don't try to display empty groups
        if not images:
            return False
        # Find missing files
        for image in images:
            if not os.path.exists(image.filename):
                missing_items_file_names.append(image.filename)
        # We cannot continue, as all images do not exist.
        if not images:
            if not remote:
                critical_error_message_box(
                    translate('ImagePlugin.MediaItem', 'Missing Image(s)'),
                    translate('ImagePlugin.MediaItem', 'The following image(s) no longer exist: %s')
                    % '\n'.join(missing_items_file_names))
            return False
        # We have missing as well as existing images. We ask what to do.
        elif missing_items_file_names and QtGui.QMessageBox.question(
                self, translate('ImagePlugin.MediaItem', 'Missing Image(s)'),
                translate('ImagePlugin.MediaItem', 'The following image(s) no longer exist: %s\n'
                          'Do you want to add the other images anyway?') % '\n'.join(missing_items_file_names),
                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)) == \
                QtGui.QMessageBox.No:
            return False
        # Continue with the existing images.
        for image in images:
            name = os.path.split(image.filename)[1]
            thumbnail = self.generate_thumbnail_path(image)
            service_item.add_from_image(image.filename, name, background, thumbnail)
        return True

    def check_group_exists(self, new_group):
        """
        Returns *True* if the given Group already exists in the database, otherwise *False*.

        :param new_group: The ImageGroups object that contains the name of the group that will be checked
        """
        groups = self.manager.get_all_objects(ImageGroups, ImageGroups.group_name == new_group.group_name)
        if groups:
            return True
        else:
            return False

    def on_add_group_click(self):
        """
        Called to add a new group
        """
        # Find out if a group must be pre-selected
        preselect_group = 0
        selected_items = self.list_view.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            if isinstance(selected_item.data(0, QtCore.Qt.UserRole), ImageFilenames):
                selected_item = selected_item.parent()
            if isinstance(selected_item, QtGui.QTreeWidgetItem):
                if isinstance(selected_item.data(0, QtCore.Qt.UserRole), ImageGroups):
                    preselect_group = selected_item.data(0, QtCore.Qt.UserRole).id
        # Show 'add group' dialog
        if self.add_group_form.exec_(show_top_level_group=True, selected_group=preselect_group):
            new_group = ImageGroups.populate(parent_id=self.add_group_form.parent_group_combobox.itemData(
                self.add_group_form.parent_group_combobox.currentIndex(), QtCore.Qt.UserRole),
                group_name=self.add_group_form.name_edit.text())
            if not self.check_group_exists(new_group):
                if self.manager.save_object(new_group):
                    self.load_full_list(self.manager.get_all_objects(
                        ImageFilenames, order_by_ref=ImageFilenames.filename))
                    self.expand_group(new_group.id)
                    self.fill_groups_combobox(self.choose_group_form.group_combobox)
                    self.fill_groups_combobox(self.add_group_form.parent_group_combobox)
                else:
                    critical_error_message_box(
                        message=translate('ImagePlugin.AddGroupForm', 'Could not add the new group.'))
            else:
                critical_error_message_box(message=translate('ImagePlugin.AddGroupForm', 'This group already exists.'))

    def on_reset_click(self):
        """
        Called to reset the Live background with the image selected.
        """
        self.reset_action.setVisible(False)
        self.live_controller.display.reset_image()

    def live_theme_changed(self):
        """
        Triggered by the change of theme in the slide controller.
        """
        self.reset_action.setVisible(False)

    def on_replace_click(self):
        """
        Called to replace Live background with the image selected.
        """
        if check_item_selected(
                self.list_view,
                translate('ImagePlugin.MediaItem', 'You must select an image to replace the background with.')):
            background = QtGui.QColor(Settings().value(self.settings_section + '/background color'))
            bitem = self.list_view.selectedItems()[0]
            if not isinstance(bitem.data(0, QtCore.Qt.UserRole), ImageFilenames):
                # Only continue when an image is selected.
                return
            filename = bitem.data(0, QtCore.Qt.UserRole).filename
            if os.path.exists(filename):
                if self.live_controller.display.direct_image(filename, background):
                    self.reset_action.setVisible(True)
                else:
                    critical_error_message_box(
                        UiStrings().LiveBGError,
                        translate('ImagePlugin.MediaItem', 'There was no display item to amend.'))
            else:
                critical_error_message_box(
                    UiStrings().LiveBGError,
                    translate('ImagePlugin.MediaItem', 'There was a problem replacing your background, '
                              'the image file "%s" no longer exists.') % filename)

    def search(self, string, show_error=True):
        """
        Perform a search on the image file names.

        :param string: The glob to search for
        :param show_error: Unused.
        """
        files = self.manager.get_all_objects(
            ImageFilenames, filter_clause=ImageFilenames.filename.contains(string),
            order_by_ref=ImageFilenames.filename)
        results = []
        for file_object in files:
            filename = os.path.split(str(file_object.filename))[1]
            results.append([file_object.filename, filename])
        return results

    def create_item_from_id(self, item_id):
        """
        Create a media item from an item id. Overridden from the parent method to change the item type.

        :param item_id: Id to make live
        """
        item = QtGui.QTreeWidgetItem()
        item_data = self.manager.get_object_filtered(ImageFilenames, ImageFilenames.filename == item_id)
        item.setText(0, os.path.basename(item_data.filename))
        item.setData(0, QtCore.Qt.UserRole, item_data)
        return item
