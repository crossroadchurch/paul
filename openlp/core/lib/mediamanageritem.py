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
Provides the generic functions for interfacing plugins with the Media Manager.
"""
import logging
import os
import re

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, RegistryProperties, Settings, UiStrings, translate
from openlp.core.lib import FileDialog, OpenLPToolbar, ServiceItem, StringContent, ListWidgetWithDnD, \
    ServiceItemContext
from openlp.core.lib.searchedit import SearchEdit
from openlp.core.lib.ui import create_widget_action, critical_error_message_box

log = logging.getLogger(__name__)


class MediaManagerItem(QtGui.QWidget, RegistryProperties):
    """
    MediaManagerItem is a helper widget for plugins.

    None of the following *need* to be used, feel free to override them completely in your plugin's implementation.
    Alternatively, call them from your plugin before or after you've done extra things that you need to.

    **Constructor Parameters**

    ``parent``
        The parent widget. Usually this will be the *Media Manager* itself. This needs to be a class descended from
        ``QWidget``.

    ``plugin``
        The plugin widget. Usually this will be the *Plugin* itself. This needs to be a class descended from ``Plugin``.

    **Member Variables**

    When creating a descendant class from this class for your plugin, the following member variables should be set.

     ``self.on_new_prompt``

        Defaults to *'Select Image(s)'*.

     ``self.on_new_file_masks``
        Defaults to *'Images (*.jpg *jpeg *.gif *.png *.bmp)'*. This assumes that the new action is to load a file. If
        not, you need to override the ``OnNew`` method.

     ``self.PreviewFunction``
        This must be a method which returns a QImage to represent the item (usually a preview). No scaling is required,
        that is performed automatically by OpenLP when necessary. If this method is not defined, a default will be used
        (treat the filename as an image).
    """
    log.info('Media Item loaded')

    def __init__(self, parent=None, plugin=None):
        """
        Constructor to create the media manager item.
        """
        super(MediaManagerItem, self).__init__(parent)
        self.plugin = plugin
        self._setup()
        self.setup_item()

    def _setup(self):
        """
        Run some initial setup. This method is separate from __init__ in order to mock it out in tests.
        """
        self.hide()
        self.whitespace = re.compile(r'[\W_]+', re.UNICODE)
        visible_title = self.plugin.get_string(StringContent.VisibleName)
        self.title = str(visible_title['title'])
        Registry().register(self.plugin.name, self)
        self.settings_section = self.plugin.name
        self.toolbar = None
        self.remote_triggered = None
        self.single_service_item = True
        self.quick_preview_allowed = False
        self.has_search = False
        self.page_layout = QtGui.QVBoxLayout(self)
        self.page_layout.setSpacing(0)
        self.page_layout.setMargin(0)
        self.required_icons()
        self.setupUi()
        self.retranslateUi()
        self.auto_select_id = -1
        # Need to use event as called across threads and UI is updated
        QtCore.QObject.connect(self, QtCore.SIGNAL('%s_go_live' % self.plugin.name), self.go_live_remote)
        QtCore.QObject.connect(self, QtCore.SIGNAL('%s_add_to_service' % self.plugin.name), self.add_to_service_remote)

    def setup_item(self):
        """
        Override this for additional Plugin setup
        """
        pass

    def required_icons(self):
        """
        This method is called to define the icons for the plugin. It provides a default set and the plugin is able to
        override the if required.
        """
        self.has_import_icon = False
        self.has_new_icon = True
        self.has_edit_icon = True
        self.has_file_icon = False
        self.has_delete_icon = True
        self.add_to_service_item = False

    def retranslateUi(self):
        """
        This method is called automatically to provide OpenLP with the opportunity to translate the ``MediaManagerItem``
        to another language.
        """
        pass

    def add_toolbar(self):
        """
        A method to help developers easily add a toolbar to the media manager item.
        """
        if self.toolbar is None:
            self.toolbar = OpenLPToolbar(self)
            self.page_layout.addWidget(self.toolbar)

    def setupUi(self):
        """
        This method sets up the interface on the button. Plugin developers use this to add and create toolbars, and the
        rest of the interface of the media manager item.
        """
        # Add a toolbar
        self.add_toolbar()
        # Allow the plugin to define buttons at start of bar
        self.add_start_header_bar()
        # Add the middle of the tool bar (pre defined)
        self.add_middle_header_bar()
        # Allow the plugin to define buttons at end of bar
        self.add_end_header_bar()
        # Add the list view
        self.add_list_view_to_toolbar()

    def add_middle_header_bar(self):
        """
        Create buttons for the media item toolbar
        """
        toolbar_actions = []
        # Import Button
        if self.has_import_icon:
            toolbar_actions.append(['Import', StringContent.Import,
                                    ':/general/general_import.png', self.on_import_click])
        # Load Button
        if self.has_file_icon:
            toolbar_actions.append(['Load', StringContent.Load, ':/general/general_open.png', self.on_file_click])
        # New Button
        if self.has_new_icon:
            toolbar_actions.append(['New', StringContent.New, ':/general/general_new.png', self.on_new_click])
        # Edit Button
        if self.has_edit_icon:
            toolbar_actions.append(['Edit', StringContent.Edit, ':/general/general_edit.png', self.on_edit_click])
        # Delete Button
        if self.has_delete_icon:
            toolbar_actions.append(['Delete', StringContent.Delete,
                                    ':/general/general_delete.png', self.on_delete_click])
        # Preview
        toolbar_actions.append(['Preview', StringContent.Preview,
                                ':/general/general_preview.png', self.on_preview_click])
        # Live Button
        toolbar_actions.append(['Live', StringContent.Live, ':/general/general_live.png', self.on_live_click])
        # Add to service Button
        toolbar_actions.append(['Service', StringContent.Service, ':/general/general_add.png', self.on_add_click])
        for action in toolbar_actions:
            if action[0] == StringContent.Preview:
                self.toolbar.addSeparator()
            self.toolbar.add_toolbar_action('%s%sAction' % (self.plugin.name, action[0]),
                                            text=self.plugin.get_string(action[1])['title'], icon=action[2],
                                            tooltip=self.plugin.get_string(action[1])['tooltip'],
                                            triggers=action[3])

    def add_list_view_to_toolbar(self):
        """
        Creates the main widget for listing items the media item is tracking
        """
        # Add the List widget
        self.list_view = ListWidgetWithDnD(self, self.plugin.name)
        self.list_view.setSpacing(1)
        self.list_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setObjectName('%sListView' % self.plugin.name)
        # Add to page_layout
        self.page_layout.addWidget(self.list_view)
        # define and add the context menu
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        if self.has_edit_icon:
            create_widget_action(self.list_view,
                                 text=self.plugin.get_string(StringContent.Edit)['title'],
                                 icon=':/general/general_edit.png',
                                 triggers=self.on_edit_click)
            create_widget_action(self.list_view, separator=True)
        create_widget_action(self.list_view,
                             'listView%s%sItem' % (self.plugin.name.title(), StringContent.Preview.title()),
                             text=self.plugin.get_string(StringContent.Preview)['title'],
                             icon=':/general/general_preview.png',
                             can_shortcuts=True,
                             triggers=self.on_preview_click)
        create_widget_action(self.list_view,
                             'listView%s%sItem' % (self.plugin.name.title(), StringContent.Live.title()),
                             text=self.plugin.get_string(StringContent.Live)['title'],
                             icon=':/general/general_live.png',
                             can_shortcuts=True,
                             triggers=self.on_live_click)
        create_widget_action(self.list_view,
                             'listView%s%sItem' % (self.plugin.name.title(), StringContent.Service.title()),
                             can_shortcuts=True,
                             text=self.plugin.get_string(StringContent.Service)['title'],
                             icon=':/general/general_add.png',
                             triggers=self.on_add_click)
        if self.has_delete_icon:
            create_widget_action(self.list_view, separator=True)
            create_widget_action(self.list_view,
                                 'listView%s%sItem' % (self.plugin.name.title(), StringContent.Delete.title()),
                                 text=self.plugin.get_string(StringContent.Delete)['title'],
                                 icon=':/general/general_delete.png',
                                 can_shortcuts=True, triggers=self.on_delete_click)
        if self.add_to_service_item:
            create_widget_action(self.list_view, separator=True)
            create_widget_action(self.list_view,
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

    def add_search_to_toolbar(self):
        """
        Creates a search field with button and related signal handling.
        """
        self.search_widget = QtGui.QWidget(self)
        self.search_widget.setObjectName('search_widget')
        self.search_layout = QtGui.QVBoxLayout(self.search_widget)
        self.search_layout.setObjectName('search_layout')
        self.search_text_layout = QtGui.QFormLayout()
        self.search_text_layout.setObjectName('search_text_layout')
        self.search_text_label = QtGui.QLabel(self.search_widget)
        self.search_text_label.setObjectName('search_text_label')
        self.search_text_edit = SearchEdit(self.search_widget)
        self.search_text_edit.setObjectName('search_text_edit')
        self.search_text_label.setBuddy(self.search_text_edit)
        self.search_text_layout.addRow(self.search_text_label, self.search_text_edit)
        self.search_layout.addLayout(self.search_text_layout)
        self.search_button_layout = QtGui.QHBoxLayout()
        self.search_button_layout.setObjectName('search_button_layout')
        self.search_button_layout.addStretch()
        self.search_text_button = QtGui.QPushButton(self.search_widget)
        self.search_text_button.setObjectName('search_text_button')
        self.search_button_layout.addWidget(self.search_text_button)
        self.search_layout.addLayout(self.search_button_layout)
        self.page_layout.addWidget(self.search_widget)
        # Signals and slots
        self.search_text_edit.returnPressed.connect(self.on_search_text_button_clicked)
        self.search_text_button.clicked.connect(self.on_search_text_button_clicked)
        self.search_text_edit.textChanged.connect(self.on_search_text_edit_changed)

    def add_custom_context_actions(self):
        """
        Implement this method in your descendant media manager item to add any context menu items.
        This method is called automatically.
        """
        pass

    def initialise(self):
        """
        Implement this method in your descendant media manager item to do any UI or other initialisation.
        This method is called automatically.
        """
        pass

    def add_start_header_bar(self):
        """
        Slot at start of toolbar for plugin to add widgets
        """
        pass

    def add_end_header_bar(self):
        """
        Slot at end of toolbar for plugin to add widgets
        """
        pass

    def on_file_click(self):
        """
        Add a file to the list widget to make it available for showing
        """
        files = FileDialog.getOpenFileNames(self, self.on_new_prompt,
                                            Settings().value(self.settings_section + '/last directory'),
                                            self.on_new_file_masks)
        log.info('New files(s) %s' % files)
        if files:
            self.application.set_busy_cursor()
            self.validate_and_load(files)
        self.application.set_normal_cursor()

    def load_file(self, data):
        """
        Turn file from Drag and Drop into an array so the Validate code can run it.

        :param data: A dictionary containing the list of files to be loaded and the target
        """
        new_files = []
        error_shown = False
        for file_name in data['files']:
            file_type = file_name.split('.')[-1]
            if file_type.lower() not in self.on_new_file_masks:
                if not error_shown:
                    critical_error_message_box(translate('OpenLP.MediaManagerItem', 'Invalid File Type'),
                                               translate('OpenLP.MediaManagerItem',
                                                         'Invalid File %s.\nSuffix not supported') % file_name)
                    error_shown = True
            else:
                new_files.append(file_name)
        if new_files:
            self.validate_and_load(new_files, data['target'])

    def dnd_move_internal(self, target):
        """
        Handle internal moving of media manager items

        :param target: The target of the DnD action
        """
        pass

    def validate_and_load(self, files, target_group=None):
        """
        Process a list for files either from the File Dialog or from Drag and
        Drop

        :param files: The files to be loaded.
        :param target_group: The QTreeWidgetItem of the group that will be the parent of the added files
        """
        names = []
        full_list = []
        for count in range(self.list_view.count()):
            names.append(self.list_view.item(count).text())
            full_list.append(self.list_view.item(count).data(QtCore.Qt.UserRole))
        duplicates_found = False
        files_added = False
        for file_path in files:
            if file_path in full_list:
                duplicates_found = True
            else:
                files_added = True
                full_list.append(file_path)
        if full_list and files_added:
            if target_group is None:
                self.list_view.clear()
            self.load_list(full_list, target_group)
            last_dir = os.path.split(files[0])[0]
            Settings().setValue(self.settings_section + '/last directory', last_dir)
            Settings().setValue('%s/%s files' % (self.settings_section, self.settings_section), self.get_file_list())
        if duplicates_found:
            critical_error_message_box(UiStrings().Duplicate,
                                       translate('OpenLP.MediaManagerItem',
                                                 'Duplicate files were found on import and were ignored.'))

    def context_menu(self, point):
        """
        Display a context menu

        :param point: The point the cursor was at
        """
        item = self.list_view.itemAt(point)
        # Decide if we have to show the context menu or not.
        if item is None:
            return
        if not item.flags() & QtCore.Qt.ItemIsSelectable:
            return
        self.menu.exec_(self.list_view.mapToGlobal(point))

    def get_file_list(self):
        """
        Return the current list of files
        """
        file_list = []
        for index in range(self.list_view.count()):
            list_item = self.list_view.item(index)
            filename = list_item.data(QtCore.Qt.UserRole)
            file_list.append(filename)
        return file_list

    def load_list(self, load_list, target_group):
        """
        Load a list. Needs to be implemented by the plugin.

        :param load_list: List object to load
        :param target_group: Group to load
        """
        raise NotImplementedError('MediaManagerItem.loadList needs to be defined by the plugin')

    def on_new_click(self):
        """
        Hook for plugins to define behaviour for adding new items.
        """
        pass

    def on_edit_click(self):
        """
        Hook for plugins to define behaviour for editing items.
        """
        pass

    def on_delete_click(self):
        """
        Delete an item. Needs to be implemented by the plugin.
        """
        raise NotImplementedError('MediaManagerItem.on_delete_click needs to be defined by the plugin')

    def on_focus(self):
        """
        Run when a tab in the media manager gains focus. This gives the media
        item a chance to focus any elements it wants to.
        """
        pass

    def generate_slide_data(self, service_item, item=None, xml_version=False, remote=False,
                            context=ServiceItemContext.Live):
        """
        Generate the slide data. Needs to be implemented by the plugin.
        :param service_item: The service Item to be processed
        :param item: The database item to be used to build the service item
        :param xml_version:
        :param remote: Was this remote triggered (False)
        :param context: The service context
        """
        raise NotImplementedError('MediaManagerItem.generate_slide_data needs to be defined by the plugin')

    def on_double_clicked(self):
        """
        Allows the list click action to be determined dynamically
        """
        if Settings().value('advanced/double click live'):
            self.on_live_click()
        elif not Settings().value('advanced/single click preview'):
            # NOTE: The above check is necessary to prevent bug #1419300
            self.on_preview_click()

    def on_selection_change(self):
        """
        Allows the change of current item in the list to be actioned
        """
        if Settings().value('advanced/single click preview') and self.quick_preview_allowed \
                and self.list_view.selectedIndexes() and self.auto_select_id == -1:
            self.on_preview_click(True)

    def on_preview_click(self, keep_focus=False):
        """
        Preview an item by building a service item then adding that service item to the preview slide controller.

        :param keep_focus: Do we keep focus (False)
        """
        if not self.list_view.selectedIndexes() and not self.remote_triggered:
            QtGui.QMessageBox.information(self, UiStrings().NISp,
                                          translate('OpenLP.MediaManagerItem',
                                                    'You must select one or more items to preview.'))
        else:
            log.debug('%s Preview requested' % self.plugin.name)
            service_item = self.build_service_item()
            if service_item:
                service_item.from_plugin = True
                self.preview_controller.add_service_item(service_item)
                if not keep_focus:
                    self.preview_controller.preview_widget.setFocus()

    def on_live_click(self):
        """
        Send an item live by building a service item then adding that service item to the live slide controller.
        """
        if not self.list_view.selectedIndexes():
            QtGui.QMessageBox.information(self, UiStrings().NISp,
                                          translate('OpenLP.MediaManagerItem',
                                                    'You must select one or more items to send live.'))
        else:
            self.go_live()

    def go_live_remote(self, message):
        """
        Remote Call wrapper

        :param message: The passed data item_id:Remote.
        """
        self.go_live(message[0], remote=message[1])

    def go_live(self, item_id=None, remote=False):
        """
        Make the currently selected item go live.

        :param item_id: item to make live
        :param remote: From Remote
        """
        log.debug('%s Live requested', self.plugin.name)
        item = None
        if item_id:
            item = self.create_item_from_id(item_id)
        service_item = self.build_service_item(item, remote=remote)
        if service_item:
            if not item_id:
                service_item.from_plugin = True
            if remote:
                service_item.will_auto_start = True
            self.live_controller.add_service_item(service_item)
            self.live_controller.preview_widget.setFocus()

    def create_item_from_id(self, item_id):
        """
        Create a media item from an item id.

        :param item_id: Id to make live
        """
        item = QtGui.QListWidgetItem()
        item.setData(QtCore.Qt.UserRole, item_id)
        return item

    def on_add_click(self):
        """
        Add a selected item to the current service
        """
        if not self.list_view.selectedIndexes():
            QtGui.QMessageBox.information(self, UiStrings().NISp,
                                          translate('OpenLP.MediaManagerItem',
                                                    'You must select one or more items to add.'))
        else:
            # Is it possible to process multiple list items to generate
            # multiple service items?
            if self.single_service_item:
                log.debug('%s Add requested', self.plugin.name)
                self.add_to_service(replace=self.remote_triggered)
            else:
                items = self.list_view.selectedIndexes()
                drop_position = self.service_manager.get_drop_position()
                for item in items:
                    self.add_to_service(item, position=drop_position)
                    if drop_position != -1:
                        drop_position += 1

    def add_to_service_remote(self, message):
        """
        Remote Call wrapper

        :param message: The passed data item:Remote.
        """
        self.add_to_service(message[0], remote=message[1])

    def add_to_service(self, item=None, replace=None, remote=False, position=-1):
        """
        Add this item to the current service.

        :param item: Item to be processed
        :param replace: Replace the existing item
        :param remote: Triggered from remote
        :param position: Position to place item
        """
        service_item = self.build_service_item(item, True, remote=remote, context=ServiceItemContext.Service)
        if service_item:
            service_item.from_plugin = False
            self.service_manager.add_service_item(service_item, replace=replace, position=position)

    def on_add_edit_click(self):
        """
        Add a selected item to an existing item in the current service.
        """
        if not self.list_view.selectedIndexes() and not self.remote_triggered:
            QtGui.QMessageBox.information(self, UiStrings().NISp,
                                          translate('OpenLP.MediaManagerItem', 'You must select one or more items.'))
        else:
            log.debug('%s Add requested', self.plugin.name)
            service_item = self.service_manager.get_service_item()
            if not service_item:
                QtGui.QMessageBox.information(self, UiStrings().NISs,
                                              translate('OpenLP.MediaManagerItem',
                                                        'You must select an existing service item to add to.'))
            elif self.plugin.name == service_item.name:
                self.generate_slide_data(service_item)
                self.service_manager.add_service_item(service_item, replace=True)
            else:
                # Turn off the remote edit update message indicator
                QtGui.QMessageBox.information(self, translate('OpenLP.MediaManagerItem', 'Invalid Service Item'),
                                              translate('OpenLP.MediaManagerItem',
                                                        'You must select a %s service item.') % self.title)

    def build_service_item(self, item=None, xml_version=False, remote=False, context=ServiceItemContext.Live):
        """
        Common method for generating a service item
        :param item: Service Item to be built.
        :param xml_version: version of XML (False)
        :param remote: Remote triggered (False)
        :param context: The context on which this is called
        """
        service_item = ServiceItem(self.plugin)
        service_item.add_icon(self.plugin.icon_path)
        if self.generate_slide_data(service_item, item, xml_version, remote, context):
            return service_item
        else:
            return None

    def service_load(self, item):
        """
        Method to add processing when a service has been loaded and individual service items need to be processed by the
        plugins.

        :param item: The item to be processed and returned.
        """
        return item

    def check_search_result(self):
        """
        Checks if the list_view is empty and adds a "No Search Results" item.
        """
        if self.list_view.count():
            return
        message = translate('OpenLP.MediaManagerItem', 'No Search Results')
        item = QtGui.QListWidgetItem(message)
        item.setFlags(QtCore.Qt.NoItemFlags)
        font = QtGui.QFont()
        font.setItalic(True)
        item.setFont(font)
        self.list_view.addItem(item)

    def _get_id_of_item_to_generate(self, item, remote_item):
        """
        Utility method to check items being submitted for slide generation.

        :param item: The item to check.
        :param remote_item: The id to assign if the slide generation was remotely triggered.
        """
        if item is None:
            if self.remote_triggered is None:
                item = self.list_view.currentItem()
                if item is None:
                    return False
                item_id = item.data(QtCore.Qt.UserRole)
            else:
                item_id = remote_item
        else:
            item_id = item.data(QtCore.Qt.UserRole)
        return item_id

    def save_auto_select_id(self):
        """
        Sorts out, what item to select after loading a list.
        """
        # The item to select has not been set.
        if self.auto_select_id == -1:
            item = self.list_view.currentItem()
            if item:
                self.auto_select_id = item.data(QtCore.Qt.UserRole)

    def search(self, string, show_error=True):
        """
        Performs a plugin specific search for items containing ``string``

        :param string: String to be displayed
        :param show_error: Should the error be shown (True)
        """
        raise NotImplementedError('Plugin.search needs to be defined by the plugin')
