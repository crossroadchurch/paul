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
The service manager sets up, loads, saves and manages services.
"""
import html
import os
import shutil
import zipfile
import json
from tempfile import mkstemp
from datetime import datetime, timedelta

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, RegistryProperties, AppLocation, Settings, ThemeLevel, OpenLPMixin, \
    RegistryMixin, check_directory_exists, UiStrings, translate
from openlp.core.lib import OpenLPToolbar, ServiceItem, ItemCapabilities, PluginStatus, build_icon
from openlp.core.lib.ui import critical_error_message_box, create_widget_action, find_and_set_in_combo_box
from openlp.core.ui import ServiceNoteForm, ServiceItemEditForm, StartTimeForm
from openlp.core.ui.printserviceform import PrintServiceForm
from openlp.core.utils import delete_file, split_filename, format_time
from openlp.core.utils.actions import ActionList, CategoryOrder


class ServiceManagerList(QtGui.QTreeWidget):
    """
    Set up key bindings and mouse behaviour for the service list
    """
    def __init__(self, service_manager, parent=None):
        """
        Constructor
        """
        super(ServiceManagerList, self).__init__(parent)
        self.service_manager = service_manager

    def keyPressEvent(self, event):
        """
        Capture Key press and respond accordingly.
        :param event:
        """
        if isinstance(event, QtGui.QKeyEvent):
            # here accept the event and do something
            if event.key() == QtCore.Qt.Key_Up:
                self.service_manager.on_move_selection_up()
                event.accept()
            elif event.key() == QtCore.Qt.Key_Down:
                self.service_manager.on_move_selection_down()
                event.accept()
            elif event.key() == QtCore.Qt.Key_Delete:
                self.service_manager.on_delete_from_service()
                event.accept()
            event.ignore()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        """
        Drag and drop event does not care what data is selected as the recipient will use events to request the data
        move just tell it what plugin to call
        :param event:
        """
        if event.buttons() != QtCore.Qt.LeftButton:
            event.ignore()
            return
        if not self.itemAt(self.mapFromGlobal(QtGui.QCursor.pos())):
            event.ignore()
            return
        drag = QtGui.QDrag(self)
        mime_data = QtCore.QMimeData()
        drag.setMimeData(mime_data)
        mime_data.setText('ServiceManager')
        drag.start(QtCore.Qt.CopyAction)


class Ui_ServiceManager(object):
    """
    UI part of the Service Manager
    """
    def setup_ui(self, widget):
        """
        Define the UI
        :param widget:
        """
        # start with the layout
        self.layout = QtGui.QVBoxLayout(widget)
        self.layout.setSpacing(0)
        self.layout.setMargin(0)
        # Create the top toolbar
        self.toolbar = OpenLPToolbar(widget)
        self.toolbar.add_toolbar_action('newService', text=UiStrings().NewService, icon=':/general/general_new.png',
                                        tooltip=UiStrings().CreateService, triggers=self.on_new_service_clicked)
        self.toolbar.add_toolbar_action('openService', text=UiStrings().OpenService,
                                        icon=':/general/general_open.png',
                                        tooltip=translate('OpenLP.ServiceManager', 'Load an existing service.'),
                                        triggers=self.on_load_service_clicked)
        self.toolbar.add_toolbar_action('saveService', text=UiStrings().SaveService,
                                        icon=':/general/general_save.png',
                                        tooltip=translate('OpenLP.ServiceManager', 'Save this service.'),
                                        triggers=self.decide_save_method)
        self.toolbar.addSeparator()
        self.theme_label = QtGui.QLabel('%s:' % UiStrings().Theme, widget)
        self.theme_label.setMargin(3)
        self.theme_label.setObjectName('theme_label')
        self.toolbar.add_toolbar_widget(self.theme_label)
        self.theme_combo_box = QtGui.QComboBox(self.toolbar)
        self.theme_combo_box.setToolTip(translate('OpenLP.ServiceManager', 'Select a theme for the service.'))
        self.theme_combo_box.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.theme_combo_box.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.theme_combo_box.setObjectName('theme_combo_box')
        self.toolbar.add_toolbar_widget(self.theme_combo_box)
        self.toolbar.setObjectName('toolbar')
        self.layout.addWidget(self.toolbar)
        # Create the service manager list
        self.service_manager_list = ServiceManagerList(widget)
        self.service_manager_list.setEditTriggers(
            QtGui.QAbstractItemView.CurrentChanged |
            QtGui.QAbstractItemView.DoubleClicked |
            QtGui.QAbstractItemView.EditKeyPressed)
        self.service_manager_list.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.service_manager_list.setAlternatingRowColors(True)
        self.service_manager_list.setHeaderHidden(True)
        self.service_manager_list.setExpandsOnDoubleClick(False)
        self.service_manager_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.service_manager_list.customContextMenuRequested.connect(self.context_menu)
        self.service_manager_list.setObjectName('service_manager_list')
        # enable drop
        self.service_manager_list.__class__.dragEnterEvent = self.drag_enter_event
        self.service_manager_list.__class__.dragMoveEvent = self.drag_enter_event
        self.service_manager_list.__class__.dropEvent = self.drop_event
        self.layout.addWidget(self.service_manager_list)
        # Add the bottom toolbar
        self.order_toolbar = OpenLPToolbar(widget)
        action_list = ActionList.get_instance()
        action_list.add_category(UiStrings().Service, CategoryOrder.standard_toolbar)
        self.service_manager_list.move_top = self.order_toolbar.add_toolbar_action(
            'moveTop',
            text=translate('OpenLP.ServiceManager', 'Move to &top'), icon=':/services/service_top.png',
            tooltip=translate('OpenLP.ServiceManager', 'Move item to the top of the service.'),
            can_shortcuts=True, category=UiStrings().Service, triggers=self.on_service_top)
        self.service_manager_list.move_up = self.order_toolbar.add_toolbar_action(
            'moveUp',
            text=translate('OpenLP.ServiceManager', 'Move &up'), icon=':/services/service_up.png',
            tooltip=translate('OpenLP.ServiceManager', 'Move item up one position in the service.'),
            can_shortcuts=True, category=UiStrings().Service, triggers=self.on_service_up)
        self.service_manager_list.move_down = self.order_toolbar.add_toolbar_action(
            'moveDown',
            text=translate('OpenLP.ServiceManager', 'Move &down'), icon=':/services/service_down.png',
            tooltip=translate('OpenLP.ServiceManager', 'Move item down one position in the service.'),
            can_shortcuts=True, category=UiStrings().Service, triggers=self.on_service_down)
        self.service_manager_list.move_bottom = self.order_toolbar.add_toolbar_action(
            'moveBottom',
            text=translate('OpenLP.ServiceManager', 'Move to &bottom'), icon=':/services/service_bottom.png',
            tooltip=translate('OpenLP.ServiceManager', 'Move item to the end of the service.'),
            can_shortcuts=True, category=UiStrings().Service, triggers=self.on_service_end)
        self.service_manager_list.down = self.order_toolbar.add_toolbar_action(
            'down',
            text=translate('OpenLP.ServiceManager', 'Move &down'), can_shortcuts=True,
            tooltip=translate('OpenLP.ServiceManager', 'Moves the selection down the window.'), visible=False,
            triggers=self.on_move_selection_down)
        action_list.add_action(self.service_manager_list.down)
        self.service_manager_list.up = self.order_toolbar.add_toolbar_action(
            'up',
            text=translate('OpenLP.ServiceManager', 'Move up'), can_shortcuts=True,
            tooltip=translate('OpenLP.ServiceManager', 'Moves the selection up the window.'), visible=False,
            triggers=self.on_move_selection_up)
        action_list.add_action(self.service_manager_list.up)
        self.order_toolbar.addSeparator()
        self.service_manager_list.delete = self.order_toolbar.add_toolbar_action(
            'delete', can_shortcuts=True,
            text=translate('OpenLP.ServiceManager', '&Delete From Service'), icon=':/general/general_delete.png',
            tooltip=translate('OpenLP.ServiceManager', 'Delete the selected item from the service.'),
            triggers=self.on_delete_from_service)
        self.order_toolbar.addSeparator()
        self.service_manager_list.expand = self.order_toolbar.add_toolbar_action(
            'expand', can_shortcuts=True,
            text=translate('OpenLP.ServiceManager', '&Expand all'), icon=':/services/service_expand_all.png',
            tooltip=translate('OpenLP.ServiceManager', 'Expand all the service items.'),
            category=UiStrings().Service, triggers=self.on_expand_all)
        self.service_manager_list.collapse = self.order_toolbar.add_toolbar_action(
            'collapse', can_shortcuts=True,
            text=translate('OpenLP.ServiceManager', '&Collapse all'), icon=':/services/service_collapse_all.png',
            tooltip=translate('OpenLP.ServiceManager', 'Collapse all the service items.'),
            category=UiStrings().Service, triggers=self.on_collapse_all)
        self.order_toolbar.addSeparator()
        self.service_manager_list.make_live = self.order_toolbar.add_toolbar_action(
            'make_live', can_shortcuts=True,
            text=translate('OpenLP.ServiceManager', 'Go Live'), icon=':/general/general_live.png',
            tooltip=translate('OpenLP.ServiceManager', 'Send the selected item to Live.'),
            category=UiStrings().Service,
            triggers=self.make_live)
        self.layout.addWidget(self.order_toolbar)
        # Connect up our signals and slots
        self.theme_combo_box.activated.connect(self.on_theme_combo_box_selected)
        self.service_manager_list.doubleClicked.connect(self.on_make_live)
        self.service_manager_list.itemCollapsed.connect(self.collapsed)
        self.service_manager_list.itemExpanded.connect(self.expanded)
        # Last little bits of setting up
        self.service_theme = Settings().value(self.main_window.service_manager_settings_section + '/service theme')
        self.service_path = AppLocation.get_section_data_path('servicemanager')
        # build the drag and drop context menu
        self.dnd_menu = QtGui.QMenu()
        self.new_action = self.dnd_menu.addAction(translate('OpenLP.ServiceManager', '&Add New Item'))
        self.new_action.setIcon(build_icon(':/general/general_edit.png'))
        self.add_to_action = self.dnd_menu.addAction(translate('OpenLP.ServiceManager', '&Add to Selected Item'))
        self.add_to_action.setIcon(build_icon(':/general/general_edit.png'))
        # build the context menu
        self.menu = QtGui.QMenu()
        self.edit_action = create_widget_action(self.menu, text=translate('OpenLP.ServiceManager', '&Edit Item'),
                                                icon=':/general/general_edit.png', triggers=self.remote_edit)
        self.rename_action = create_widget_action(self.menu, text=translate('OpenLP.ServiceManager', '&Rename...'),
                                                  icon=':/general/general_edit.png',
                                                  triggers=self.on_service_item_rename)
        self.maintain_action = create_widget_action(self.menu, text=translate('OpenLP.ServiceManager', '&Reorder Item'),
                                                    icon=':/general/general_edit.png',
                                                    triggers=self.on_service_item_edit_form)
        self.notes_action = create_widget_action(self.menu, text=translate('OpenLP.ServiceManager', '&Notes'),
                                                 icon=':/services/service_notes.png',
                                                 triggers=self.on_service_item_note_form)
        self.time_action = create_widget_action(self.menu, text=translate('OpenLP.ServiceManager', '&Start Time'),
                                                icon=':/media/media_time.png', triggers=self.on_start_time_form)
        self.auto_start_action = create_widget_action(self.menu, text='',
                                                      icon=':/media/auto-start_active.png',
                                                      triggers=self.on_auto_start)
        # Add already existing delete action to the menu.
        self.menu.addAction(self.service_manager_list.delete)
        self.create_custom_action = create_widget_action(self.menu,
                                                         text=translate('OpenLP.ServiceManager', 'Create New &Custom '
                                                                                                 'Slide'),
                                                         icon=':/general/general_edit.png',
                                                         triggers=self.create_custom)
        self.menu.addSeparator()
        # Add AutoPlay menu actions
        self.auto_play_slides_menu = QtGui.QMenu(translate('OpenLP.ServiceManager', '&Auto play slides'))
        self.menu.addMenu(self.auto_play_slides_menu)
        auto_play_slides_group = QtGui.QActionGroup(self.auto_play_slides_menu)
        auto_play_slides_group.setExclusive(True)
        self.auto_play_slides_loop = create_widget_action(self.auto_play_slides_menu,
                                                          text=translate('OpenLP.ServiceManager', 'Auto play slides '
                                                                                                  '&Loop'),
                                                          checked=False, triggers=self.toggle_auto_play_slides_loop)
        auto_play_slides_group.addAction(self.auto_play_slides_loop)
        self.auto_play_slides_once = create_widget_action(self.auto_play_slides_menu,
                                                          text=translate('OpenLP.ServiceManager', 'Auto play slides '
                                                                                                  '&Once'),
                                                          checked=False, triggers=self.toggle_auto_play_slides_once)
        auto_play_slides_group.addAction(self.auto_play_slides_once)
        self.auto_play_slides_menu.addSeparator()
        self.timed_slide_interval = create_widget_action(self.auto_play_slides_menu,
                                                         text=translate('OpenLP.ServiceManager', '&Delay between '
                                                                                                 'slides'),
                                                         triggers=self.on_timed_slide_interval)
        self.menu.addSeparator()
        self.preview_action = create_widget_action(self.menu, text=translate('OpenLP.ServiceManager', 'Show &Preview'),
                                                   icon=':/general/general_preview.png', triggers=self.make_preview)
        # Add already existing make live action to the menu.
        self.menu.addAction(self.service_manager_list.make_live)
        self.menu.addSeparator()
        self.theme_menu = QtGui.QMenu(translate('OpenLP.ServiceManager', '&Change Item Theme'))
        self.menu.addMenu(self.theme_menu)
        self.service_manager_list.addActions(
            [self.service_manager_list.move_down,
             self.service_manager_list.move_up,
             self.service_manager_list.make_live,
             self.service_manager_list.move_top,
             self.service_manager_list.move_bottom,
             self.service_manager_list.up,
             self.service_manager_list.down,
             self.service_manager_list.expand,
             self.service_manager_list.collapse
             ])
        Registry().register_function('theme_update_list', self.update_theme_list)
        Registry().register_function('config_screen_changed', self.regenerate_service_items)
        Registry().register_function('theme_update_global', self.theme_change)
        Registry().register_function('mediaitem_suffix_reset', self.reset_supported_suffixes)

    def drag_enter_event(self, event):
        """
        Accept Drag events

        :param event: Handle of the event passed
        """
        event.accept()


class ServiceManager(OpenLPMixin, RegistryMixin, QtGui.QWidget, Ui_ServiceManager, RegistryProperties):
    """
    Manages the services. This involves taking text strings from plugins and adding them to the service. This service
    can then be zipped up with all the resources used into one OSZ or oszl file for use on any OpenLP v2 installation.
    Also handles the UI tasks of moving things up and down etc.
    """
    def __init__(self, parent=None):
        """
        Sets up the service manager, toolbars, list view, et al.
        """
        super(ServiceManager, self).__init__(parent)
        self.active = build_icon(':/media/auto-start_active.png')
        self.inactive = build_icon(':/media/auto-start_inactive.png')
        self.service_items = []
        self.suffixes = []
        self.drop_position = -1
        self.service_id = 0
        # is a new service and has not been saved
        self._modified = False
        self._file_name = ''
        self.service_has_all_original_files = True

    def bootstrap_initialise(self):
        """
        To be called as part of initialisation
        """
        self.setup_ui(self)
        # Need to use event as called across threads and UI is updated
        QtCore.QObject.connect(self, QtCore.SIGNAL('servicemanager_set_item'), self.on_set_item)
        QtCore.QObject.connect(self, QtCore.SIGNAL('servicemanager_next_item'), self.next_item)
        QtCore.QObject.connect(self, QtCore.SIGNAL('servicemanager_previous_item'), self.previous_item)

    def bootstrap_post_set_up(self):
        """
        Can be set up as a late setup
        """
        self.service_note_form = ServiceNoteForm()
        self.service_item_edit_form = ServiceItemEditForm()
        self.start_time_form = StartTimeForm()

    def set_modified(self, modified=True):
        """
        Setter for property "modified". Sets whether or not the current service has been modified.

        :param modified: Indicates if the service has new or removed items.  Used to trigger a remote update.
        """
        if modified:
            self.service_id += 1
        self._modified = modified
        service_file = self.short_file_name() or translate('OpenLP.ServiceManager', 'Untitled Service')
        self.main_window.set_service_modified(modified, service_file)

    def is_modified(self):
        """
        Getter for boolean property "modified".
        """
        return self._modified

    def set_file_name(self, file_name):
        """
        Setter for service file.

        :param file_name: The service file name
        """
        self._file_name = str(file_name)
        self.main_window.set_service_modified(self.is_modified(), self.short_file_name())
        Settings().setValue('servicemanager/last file', file_name)
        self._save_lite = self._file_name.endswith('.oszl')

    def file_name(self):
        """
        Return the current file name including path.
        """
        return self._file_name

    def short_file_name(self):
        """
        Return the current file name, excluding the path.
        """
        return split_filename(self._file_name)[1]

    def reset_supported_suffixes(self):
        """
        Resets the Suffixes list.

        """
        self.suffixes = []

    def supported_suffixes(self, suffix_list):
        """
        Adds Suffixes supported to the master list. Called from Plugins.

        :param suffix_list: New Suffix's to be supported
        """
        if isinstance(suffix_list, str):
            self.suffixes.append(suffix_list)
        else:
            for suffix in suffix_list:
                if suffix not in self.suffixes:
                    self.suffixes.append(suffix)

    def on_new_service_clicked(self, field=None):
        """
        Create a new service.
        :param field:
        """
        if self.is_modified():
            result = self.save_modified_service()
            if result == QtGui.QMessageBox.Cancel:
                return False
            elif result == QtGui.QMessageBox.Save:
                if not self.decide_save_method():
                    return False
        self.new_file()

    def on_load_service_clicked(self, load_file=None):
        """
        Loads the service file and saves the existing one it there is one unchanged.

        :param load_file: The service file to the loaded.  Will be None is from menu so selection will be required.
        """
        if self.is_modified():
            result = self.save_modified_service()
            if result == QtGui.QMessageBox.Cancel:
                return False
            elif result == QtGui.QMessageBox.Save:
                self.decide_save_method()
        if not load_file:
            file_name = QtGui.QFileDialog.getOpenFileName(
                self.main_window,
                translate('OpenLP.ServiceManager', 'Open File'),
                Settings().value(self.main_window.service_manager_settings_section + '/last directory'),
                translate('OpenLP.ServiceManager', 'OpenLP Service Files (*.osz *.oszl)')
            )
            if not file_name:
                return False
        else:
            file_name = load_file
        Settings().setValue(self.main_window.service_manager_settings_section + '/last directory',
                            split_filename(file_name)[0])
        self.load_file(file_name)

    def save_modified_service(self):
        """
        Check to see if a service needs to be saved.
        """
        return QtGui.QMessageBox.question(self.main_window,
                                          translate('OpenLP.ServiceManager', 'Modified Service'),
                                          translate('OpenLP.ServiceManager',
                                                    'The current service has been modified. Would you like to save '
                                                    'this service?'),
                                          QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard |
                                          QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Save)

    def on_recent_service_clicked(self, field=None):
        """
        Load a recent file as the service triggered by mainwindow recent service list.
        :param field:
        """
        sender = self.sender()
        self.load_file(sender.data())

    def new_file(self):
        """
        Create a blank new service file.
        """
        self.service_manager_list.clear()
        self.service_items = []
        self.set_file_name('')
        self.service_id += 1
        self.set_modified(False)
        Settings().setValue('servicemanager/last file', '')
        self.plugin_manager.new_service_created()

    def create_basic_service(self):
        """
        Create the initial service array with the base items to be saved.

        :return service array
        """
        service = []
        core = {'lite-service': self._save_lite,
                'service-theme': self.service_theme
                }
        service.append({'openlp_core': core})
        return service

    def save_file(self, field=None):
        """
        Save the current service file.

        A temporary file is created so that we don't overwrite the existing one and leave a mangled service file should
        there be an error when saving. Audio files are also copied into the service manager directory, and then packaged
        into the zip file.
        """
        if not self.file_name():
            return self.save_file_as()
        temp_file, temp_file_name = mkstemp('.osz', 'openlp_')
        # We don't need the file handle.
        os.close(temp_file)
        self.log_debug(temp_file_name)
        path_file_name = str(self.file_name())
        path, file_name = os.path.split(path_file_name)
        base_name = os.path.splitext(file_name)[0]
        service_file_name = '%s.osj' % base_name
        self.log_debug('ServiceManager.save_file - %s' % path_file_name)
        Settings().setValue(self.main_window.service_manager_settings_section + '/last directory', path)
        service = self.create_basic_service()
        write_list = []
        missing_list = []
        audio_files = []
        total_size = 0
        self.application.set_busy_cursor()
        # Number of items + 1 to zip it
        self.main_window.display_progress_bar(len(self.service_items) + 1)
        # Get list of missing files, and list of files to write
        for item in self.service_items:
            if not item['service_item'].uses_file():
                continue
            for frame in item['service_item'].get_frames():
                path_from = item['service_item'].get_frame_path(frame=frame)
                if path_from in write_list or path_from in missing_list:
                    continue
                if not os.path.exists(path_from):
                    missing_list.append(path_from)
                else:
                    write_list.append(path_from)
        if missing_list:
            self.application.set_normal_cursor()
            title = translate('OpenLP.ServiceManager', 'Service File(s) Missing')
            message = translate('OpenLP.ServiceManager',
                                'The following file(s) in the service are missing: %s\n\n'
                                'These files will be removed if you continue to save.') % "\n\t".join(missing_list)
            answer = QtGui.QMessageBox.critical(self, title, message,
                                                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok |
                                                                                  QtGui.QMessageBox.Cancel))
            if answer == QtGui.QMessageBox.Cancel:
                self.main_window.finished_progress_bar()
                return False
        # Check if item contains a missing file.
        for item in list(self.service_items):
            self.main_window.increment_progress_bar()
            item['service_item'].remove_invalid_frames(missing_list)
            if item['service_item'].missing_frames():
                self.service_items.remove(item)
            else:
                service_item = item['service_item'].get_service_repr(self._save_lite)
                if service_item['header']['background_audio']:
                    for i, file_name in enumerate(service_item['header']['background_audio']):
                        new_file = os.path.join('audio', item['service_item'].unique_identifier, file_name)
                        audio_files.append((file_name, new_file))
                        service_item['header']['background_audio'][i] = new_file
                # Add the service item to the service.
                service.append({'serviceitem': service_item})
        self.repaint_service_list(-1, -1)
        for file_item in write_list:
            file_size = os.path.getsize(file_item)
            total_size += file_size
        self.log_debug('ServiceManager.save_file - ZIP contents size is %i bytes' % total_size)
        service_content = json.dumps(service)
        # Usual Zip file cannot exceed 2GiB, file with Zip64 cannot be extracted using unzip in UNIX.
        allow_zip_64 = (total_size > 2147483648 + len(service_content))
        self.log_debug('ServiceManager.save_file - allowZip64 is %s' % allow_zip_64)
        zip_file = None
        success = True
        self.main_window.increment_progress_bar()
        try:
            zip_file = zipfile.ZipFile(temp_file_name, 'w', zipfile.ZIP_STORED, allow_zip_64)
            # First we add service contents..
            zip_file.writestr(service_file_name, service_content)
            # Finally add all the listed media files.
            for write_from in write_list:
                zip_file.write(write_from, write_from)
            for audio_from, audio_to in audio_files:
                if audio_from.startswith('audio'):
                    # When items are saved, they get new unique_identifier. Let's copy the file to the new location.
                    # Unused files can be ignored, OpenLP automatically cleans up the service manager dir on exit.
                    audio_from = os.path.join(self.service_path, audio_from)
                save_file = os.path.join(self.service_path, audio_to)
                save_path = os.path.split(save_file)[0]
                check_directory_exists(save_path)
                if not os.path.exists(save_file):
                    shutil.copy(audio_from, save_file)
                zip_file.write(audio_from, audio_to)
        except IOError:
            self.log_exception('Failed to save service to disk: %s' % temp_file_name)
            self.main_window.error_message(translate('OpenLP.ServiceManager', 'Error Saving File'),
                                           translate('OpenLP.ServiceManager', 'There was an error saving your file.'))
            success = False
        finally:
            if zip_file:
                zip_file.close()
        self.main_window.finished_progress_bar()
        self.application.set_normal_cursor()
        if success:
            try:
                shutil.copy(temp_file_name, path_file_name)
            except shutil.Error:
                return self.save_file_as()
            except OSError as ose:
                QtGui.QMessageBox.critical(self, translate('OpenLP.ServiceManager', 'Error Saving File'),
                                           translate('OpenLP.ServiceManager', 'An error occurred while writing the '
                                                     'service file: %s') % ose.strerror,
                                           QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))
                success = False
            self.main_window.add_recent_file(path_file_name)
            self.set_modified(False)
        delete_file(temp_file_name)
        return success

    def save_local_file(self):
        """
        Save the current service file but leave all the file references alone to point to the current machine.
        This format is not transportable as it will not contain any files.
        """
        if not self.file_name():
            return self.save_file_as()
        temp_file, temp_file_name = mkstemp('.oszl', 'openlp_')
        # We don't need the file handle.
        os.close(temp_file)
        self.log_debug(temp_file_name)
        path_file_name = str(self.file_name())
        path, file_name = os.path.split(path_file_name)
        base_name = os.path.splitext(file_name)[0]
        service_file_name = '%s.osj' % base_name
        self.log_debug('ServiceManager.save_file - %s' % path_file_name)
        Settings().setValue(self.main_window.service_manager_settings_section + '/last directory', path)
        service = self.create_basic_service()
        self.application.set_busy_cursor()
        # Number of items + 1 to zip it
        self.main_window.display_progress_bar(len(self.service_items) + 1)
        for item in self.service_items:
            self.main_window.increment_progress_bar()
            service_item = item['service_item'].get_service_repr(self._save_lite)
            # TODO: check for file item on save.
            service.append({'serviceitem': service_item})
            self.main_window.increment_progress_bar()
        service_content = json.dumps(service)
        zip_file = None
        success = True
        self.main_window.increment_progress_bar()
        try:
            zip_file = zipfile.ZipFile(temp_file_name, 'w', zipfile.ZIP_STORED, True)
            # First we add service contents.
            zip_file.writestr(service_file_name, service_content)
        except IOError:
            self.log_exception('Failed to save service to disk: %s', temp_file_name)
            self.main_window.error_message(translate('OpenLP.ServiceManager', 'Error Saving File'),
                                           translate('OpenLP.ServiceManager', 'There was an error saving your file.'))
            success = False
        finally:
            if zip_file:
                zip_file.close()
        self.main_window.finished_progress_bar()
        self.application.set_normal_cursor()
        if success:
            try:
                shutil.copy(temp_file_name, path_file_name)
            except shutil.Error:
                return self.save_file_as()
            self.main_window.add_recent_file(path_file_name)
            self.set_modified(False)
        delete_file(temp_file_name)
        return success

    def save_file_as(self, field=None):
        """
        Get a file name and then call :func:`ServiceManager.save_file` to save the file.
        """
        default_service_enabled = Settings().value('advanced/default service enabled')
        if default_service_enabled:
            service_day = Settings().value('advanced/default service day')
            if service_day == 7:
                local_time = datetime.now()
            else:
                service_hour = Settings().value('advanced/default service hour')
                service_minute = Settings().value('advanced/default service minute')
                now = datetime.now()
                day_delta = service_day - now.weekday()
                if day_delta < 0:
                    day_delta += 7
                time = now + timedelta(days=day_delta)
                local_time = time.replace(hour=service_hour, minute=service_minute)
            default_pattern = Settings().value('advanced/default service name')
            default_file_name = format_time(default_pattern, local_time)
        else:
            default_file_name = ''
        directory = Settings().value(self.main_window.service_manager_settings_section + '/last directory')
        path = os.path.join(directory, default_file_name)
        # SaveAs from osz to oszl is not valid as the files will be deleted on exit which is not sensible or usable in
        # the long term.
        if self._file_name.endswith('oszl') or self.service_has_all_original_files:
            file_name = QtGui.QFileDialog.getSaveFileName(self.main_window, UiStrings().SaveService, path,
                                                          translate('OpenLP.ServiceManager',
                                                                    'OpenLP Service Files (*.osz);; OpenLP Service '
                                                                    'Files - lite (*.oszl)'))
        else:
            file_name = QtGui.QFileDialog.getSaveFileName(self.main_window, UiStrings().SaveService, path,
                                                          translate('OpenLP.ServiceManager',
                                                                    'OpenLP Service Files (*.osz);;'))
        if not file_name:
            return False
        if os.path.splitext(file_name)[1] == '':
            file_name += '.osz'
        else:
            ext = os.path.splitext(file_name)[1]
            file_name.replace(ext, '.osz')
        self.set_file_name(file_name)
        self.decide_save_method()

    def decide_save_method(self, field=None):
        """
        Determine which type of save method to use.
        :param field:
        """
        if not self.file_name():
            return self.save_file_as()
        if self._save_lite:
            return self.save_local_file()
        else:
            return self.save_file()

    def load_file(self, file_name):
        """
        Load an existing service file
        :param file_name:
        """
        if not file_name:
            return False
        file_name = str(file_name)
        if not os.path.exists(file_name):
            return False
        zip_file = None
        file_to = None
        self.application.set_busy_cursor()
        try:
            zip_file = zipfile.ZipFile(file_name)
            for zip_info in zip_file.infolist():
                try:
                    ucs_file = zip_info.filename
                except UnicodeDecodeError:
                    self.log_exception('file_name "%s" is not valid UTF-8' % zip_info.file_name)
                    critical_error_message_box(message=translate('OpenLP.ServiceManager',
                                               'File is not a valid service.\n The content encoding is not UTF-8.'))
                    continue
                os_file = ucs_file.replace('/', os.path.sep)
                os_file = os.path.basename(os_file)
                self.log_debug('Extract file: %s' % os_file)
                zip_info.filename = os_file
                zip_file.extract(zip_info, self.service_path)
                if os_file.endswith('osj') or os_file.endswith('osd'):
                    p_file = os.path.join(self.service_path, os_file)
            if 'p_file' in locals():
                file_to = open(p_file, 'r')
                if p_file.endswith('osj'):
                    items = json.load(file_to)
                else:
                    critical_error_message_box(message=translate('OpenLP.ServiceManager',
                                                                 'The service file you are trying to open is in an old '
                                                                 'format.\n Please save it using OpenLP 2.0.2 or '
                                                                 'greater.'))
                    return
                file_to.close()
                self.new_file()
                self.set_file_name(file_name)
                self.main_window.display_progress_bar(len(items))
                self.process_service_items(items)
                delete_file(p_file)
                self.main_window.add_recent_file(file_name)
                self.set_modified(False)
                Settings().setValue('servicemanager/last file', file_name)
            else:
                critical_error_message_box(message=translate('OpenLP.ServiceManager', 'File is not a valid service.'))
                self.log_error('File contains no service data')
        except (IOError, NameError, zipfile.BadZipfile):
            self.log_exception('Problem loading service file %s' % file_name)
            critical_error_message_box(message=translate('OpenLP.ServiceManager',
                                       'File could not be opened because it is corrupt.'))
        except zipfile.BadZipfile:
            if os.path.getsize(file_name) == 0:
                self.log_exception('Service file is zero sized: %s' % file_name)
                QtGui.QMessageBox.information(self, translate('OpenLP.ServiceManager', 'Empty File'),
                                              translate('OpenLP.ServiceManager', 'This service file does not contain '
                                                                                 'any data.'))
            else:
                self.log_exception('Service file is cannot be extracted as zip: %s' % file_name)
                QtGui.QMessageBox.information(self, translate('OpenLP.ServiceManager', 'Corrupt File'),
                                              translate('OpenLP.ServiceManager',
                                                        'This file is either corrupt or it is not an OpenLP 2 service '
                                                        'file.'))
            self.application.set_normal_cursor()
            return
        finally:
            if file_to:
                file_to.close()
            if zip_file:
                zip_file.close()
        self.main_window.finished_progress_bar()
        self.application.set_normal_cursor()
        self.repaint_service_list(-1, -1)

    def process_service_items(self, service_items):
        """
        Process all the array of service items loaded from the saved service

        :param service_items: list of service_items
        """
        for item in service_items:
            self.main_window.increment_progress_bar()
            service_item = ServiceItem()
            if 'openlp_core' in item:
                item = item.get('openlp_core')
                theme = item.get('service-theme', None)
                if theme:
                    find_and_set_in_combo_box(self.theme_combo_box, theme, set_missing=False)
                    if theme == self.theme_combo_box.currentText():
                        self.renderer.set_service_theme(theme)
            else:
                if self._save_lite:
                    service_item.set_from_service(item)
                else:
                    service_item.set_from_service(item, self.service_path)
                service_item.validate_item(self.suffixes)
                if service_item.is_capable(ItemCapabilities.OnLoadUpdate):
                    new_item = Registry().get(service_item.name).service_load(service_item)
                    if new_item:
                        service_item = new_item
                self.add_service_item(service_item, repaint=False)

    def load_last_file(self):
        """
        Load the last service item from the service manager when the service was last closed. Can be blank if there was
        no service present.
        """
        file_name = Settings().value('servicemanager/last file')
        if file_name:
            self.load_file(file_name)

    def context_menu(self, point):
        """
        The Right click context menu from the Serviceitem list

        :param point: The location of the cursor.
        """
        item = self.service_manager_list.itemAt(point)
        if item is None:
            return
        if item.parent():
            pos = item.parent().data(0, QtCore.Qt.UserRole)
        else:
            pos = item.data(0, QtCore.Qt.UserRole)
        service_item = self.service_items[pos - 1]
        self.edit_action.setVisible(False)
        self.rename_action.setVisible(False)
        self.create_custom_action.setVisible(False)
        self.maintain_action.setVisible(False)
        self.notes_action.setVisible(False)
        self.time_action.setVisible(False)
        self.auto_start_action.setVisible(False)
        if service_item['service_item'].is_capable(ItemCapabilities.CanEdit) and service_item['service_item'].edit_id:
            self.edit_action.setVisible(True)
        if service_item['service_item'].is_capable(ItemCapabilities.CanEditTitle):
            self.rename_action.setVisible(True)
        if service_item['service_item'].is_capable(ItemCapabilities.CanMaintain):
            self.maintain_action.setVisible(True)
        if item.parent() is None:
            self.notes_action.setVisible(True)
        if service_item['service_item'].is_capable(ItemCapabilities.CanLoop) and  \
                len(service_item['service_item'].get_frames()) > 1:
            self.auto_play_slides_menu.menuAction().setVisible(True)
            self.auto_play_slides_once.setChecked(service_item['service_item'].auto_play_slides_once)
            self.auto_play_slides_loop.setChecked(service_item['service_item'].auto_play_slides_loop)
            self.timed_slide_interval.setChecked(service_item['service_item'].timed_slide_interval > 0)
            if service_item['service_item'].timed_slide_interval > 0:
                delay_suffix = ' %s s' % str(service_item['service_item'].timed_slide_interval)
            else:
                delay_suffix = ' ...'
            self.timed_slide_interval.setText(
                translate('OpenLP.ServiceManager', '&Delay between slides') + delay_suffix)
            # TODO for future: make group explains itself more visually
        else:
            self.auto_play_slides_menu.menuAction().setVisible(False)
        if service_item['service_item'].is_capable(ItemCapabilities.HasVariableStartTime) and \
                not service_item['service_item'].is_capable(ItemCapabilities.IsOptical):
            self.time_action.setVisible(True)
        if service_item['service_item'].is_capable(ItemCapabilities.CanAutoStartForLive):
            self.auto_start_action.setVisible(True)
            self.auto_start_action.setIcon(self.inactive)
            self.auto_start_action.setText(translate('OpenLP.ServiceManager', '&Auto Start - inactive'))
            if service_item['service_item'].will_auto_start:
                self.auto_start_action.setText(translate('OpenLP.ServiceManager', '&Auto Start - active'))
                self.auto_start_action.setIcon(self.active)
        if service_item['service_item'].is_text():
            for plugin in self.plugin_manager.plugins:
                if plugin.name == 'custom' and plugin.status == PluginStatus.Active:
                    self.create_custom_action.setVisible(True)
                    break
        self.theme_menu.menuAction().setVisible(False)
        # Set up the theme menu.
        if service_item['service_item'].is_text() and self.renderer.theme_level == ThemeLevel.Song:
            self.theme_menu.menuAction().setVisible(True)
            # The service item does not have a theme, check the "Default".
            if service_item['service_item'].theme is None:
                theme_action = self.theme_menu.defaultAction()
            else:
                theme_action = self.theme_menu.findChild(QtGui.QAction, service_item['service_item'].theme)
            if theme_action is not None:
                theme_action.setChecked(True)
        self.menu.exec_(self.service_manager_list.mapToGlobal(point))

    def on_service_item_note_form(self, field=None):
        """
        Allow the service note to be edited
        :param field:
        """
        item = self.find_service_item()[0]
        self.service_note_form.text_edit.setPlainText(self.service_items[item]['service_item'].notes)
        if self.service_note_form.exec_():
            self.service_items[item]['service_item'].notes = self.service_note_form.text_edit.toPlainText()
            self.repaint_service_list(item, -1)
            self.set_modified()

    def on_start_time_form(self, field=None):
        """
        Opens a dialog to type in service item notes.
        :param field:
        """
        item = self.find_service_item()[0]
        self.start_time_form.item = self.service_items[item]
        if self.start_time_form.exec_():
            self.repaint_service_list(item, -1)

    def toggle_auto_play_slides_once(self, field=None):
        """
        Toggle Auto play slide once. Inverts auto play once option for the item

        :param field:
        """
        item = self.find_service_item()[0]
        service_item = self.service_items[item]['service_item']
        service_item.auto_play_slides_once = not service_item.auto_play_slides_once
        if service_item.auto_play_slides_once:
            service_item.auto_play_slides_loop = False
            self.auto_play_slides_loop.setChecked(False)
        if service_item.auto_play_slides_once and service_item.timed_slide_interval == 0:
            service_item.timed_slide_interval = Settings().value(
                self.main_window.general_settings_section + '/loop delay')
        self.set_modified()

    def toggle_auto_play_slides_loop(self, field=None):
        """
        Toggle Auto play slide loop.

        :param field:
        """
        item = self.find_service_item()[0]
        service_item = self.service_items[item]['service_item']
        service_item.auto_play_slides_loop = not service_item.auto_play_slides_loop
        if service_item.auto_play_slides_loop:
            service_item.auto_play_slides_once = False
            self.auto_play_slides_once.setChecked(False)
        if service_item.auto_play_slides_loop and service_item.timed_slide_interval == 0:
            service_item.timed_slide_interval = Settings().value(
                self.main_window.general_settings_section + '/loop delay')
        self.set_modified()

    def on_timed_slide_interval(self, field=None):
        """
        Shows input dialog for enter interval in seconds for delay
        :param field:
        """
        item = self.find_service_item()[0]
        service_item = self.service_items[item]['service_item']
        if service_item.timed_slide_interval == 0:
            timed_slide_interval = Settings().value(self.main_window.general_settings_section + '/loop delay')
        else:
            timed_slide_interval = service_item.timed_slide_interval
        timed_slide_interval, ok = QtGui.QInputDialog.getInteger(self, translate('OpenLP.ServiceManager',
                                                                 'Input delay'),
                                                                 translate('OpenLP.ServiceManager',
                                                                           'Delay between slides in seconds.'),
                                                                 timed_slide_interval, 0, 180, 1)
        if ok:
            service_item.timed_slide_interval = timed_slide_interval
        if service_item.timed_slide_interval != 0 and not service_item.auto_play_slides_loop \
                and not service_item.auto_play_slides_once:
            service_item.auto_play_slides_loop = True
        elif service_item.timed_slide_interval == 0:
            service_item.auto_play_slides_loop = False
            service_item.auto_play_slides_once = False
        self.set_modified()

    def on_auto_start(self, field=None):
        """
        Toggles to Auto Start Setting.
        """
        item = self.find_service_item()[0]
        self.service_items[item]['service_item'].will_auto_start = \
            not self.service_items[item]['service_item'].will_auto_start

    def on_service_item_edit_form(self, field=None):
        """
        Opens a dialog to edit the service item and update the service display if changes are saved.
        :param field:
        """
        item = self.find_service_item()[0]
        self.service_item_edit_form.set_service_item(self.service_items[item]['service_item'])
        if self.service_item_edit_form.exec_():
            self.add_service_item(self.service_item_edit_form.get_service_item(),
                                  replace=True, expand=self.service_items[item]['expanded'])

    def preview_live(self, unique_identifier, row):
        """
        Called by the SlideController to request a preview item be made live and allows the next preview to be updated
        if relevant.

        :param unique_identifier: Reference to the service_item
        :param row: individual row number
        """
        for sitem in self.service_items:
            if sitem['service_item'].unique_identifier == unique_identifier:
                item = self.service_manager_list.topLevelItem(sitem['order'] - 1)
                self.service_manager_list.setCurrentItem(item)
                self.make_live(int(row))
                return

    def next_item(self):
        """
        Called by the SlideController to select the next service item.
        """
        if not self.service_manager_list.selectedItems():
            return
        selected = self.service_manager_list.selectedItems()[0]
        look_for = 0
        service_iterator = QtGui.QTreeWidgetItemIterator(self.service_manager_list)
        while service_iterator.value():
            if look_for == 1 and service_iterator.value().parent() is None:
                self.service_manager_list.setCurrentItem(service_iterator.value())
                self.make_live()
                return
            if service_iterator.value() == selected:
                look_for = 1
            service_iterator += 1

    def previous_item(self, last_slide=False):
        """
        Called by the SlideController to select the previous service item.

        :param last_slide: Is this the last slide in the service_item.
        """
        if not self.service_manager_list.selectedItems():
            return
        selected = self.service_manager_list.selectedItems()[0]
        prev_item = None
        prev_item_last_slide = None
        service_iterator = QtGui.QTreeWidgetItemIterator(self.service_manager_list)
        while service_iterator.value():
            if service_iterator.value() == selected:
                if last_slide and prev_item_last_slide:
                    pos = prev_item.data(0, QtCore.Qt.UserRole)
                    check_expanded = self.service_items[pos - 1]['expanded']
                    self.service_manager_list.setCurrentItem(prev_item_last_slide)
                    if not check_expanded:
                        self.service_manager_list.collapseItem(prev_item)
                    self.make_live()
                    self.service_manager_list.setCurrentItem(prev_item)
                elif prev_item:
                    self.service_manager_list.setCurrentItem(prev_item)
                    self.make_live()
                return
            if service_iterator.value().parent() is None:
                prev_item = service_iterator.value()
            if service_iterator.value().parent() is prev_item:
                prev_item_last_slide = service_iterator.value()
            service_iterator += 1

    def on_set_item(self, message, field=None):
        """
        Called by a signal to select a specific item and make it live usually from remote.

        :param field:
        :param message: The data passed in from a remove message
        """
        self.log_debug(message)
        self.set_item(int(message))

    def set_item(self, index):
        """
        Makes a specific item in the service live.

        :param index: The index of the service item list to be actioned.
        """
        if 0 <= index < self.service_manager_list.topLevelItemCount():
            item = self.service_manager_list.topLevelItem(index)
            self.service_manager_list.setCurrentItem(item)
            self.make_live()

    def on_move_selection_up(self):
        """
        Moves the cursor selection up the window. Called by the up arrow.
        """
        item = self.service_manager_list.currentItem()
        item_before = self.service_manager_list.itemAbove(item)
        if item_before is None:
            return
        self.service_manager_list.setCurrentItem(item_before)

    def on_move_selection_down(self):
        """
        Moves the cursor selection down the window. Called by the down arrow.
        """
        item = self.service_manager_list.currentItem()
        item_after = self.service_manager_list.itemBelow(item)
        if item_after is None:
            return
        self.service_manager_list.setCurrentItem(item_after)

    def on_collapse_all(self, field=None):
        """
        Collapse all the service items.
        :param field:
        """
        for item in self.service_items:
            item['expanded'] = False
        self.service_manager_list.collapseAll()

    def collapsed(self, item):
        """
        Record if an item is collapsed. Used when repainting the list to get the correct state.

        :param item: The service item to be checked
        """
        pos = item.data(0, QtCore.Qt.UserRole)
        self.service_items[pos - 1]['expanded'] = False

    def on_expand_all(self, field=None):
        """
        Collapse all the service items.
        :param field:
        """
        for item in self.service_items:
            item['expanded'] = True
        self.service_manager_list.expandAll()

    def expanded(self, item):
        """
        Record if an item is collapsed. Used when repainting the list to get the correct state.

        :param item: The service item to be checked
        """
        pos = item.data(0, QtCore.Qt.UserRole)
        self.service_items[pos - 1]['expanded'] = True

    def on_service_top(self, field=None):
        """
        Move the current ServiceItem to the top of the list.
        :param field:
        """
        item, child = self.find_service_item()
        if item < len(self.service_items) and item != -1:
            temp = self.service_items[item]
            self.service_items.remove(self.service_items[item])
            self.service_items.insert(0, temp)
            self.repaint_service_list(0, child)
            self.set_modified()

    def on_service_up(self, field=None):
        """
        Move the current ServiceItem one position up in the list.
        :param field:
        """
        item, child = self.find_service_item()
        if item > 0:
            temp = self.service_items[item]
            self.service_items.remove(self.service_items[item])
            self.service_items.insert(item - 1, temp)
            self.repaint_service_list(item - 1, child)
            self.set_modified()

    def on_service_down(self, field=None):
        """
        Move the current ServiceItem one position down in the list.
        :param field:
        """
        item, child = self.find_service_item()
        if item < len(self.service_items) and item != -1:
            temp = self.service_items[item]
            self.service_items.remove(self.service_items[item])
            self.service_items.insert(item + 1, temp)
            self.repaint_service_list(item + 1, child)
            self.set_modified()

    def on_service_end(self, field=None):
        """
        Move the current ServiceItem to the bottom of the list.
        :param field:
        """
        item, child = self.find_service_item()
        if item < len(self.service_items) and item != -1:
            temp = self.service_items[item]
            self.service_items.remove(self.service_items[item])
            self.service_items.insert(len(self.service_items), temp)
            self.repaint_service_list(len(self.service_items) - 1, child)
            self.set_modified()

    def on_delete_from_service(self, field=None):
        """
        Remove the current ServiceItem from the list.
        :param field:
        """
        item = self.find_service_item()[0]
        if item != -1:
            self.service_items.remove(self.service_items[item])
            self.repaint_service_list(item - 1, -1)
            self.set_modified()

    def repaint_service_list(self, service_item, service_item_child):
        """
        Clear the existing service list and prepaint all the items. This is used when moving items as the move takes
        place in a supporting list, and when regenerating all the items due to theme changes.

        :param service_item: The item which changed. (int)
        :param service_item_child: The child of the ``service_item``, which will be selected. (int)
        """
        # Correct order of items in array
        count = 1
        self.service_has_all_original_files = True
        for item in self.service_items:
            item['order'] = count
            count += 1
            if not item['service_item'].has_original_files:
                self.service_has_all_original_files = False
        # Repaint the screen
        self.service_manager_list.clear()
        self.service_manager_list.clearSelection()
        for item_count, item in enumerate(self.service_items):
            service_item_from_item = item['service_item']
            tree_widget_item = QtGui.QTreeWidgetItem(self.service_manager_list)
            if service_item_from_item.is_valid:
                if service_item_from_item.notes:
                    icon = QtGui.QImage(service_item_from_item.icon)
                    icon = icon.scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                    overlay = QtGui.QImage(':/services/service_item_notes.png')
                    overlay = overlay.scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                    painter = QtGui.QPainter(icon)
                    painter.drawImage(0, 0, overlay)
                    painter.end()
                    tree_widget_item.setIcon(0, build_icon(icon))
                elif service_item_from_item.temporary_edit:
                    icon = QtGui.QImage(service_item_from_item.icon)
                    icon = icon.scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                    overlay = QtGui.QImage(':/general/general_export.png')
                    overlay = overlay.scaled(40, 40, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                    painter = QtGui.QPainter(icon)
                    painter.drawImage(40, 0, overlay)
                    painter.end()
                    tree_widget_item.setIcon(0, build_icon(icon))
                else:
                    tree_widget_item.setIcon(0, service_item_from_item.iconic_representation)
            else:
                tree_widget_item.setIcon(0, build_icon(':/general/general_delete.png'))
            tree_widget_item.setText(0, service_item_from_item.get_display_title())
            tips = []
            if service_item_from_item.temporary_edit:
                tips.append('<strong>%s:</strong> <em>%s</em>' % (translate('OpenLP.ServiceManager', 'Edit'),
                            (translate('OpenLP.ServiceManager', 'Service copy only'))))
            if service_item_from_item.theme and service_item_from_item.theme != -1:
                tips.append('<strong>%s:</strong> <em>%s</em>' %
                            (translate('OpenLP.ServiceManager', 'Slide theme'), service_item_from_item.theme))
            if service_item_from_item.notes:
                tips.append('<strong>%s: </strong> %s' %
                            (translate('OpenLP.ServiceManager', 'Notes'), html.escape(service_item_from_item.notes)))
            if item['service_item'].is_capable(ItemCapabilities.HasVariableStartTime):
                tips.append(item['service_item'].get_media_time())
            tree_widget_item.setToolTip(0, '<br>'.join(tips))
            tree_widget_item.setData(0, QtCore.Qt.UserRole, item['order'])
            tree_widget_item.setSelected(item['selected'])
            # Add the children to their parent tree_widget_item.
            for count, frame in enumerate(service_item_from_item.get_frames()):
                child = QtGui.QTreeWidgetItem(tree_widget_item)
                # prefer to use a display_title
                if service_item_from_item.is_capable(ItemCapabilities.HasDisplayTitle):
                    text = frame['display_title'].replace('\n', ' ')
                else:
                    text = frame['title'].replace('\n', ' ')
                child.setText(0, text[:40])
                child.setData(0, QtCore.Qt.UserRole, count)
                if service_item == item_count:
                    if item['expanded'] and service_item_child == count:
                        self.service_manager_list.setCurrentItem(child)
                    elif service_item_child == -1:
                        self.service_manager_list.setCurrentItem(tree_widget_item)
            tree_widget_item.setExpanded(item['expanded'])

    def clean_up(self):
        """
        Empties the service_path of temporary files on system exit.
        """
        for file_name in os.listdir(self.service_path):
            file_path = os.path.join(self.service_path, file_name)
            delete_file(file_path)
        if os.path.exists(os.path.join(self.service_path, 'audio')):
            shutil.rmtree(os.path.join(self.service_path, 'audio'), True)

    def on_theme_combo_box_selected(self, current_index):
        """
        Set the theme for the current service.

        :param current_index: The combo box index for the selected item
        """
        self.service_theme = self.theme_combo_box.currentText()
        self.renderer.set_service_theme(self.service_theme)
        Settings().setValue(self.main_window.service_manager_settings_section + '/service theme', self.service_theme)
        self.regenerate_service_items(True)

    def theme_change(self):
        """
        The theme may have changed in the settings dialog so make sure the theme combo box is in the correct state.
        """
        visible = self.renderer.theme_level == ThemeLevel.Global
        self.theme_label.setVisible(visible)
        self.theme_combo_box.setVisible(visible)

    def regenerate_service_items(self, changed=False):
        """
        Rebuild the service list as things have changed and a repaint is the easiest way to do this.

        :param changed: True if the list has changed for new / removed items. False for a theme change.
        """
        self.application.set_busy_cursor()
        # force reset of renderer as theme data has changed
        self.service_has_all_original_files = True
        if self.service_items:
            for item in self.service_items:
                item['selected'] = False
            service_iterator = QtGui.QTreeWidgetItemIterator(self.service_manager_list)
            selected_item = None
            while service_iterator.value():
                if service_iterator.value().isSelected():
                    selected_item = service_iterator.value()
                service_iterator += 1
            if selected_item is not None:
                if selected_item.parent() is None:
                    pos = selected_item.data(0, QtCore.Qt.UserRole)
                else:
                    pos = selected_item.parent().data(0, QtCore.Qt.UserRole)
                self.service_items[pos - 1]['selected'] = True
            temp_service_items = self.service_items
            self.service_manager_list.clear()
            self.service_items = []
            self.is_new = True
            for item in temp_service_items:
                self.add_service_item(item['service_item'], False, expand=item['expanded'], repaint=False,
                                      selected=item['selected'])
            # Set to False as items may have changed rendering does not impact the saved song so True may also be valid
            if changed:
                self.set_modified()
            # Repaint it once only at the end
            self.repaint_service_list(-1, -1)
        self.application.set_normal_cursor()

    def replace_service_item(self, new_item):
        """
        Using the service item passed replace the one with the same edit id if found.

        :param new_item: a new service item to up date an existing one.
        """
        for item_count, item in enumerate(self.service_items):
            if item['service_item'].edit_id == new_item.edit_id and item['service_item'].name == new_item.name:
                new_item.render()
                new_item.merge(item['service_item'])
                item['service_item'] = new_item
                self.repaint_service_list(item_count + 1, 0)
                self.live_controller.replace_service_manager_item(new_item)
                self.set_modified()

    def add_service_item(self, item, rebuild=False, expand=None, replace=False, repaint=True, selected=False,
                         position=-1):
        """
        Add a Service item to the list

        :param item: Service Item to be added
        :param rebuild: Do we need to rebuild the live display (Default False)
        :param expand: Override the default expand settings. (Tristate)
        :param replace: Is the service item a replacement (Default False)
        :param repaint: Do we need to repaint the service item list (Default True)
        :param selected: Has the item been selected (Default False)
        :param position: The position where the item is dropped (Default -1)
        """
        # if not passed set to config value
        if expand is None:
            expand = Settings().value('advanced/expand service item')
        item.from_service = True
        if position != -1:
            self.drop_position = position
        if replace:
            s_item, child = self.find_service_item()
            item.merge(self.service_items[s_item]['service_item'])
            self.service_items[s_item]['service_item'] = item
            self.repaint_service_list(s_item, child)
            self.live_controller.replace_service_manager_item(item)
        else:
            item.render()
            # nothing selected for dnd
            if self.drop_position == -1:
                if isinstance(item, list):
                    for ind_item in item:
                        self.service_items.append({'service_item': ind_item,
                                                   'order': len(self.service_items) + 1,
                                                   'expanded': expand, 'selected': selected})
                else:
                    self.service_items.append({'service_item': item,
                                               'order': len(self.service_items) + 1,
                                               'expanded': expand, 'selected': selected})
                if repaint:
                    self.repaint_service_list(len(self.service_items) - 1, -1)
            else:
                self.service_items.insert(self.drop_position,
                                          {'service_item': item, 'order': self.drop_position,
                                           'expanded': expand, 'selected': selected})
                self.repaint_service_list(self.drop_position, -1)
            # if rebuilding list make sure live is fixed.
            if rebuild:
                self.live_controller.replace_service_manager_item(item)
        self.drop_position = -1
        self.set_modified()

    def make_preview(self, field=None):
        """
        Send the current item to the Preview slide controller
        :param field:
        """
        self.application.set_busy_cursor()
        item, child = self.find_service_item()
        if self.service_items[item]['service_item'].is_valid:
            self.preview_controller.add_service_manager_item(self.service_items[item]['service_item'], child)
        else:
            critical_error_message_box(translate('OpenLP.ServiceManager', 'Missing Display Handler'),
                                       translate('OpenLP.ServiceManager',
                                                 'Your item cannot be displayed as there is no handler to display it'))
        self.application.set_normal_cursor()

    def get_service_item(self):
        """
        Send the current item to the Preview slide controller
        """
        item = self.find_service_item()[0]
        if item == -1:
            return False
        else:
            return self.service_items[item]['service_item']

    def on_make_live(self, field=None):
        """
        Send the current item to the Live slide controller but triggered by a tablewidget click event.
        :param field:
        """
        self.make_live()

    def make_live(self, row=-1):
        """
        Send the current item to the Live slide controller

        :param row: Row number to be displayed if from preview. -1 is passed if the value is not set
        """
        item, child = self.find_service_item()
        # No items in service
        if item == -1:
            return
        if row != -1:
            child = row
        self.application.set_busy_cursor()
        if self.service_items[item]['service_item'].is_valid:
            self.live_controller.add_service_manager_item(self.service_items[item]['service_item'], child)
            if Settings().value(self.main_window.general_settings_section + '/auto preview'):
                item += 1
                if self.service_items and item < len(self.service_items) and \
                        self.service_items[item]['service_item'].is_capable(ItemCapabilities.CanPreview):
                    self.preview_controller.add_service_manager_item(self.service_items[item]['service_item'], 0)
                    self.live_controller.preview_widget.setFocus()
        else:
            critical_error_message_box(translate('OpenLP.ServiceManager', 'Missing Display Handler'),
                                       translate('OpenLP.ServiceManager',
                                                 'Your item cannot be displayed as the plugin required to display it '
                                                 'is missing or inactive'))
        self.application.set_normal_cursor()

    def remote_edit(self, field=None):
        """
        Triggers a remote edit to a plugin to allow item to be edited.
        :param field:
        """
        item = self.find_service_item()[0]
        if self.service_items[item]['service_item'].is_capable(ItemCapabilities.CanEdit):
            new_item = Registry().get(self.service_items[item]['service_item'].name). \
                on_remote_edit(self.service_items[item]['service_item'].edit_id)
            if new_item:
                self.add_service_item(new_item, replace=True)

    def on_service_item_rename(self, field=None):
        """
        Opens a dialog to rename the service item.

        :param field: Not used, but PyQt needs this.
        """
        item = self.find_service_item()[0]
        if not self.service_items[item]['service_item'].is_capable(ItemCapabilities.CanEditTitle):
            return
        title = self.service_items[item]['service_item'].title
        title, ok = QtGui.QInputDialog.getText(self, translate('OpenLP.ServiceManager', 'Rename item title'),
                                               translate('OpenLP.ServiceManager', 'Title:'),
                                               QtGui.QLineEdit.Normal, self.trUtf8(title))
        if ok:
            self.service_items[item]['service_item'].title = title
            self.repaint_service_list(item, -1)
            self.set_modified()

    def create_custom(self, field=None):
        """
        Saves the current text item as a custom slide
        :param field:
        """
        item = self.find_service_item()[0]
        Registry().execute('custom_create_from_service', self.service_items[item]['service_item'])

    def find_service_item(self):
        """
        Finds the first selected ServiceItem in the list and returns the position of the service_item_from_item and its
        selected child item. For example, if the third child item (in the Slidecontroller known as slide) in the
        second service item is selected this will return::

            (1, 2)
        """
        items = self.service_manager_list.selectedItems()
        service_item = -1
        service_item_child = -1
        for item in items:
            parent_item = item.parent()
            if parent_item is None:
                service_item = item.data(0, QtCore.Qt.UserRole)
            else:
                service_item = parent_item.data(0, QtCore.Qt.UserRole)
                service_item_child = item.data(0, QtCore.Qt.UserRole)
            # Adjust for zero based arrays.
            service_item -= 1
            # Only process the first item on the list for this method.
            break
        return service_item, service_item_child

    def drop_event(self, event):
        """
        Receive drop event and trigger an internal event to get the plugins to build and push the correct service item.
        The drag event payload carries the plugin name

        :param event: Handle of the event passed
        """
        link = event.mimeData()
        if link.hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            for url in link.urls():
                file_name = url.toLocalFile()
                if file_name.endswith('.osz'):
                    self.on_load_service_clicked(file_name)
                elif file_name.endswith('.oszl'):
                    # todo correct
                    self.on_load_service_clicked(file_name)
        elif link.hasText():
            plugin = link.text()
            item = self.service_manager_list.itemAt(event.pos())
            # ServiceManager started the drag and drop
            if plugin == 'ServiceManager':
                start_pos, child = self.find_service_item()
                # If no items selected
                if start_pos == -1:
                    return
                if item is None:
                    end_pos = len(self.service_items)
                else:
                    end_pos = self._get_parent_item_data(item) - 1
                service_item = self.service_items[start_pos]
                self.service_items.remove(service_item)
                self.service_items.insert(end_pos, service_item)
                self.repaint_service_list(end_pos, child)
                self.set_modified()
            else:
                # we are not over anything so drop
                replace = False
                if item is None:
                    self.drop_position = len(self.service_items)
                else:
                    # we are over something so lets investigate
                    pos = self._get_parent_item_data(item) - 1
                    service_item = self.service_items[pos]
                    if (plugin == service_item['service_item'].name and
                            service_item['service_item'].is_capable(ItemCapabilities.CanAppend)):
                        action = self.dnd_menu.exec_(QtGui.QCursor.pos())
                        # New action required
                        if action == self.new_action:
                            self.drop_position = self._get_parent_item_data(item)
                        # Append to existing action
                        if action == self.add_to_action:
                            self.drop_position = self._get_parent_item_data(item)
                            item.setSelected(True)
                            replace = True
                    else:
                        self.drop_position = self._get_parent_item_data(item) - 1
                Registry().execute('%s_add_service_item' % plugin, replace)

    def update_theme_list(self, theme_list):
        """
        Called from ThemeManager when the Themes have changed

        :param theme_list: A list of current themes to be displayed
        """
        self.theme_combo_box.clear()
        self.theme_menu.clear()
        self.theme_combo_box.addItem('')
        theme_group = QtGui.QActionGroup(self.theme_menu)
        theme_group.setExclusive(True)
        theme_group.setObjectName('theme_group')
        # Create a "Default" theme, which allows the user to reset the item's theme to the service theme or global
        # theme.
        default_theme = create_widget_action(self.theme_menu, text=UiStrings().Default, checked=False,
                                             triggers=self.on_theme_change_action)
        self.theme_menu.setDefaultAction(default_theme)
        theme_group.addAction(default_theme)
        self.theme_menu.addSeparator()
        for theme in theme_list:
            self.theme_combo_box.addItem(theme)
            theme_group.addAction(create_widget_action(self.theme_menu, theme, text=theme, checked=False,
                                  triggers=self.on_theme_change_action))
        find_and_set_in_combo_box(self.theme_combo_box, self.service_theme)
        self.renderer.set_service_theme(self.service_theme)
        self.regenerate_service_items()

    def on_theme_change_action(self, field=None):
        """
        Handles theme change events

        :param field:
        """
        theme = self.sender().objectName()
        # No object name means that the "Default" theme is supposed to be used.
        if not theme:
            theme = None
        item = self.find_service_item()[0]
        self.service_items[item]['service_item'].update_theme(theme)
        self.regenerate_service_items(True)

    def _get_parent_item_data(self, item):
        """
        Finds and returns the parent item for any item

        :param item: The service item list item to be checked.
        """
        parent_item = item.parent()
        if parent_item is None:
            return item.data(0, QtCore.Qt.UserRole)
        else:
            return parent_item.data(0, QtCore.Qt.UserRole)

    def print_service_order(self, field=None):
        """
        Print a Service Order Sheet.
        """
        setting_dialog = PrintServiceForm()
        setting_dialog.exec_()

    def get_drop_position(self):
        """
        Getter for drop_position. Used in: MediaManagerItem
        """
        return self.drop_position
