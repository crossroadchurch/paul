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
The Loop Manager manages adding, running and deleting of looped video backgrounds.
"""
import os, glob, shutil, subprocess

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, RegistryProperties, AppLocation, Settings, OpenLPMixin, RegistryMixin, \
    check_directory_exists, UiStrings, translate
from openlp.core.lib import FileDialog, OpenLPToolbar, build_icon, check_item_selected
from openlp.core.lib.ui import critical_error_message_box, create_widget_action
from openlp.core.ui import FileRenameForm
from openlp.core.utils import get_locale_key, split_filename


class Ui_LoopManager(object):
    """
    UI part of the Loop Manager
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
        self.add_toolbar_action = self.toolbar.add_toolbar_action('add_loop',
                                                                  text=translate('OpenLP.LoopManager',
                                                                                 'Add Loop'),
                                                                  icon=':/general/general_add.png',
                                                                  tooltip=translate('OpenLP.LoopManager',
                                                                                    'Add a loop.'),
                                                                  triggers=self.on_add_loop)
        self.delete_toolbar_action = self.toolbar.add_toolbar_action('delete_loop',
                                                                     text=translate('OpenLP.LoopManager',
                                                                                    'Delete Loop'),
                                                                     icon=':/general/general_delete.png',
                                                                     tooltip=translate('OpenLP.LoopManager',
                                                                                       'Delete a loop.'),
                                                                     triggers=self.on_delete_loop)
        self.toolbar.addSeparator()
        self.play_toolbar_action = self.toolbar.add_toolbar_action('play_loop',
                                                                    text=translate('OpenLP.LoopManager',
                                                                                   'Play Loop'),
                                                                    icon=':/slides/media_playback_start.png',
                                                                    tooltip=translate('OpenLP.LoopManager',
                                                                                      'Play a loop.'),
                                                                    triggers=self.on_display_loop)
        self.stop_toolbar_action = self.toolbar.add_toolbar_action('stop_loop',
                                                                   text=translate('OpenLP.LoopManager',
                                                                                  'Stop Active Loop'),
                                                                   icon=':/slides/media_playback_stop.png',
                                                                   tooltip=translate('OpenLP.LoopManager',
                                                                                     'Stop playback of active loop.'),
                                                                   triggers=self.on_stop_loop)
        self.layout.addWidget(self.toolbar)
        self.loop_widget = QtGui.QWidgetAction(self.toolbar)
        self.loop_widget.setObjectName('loop_widget')
        # create loop manager list
        self.loop_list_widget = QtGui.QListWidget(widget)
        self.loop_list_widget.setAlternatingRowColors(True)
        self.loop_list_widget.setIconSize(QtCore.QSize(88, 50))
        self.loop_list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.loop_list_widget.setObjectName('loop_list_widget')
        self.layout.addWidget(self.loop_list_widget)
        self.loop_list_widget.customContextMenuRequested.connect(self.context_menu)
        # build the context menu
        self.menu = QtGui.QMenu()
        self.rename_action = create_widget_action(self.menu,
                                                  text=translate('OpenLP.LoopManager', '&Rename Loop'),
                                                  icon=':/general/general_edit.png', triggers=self.on_rename_loop)
        self.delete_action = create_widget_action(self.menu,
                                                  text=translate('OpenLP.LoopManager', '&Delete Loop'),
                                                  icon=':/general/general_delete.png', triggers=self.on_delete_loop)
        self.menu.addSeparator()
        self.display_action = create_widget_action(self.menu,
                                                   text=translate('OpenLP.LoopManager', 'Dis&play Loop'),
                                                   icon=':/slides/media_playback_start.png', triggers=self.on_display_loop)

        # Signals
        self.loop_list_widget.doubleClicked.connect(self.on_display_loop)


class LoopManager(OpenLPMixin, RegistryMixin, QtGui.QWidget, Ui_LoopManager, RegistryProperties):
    """
    Manages the Loops and allows them to be executed.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(LoopManager, self).__init__(parent)
        self.settings_section = 'loops'
        # Variables
        self.loop_list = []


    def bootstrap_initialise(self):
        """
        Process the bootstrap initialise setup request
        """
        self.setup_ui(self)
        self.build_loop_path()


    def bootstrap_post_set_up(self):
        """
        Process the bootstrap post setup request
        """
        self.load_loops()
        self.file_rename_form = FileRenameForm()
        self.on_new_prompt = translate('OpenLP.LoopManager', 'Select Video Loop')
        self.on_new_file_masks = translate('OpenLP.LoopManager', 'Videos (%s);;%s (*)') % (
            ' '.join(self.media_controller.video_extensions_list), UiStrings().AllFiles)


    def build_loop_path(self):
        """
        Set up the loop path variables
        """
        self.path = AppLocation.get_section_data_path(self.settings_section)
        check_directory_exists(self.path)
        self.thumb_path = os.path.join(self.path, 'thumbnails')
        check_directory_exists(self.thumb_path)


    def context_menu(self, point):
        """
        Build the Right Click Context menu

        :param point: The position of the mouse so the correct item can be found.
        """
        item = self.loop_list_widget.itemAt(point)
        if item is None:
            return
        self.menu.exec_(self.loop_list_widget.mapToGlobal(point))


    def on_add_loop(self, field=None):
        """
        Adds a new video background loop and creates the associated thumbnail image for the UI.
        :param field:
        """
        files = FileDialog.getOpenFileNames(self, self.on_new_prompt,
                                            Settings().value(self.settings_section + '/last directory'),
                                            self.on_new_file_masks)
        if files:
            Settings().setValue(self.settings_section + '/last directory', split_filename(files[0])[0])
            for f in files:
                self.application.set_busy_cursor()
                shutil.copy(f, self.path)
                self.create_loop_thumbnail(split_filename(f)[1])
                self.application.set_normal_cursor()
        self.load_loops()


    def create_loop_thumbnail(self, loop_file):
        """
        Creates a thumbnail for the specified video loop, which is already in self.path
        :param loop_file: Video file (inc extension), relative to self.path
        """
        vlc_cmd = ['vlc', os.path.join(self.path, loop_file), '--rate=1', '--scene-prefix=' + os.path.splitext(loop_file)[0],
                   '--video-filter=scene', '--vout=dummy', '--aout=dummy', '--start-time=1', '--stop-time=2',
                   '--scene-replace', '--scene-format=jpg', '--scene-path=' + self.thumb_path,
                   '--width=88', '--height=50', '--intf=dummy', 'vlc://quit']
        ret_code = subprocess.call(vlc_cmd)
        return True


    def on_rename_loop(self, field=None):
        """
        Renames an existing loop to a new name
        :param field:
        """
        item = self.loop_list_widget.currentItem()
        old_loop_name = os.path.splitext(item.data(QtCore.Qt.UserRole))[0]
        old_loop_ext = os.path.splitext(item.data(QtCore.Qt.UserRole))[1]
        self.file_rename_form.file_name_edit.setText(old_loop_name)
        if self.file_rename_form.exec_():
            new_loop_name = self.file_rename_form.file_name_edit.text()
            if old_loop_name == new_loop_name:
                return
            if self.check_if_loop_exists(new_loop_name) == False:
                os.rename(os.path.join(self.path, old_loop_name + old_loop_ext),
                          os.path.join(self.path, new_loop_name + old_loop_ext))
                os.rename(os.path.join(self.thumb_path, old_loop_name + '.jpg'),
                          os.path.join(self.thumb_path, new_loop_name + '.jpg'))
            self.load_loops()


    def on_delete_loop(self, field=None):
        """
        Delete a loop triggered by the UI.
        :param field:
        """
        if check_item_selected(self.loop_list_widget,
                               translate('OpenLP.LoopManager', 'You must select a loop to delete.')):
            item = self.loop_list_widget.currentItem()
            cur_loop = item.text()
            check_answer = QtGui.QMessageBox.question(self, translate('OpenLP.LoopManager', 'Delete Confirmation'),
                                                      translate('OpenLP.LoopManager', 'Remove %s loop and delete files?' % cur_loop),
                                                      QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No),
                                                      QtGui.QMessageBox.No)
            if check_answer == QtGui.QMessageBox.No:
                return

            # Remove loop from UI
            row = self.loop_list_widget.row(item)
            self.loop_list_widget.takeItem(row)

            # Remove loop and thumbnail from disk
            self.application.set_busy_cursor()
            os.remove(os.path.join(self.path, item.data(QtCore.Qt.UserRole)))
            os.remove(os.path.join(self.thumb_path, cur_loop + '.jpg'))
            self.application.set_normal_cursor()


    def on_display_loop(self, field=None):
        if check_item_selected(self.loop_list_widget,
                               translate('OpenLP.LoopManager', 'You must select a loop to play.')):
            item = self.loop_list_widget.currentItem()
            loop_file = os.path.join(self.path, item.data(QtCore.Qt.UserRole))
            vlc_cmd = ['vlc', loop_file, '--one-instance', '--repeat', '-f']
            subprocess.Popen(vlc_cmd)
            # Update GUI to show currently playing loop_thumb
            #f = item.font
            #QtGui.QFont.setBold(True)
            #item.setFont(f)
            #item.setBackgroundColor(QtGui.QColor(0,255,0,255))
            return True


    def on_stop_loop(self, field=None):
        vlc_cmd = ['vlc', '--one-instance', '-f', 'vlc://quit']
        subprocess.Popen(vlc_cmd)
        return True


    def load_loops(self):
        """
        Loads all loops into the plugin
        """
        self.loop_list = []
        self.loop_list_widget.clear()
        files = AppLocation.get_files(self.settings_section)
        # Sort the loops by name, language specific
        files.sort(key=lambda file_name: get_locale_key(str(file_name)))
        # now process the file list of loop
        for name in files:
            if os.path.isfile(os.path.join(self.path, name)):
                # check to see loop has corresponding thumbnail
                loop_thumb = os.path.join(self.thumb_path, os.path.splitext(name)[0] + '.jpg')
                if os.path.exists(loop_thumb) == False:
                    self.create_loop_thumbnail(name)
                loop_name = os.path.splitext(name)[0]
                item_name = QtGui.QListWidgetItem(loop_name)
                icon = build_icon(loop_thumb)
                item_name.setIcon(icon)
                item_name.setData(QtCore.Qt.UserRole, name)
                self.loop_list_widget.addItem(item_name)
                self.loop_list.append(loop_name)


    def check_if_loop_exists(self, loop_name):
        """
        Check if loop already exists and displays error message

        :param loop_name:  Name of the Loop to test
        :return True if loop exists, False otherwise
        """
        if len(glob.glob(os.path.join(self.path, loop_name) + '*')) > 0:
            critical_error_message_box(
                translate('OpenLP.LoopManager', 'Validation Error'),
                translate('OpenLP.LoopManager', 'A loop with this name already exists.'))
            return True
        return False
