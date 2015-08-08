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
This is the main window, where all the action happens.
"""
import logging
import os
import sys
import shutil
from distutils import dir_util
from distutils.errors import DistutilsFileError
from tempfile import gettempdir
import time
from datetime import datetime

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, RegistryProperties, AppLocation, Settings, check_directory_exists, translate, \
    is_win, is_macosx
from openlp.core.lib import Renderer, OpenLPDockWidget, PluginManager, ImageManager, PluginStatus, ScreenList, \
    build_icon
from openlp.core.lib.ui import UiStrings, create_action
from openlp.core.ui import AboutForm, SettingsForm, ServiceManager, ThemeManager, LiveController, PluginForm, \
    MediaDockManager, ShortcutListForm, FormattingTagForm, PreviewController

from openlp.core.ui.media import MediaController
from openlp.core.utils import LanguageManager, add_actions, get_application_version
from openlp.core.utils.actions import ActionList, CategoryOrder
from openlp.core.ui.firsttimeform import FirstTimeForm
from openlp.core.ui.projector.manager import ProjectorManager

log = logging.getLogger(__name__)

MEDIA_MANAGER_STYLE = """
QToolBox {
    padding-bottom: 2px;
}
QToolBox::tab {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 palette(button), stop: 1.0 palette(mid));
    border: 1px solid palette(mid);
    border-radius: 3px;
}
QToolBox::tab:selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 palette(light), stop: 1.0 palette(button));
    border: 1px solid palette(mid);
    font-weight: bold;
}
"""

PROGRESSBAR_STYLE = """
QProgressBar{
    height: 10px;
}
"""


class Ui_MainWindow(object):
    """
    This is the UI part of the main window.
    """
    def setupUi(self, main_window):
        """
        Set up the user interface
        """
        main_window.setObjectName('MainWindow')
        main_window.setWindowIcon(build_icon(':/icon/openlp-logo.svg'))
        main_window.setDockNestingEnabled(True)
        if is_macosx():
            main_window.setDocumentMode(True)
        # Set up the main container, which contains all the other form widgets.
        self.main_content = QtGui.QWidget(main_window)
        self.main_content.setObjectName('main_content')
        self.main_content_layout = QtGui.QHBoxLayout(self.main_content)
        self.main_content_layout.setSpacing(0)
        self.main_content_layout.setMargin(0)
        self.main_content_layout.setObjectName('main_content_layout')
        main_window.setCentralWidget(self.main_content)
        self.control_splitter = QtGui.QSplitter(self.main_content)
        self.control_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.control_splitter.setObjectName('control_splitter')
        self.main_content_layout.addWidget(self.control_splitter)
        # Create slide controllers
        PreviewController(self)
        LiveController(self)
        preview_visible = Settings().value('user interface/preview panel')
        live_visible = Settings().value('user interface/live panel')
        panel_locked = Settings().value('user interface/lock panel')
        # Create menu
        self.menu_bar = QtGui.QMenuBar(main_window)
        self.menu_bar.setObjectName('menu_bar')
        self.file_menu = QtGui.QMenu(self.menu_bar)
        self.file_menu.setObjectName('fileMenu')
        self.recent_files_menu = QtGui.QMenu(self.file_menu)
        self.recent_files_menu.setObjectName('recentFilesMenu')
        self.file_import_menu = QtGui.QMenu(self.file_menu)
        if not is_macosx():
            self.file_import_menu.setIcon(build_icon(u':/general/general_import.png'))
        self.file_import_menu.setObjectName('file_import_menu')
        self.file_export_menu = QtGui.QMenu(self.file_menu)
        if not is_macosx():
            self.file_export_menu.setIcon(build_icon(u':/general/general_export.png'))
        self.file_export_menu.setObjectName('file_export_menu')
        # View Menu
        self.view_menu = QtGui.QMenu(self.menu_bar)
        self.view_menu.setObjectName('viewMenu')
        self.view_mode_menu = QtGui.QMenu(self.view_menu)
        self.view_mode_menu.setObjectName('viewModeMenu')
        # Tools Menu
        self.tools_menu = QtGui.QMenu(self.menu_bar)
        self.tools_menu.setObjectName('tools_menu')
        # Settings Menu
        self.settings_menu = QtGui.QMenu(self.menu_bar)
        self.settings_menu.setObjectName('settingsMenu')
        self.settings_language_menu = QtGui.QMenu(self.settings_menu)
        self.settings_language_menu.setObjectName('settingsLanguageMenu')
        # Help Menu
        self.help_menu = QtGui.QMenu(self.menu_bar)
        self.help_menu.setObjectName('helpMenu')
        main_window.setMenuBar(self.menu_bar)
        self.status_bar = QtGui.QStatusBar(main_window)
        self.status_bar.setObjectName('status_bar')
        main_window.setStatusBar(self.status_bar)
        self.load_progress_bar = QtGui.QProgressBar(self.status_bar)
        self.load_progress_bar.setObjectName('load_progress_bar')
        self.status_bar.addPermanentWidget(self.load_progress_bar)
        self.load_progress_bar.hide()
        self.load_progress_bar.setValue(0)
        self.load_progress_bar.setStyleSheet(PROGRESSBAR_STYLE)
        self.default_theme_label = QtGui.QLabel(self.status_bar)
        self.default_theme_label.setObjectName('default_theme_label')
        self.status_bar.addPermanentWidget(self.default_theme_label)
        # Create the MediaManager
        self.media_manager_dock = OpenLPDockWidget(main_window, 'media_manager_dock',
                                                   ':/system/system_mediamanager.png')
        self.media_manager_dock.setStyleSheet(MEDIA_MANAGER_STYLE)
        # Create the media toolbox
        self.media_tool_box = QtGui.QToolBox(self.media_manager_dock)
        self.media_tool_box.setObjectName('media_tool_box')
        self.media_manager_dock.setWidget(self.media_tool_box)
        main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.media_manager_dock)
        # Create the service manager
        self.service_manager_dock = OpenLPDockWidget(main_window, 'service_manager_dock',
                                                     ':/system/system_servicemanager.png')
        self.service_manager_contents = ServiceManager(self.service_manager_dock)
        self.service_manager_dock.setWidget(self.service_manager_contents)
        main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.service_manager_dock)
        # Create the theme manager
        self.theme_manager_dock = OpenLPDockWidget(main_window, 'theme_manager_dock',
                                                   ':/system/system_thememanager.png')
        self.theme_manager_contents = ThemeManager(self.theme_manager_dock)
        self.theme_manager_contents.setObjectName('theme_manager_contents')
        self.theme_manager_dock.setWidget(self.theme_manager_contents)
        main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.theme_manager_dock)
        # Create the projector manager
        self.projector_manager_dock = OpenLPDockWidget(parent=main_window,
                                                       name='projector_manager_dock',
                                                       icon=':/projector/projector_manager.png')
        self.projector_manager_contents = ProjectorManager(self.projector_manager_dock)
        self.projector_manager_contents.setObjectName('projector_manager_contents')
        self.projector_manager_dock.setWidget(self.projector_manager_contents)
        main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.projector_manager_dock)
        # Create the menu items
        action_list = ActionList.get_instance()
        action_list.add_category(UiStrings().File, CategoryOrder.standard_menu)
        self.file_new_item = create_action(main_window, 'fileNewItem', icon=':/general/general_new.png',
                                           can_shortcuts=True, category=UiStrings().File,
                                           triggers=self.service_manager_contents.on_new_service_clicked)
        self.file_open_item = create_action(main_window, 'fileOpenItem', icon=':/general/general_open.png',
                                            can_shortcuts=True, category=UiStrings().File,
                                            triggers=self.service_manager_contents.on_load_service_clicked)
        self.file_save_item = create_action(main_window, 'fileSaveItem', icon=':/general/general_save.png',
                                            can_shortcuts=True, category=UiStrings().File,
                                            triggers=self.service_manager_contents.save_file)
        self.file_save_as_item = create_action(main_window, 'fileSaveAsItem', can_shortcuts=True,
                                               category=UiStrings().File,
                                               triggers=self.service_manager_contents.save_file_as)
        self.print_service_order_item = create_action(main_window, 'printServiceItem', can_shortcuts=True,
                                                      category=UiStrings().File,
                                                      triggers=self.service_manager_contents.print_service_order)
        self.file_exit_item = create_action(main_window, 'fileExitItem', icon=':/system/system_exit.png',
                                            can_shortcuts=True,
                                            category=UiStrings().File, triggers=main_window.close)
        # Give QT Extra Hint that this is the Exit Menu Item
        self.file_exit_item.setMenuRole(QtGui.QAction.QuitRole)
        action_list.add_category(UiStrings().Import, CategoryOrder.standard_menu)
        self.import_theme_item = create_action(main_window, 'importThemeItem', category=UiStrings().Import,
                                               can_shortcuts=True)
        self.import_language_item = create_action(main_window, 'importLanguageItem')
        action_list.add_category(UiStrings().Export, CategoryOrder.standard_menu)
        self.export_theme_item = create_action(main_window, 'exportThemeItem', category=UiStrings().Export,
                                               can_shortcuts=True)
        self.export_language_item = create_action(main_window, 'exportLanguageItem')
        action_list.add_category(UiStrings().View, CategoryOrder.standard_menu)
        # Projector items
        self.import_projector_item = create_action(main_window, 'importProjectorItem', category=UiStrings().Import,
                                                   can_shortcuts=False)
        action_list.add_category(UiStrings().Import, CategoryOrder.standard_menu)
        self.view_projector_manager_item = create_action(main_window, 'viewProjectorManagerItem',
                                                         icon=':/projector/projector_manager.png',
                                                         checked=self.projector_manager_dock.isVisible(),
                                                         can_shortcuts=True,
                                                         category=UiStrings().View,
                                                         triggers=self.toggle_projector_manager)
        self.view_media_manager_item = create_action(main_window, 'viewMediaManagerItem',
                                                     icon=':/system/system_mediamanager.png',
                                                     checked=self.media_manager_dock.isVisible(),
                                                     can_shortcuts=True,
                                                     category=UiStrings().View, triggers=self.toggle_media_manager)
        self.view_theme_manager_item = create_action(main_window, 'viewThemeManagerItem', can_shortcuts=True,
                                                     icon=':/system/system_thememanager.png',
                                                     checked=self.theme_manager_dock.isVisible(),
                                                     category=UiStrings().View, triggers=self.toggle_theme_manager)
        self.view_service_manager_item = create_action(main_window, 'viewServiceManagerItem', can_shortcuts=True,
                                                       icon=':/system/system_servicemanager.png',
                                                       checked=self.service_manager_dock.isVisible(),
                                                       category=UiStrings().View, triggers=self.toggle_service_manager)
        self.view_preview_panel = create_action(main_window, 'viewPreviewPanel', can_shortcuts=True,
                                                checked=preview_visible, category=UiStrings().View,
                                                triggers=self.set_preview_panel_visibility)
        self.view_live_panel = create_action(main_window, 'viewLivePanel', can_shortcuts=True, checked=live_visible,
                                             category=UiStrings().View, triggers=self.set_live_panel_visibility)
        self.lock_panel = create_action(main_window, 'lockPanel', can_shortcuts=True, checked=panel_locked,
                                        category=UiStrings().View, triggers=self.set_lock_panel)
        action_list.add_category(UiStrings().ViewMode, CategoryOrder.standard_menu)
        self.mode_default_item = create_action(
            main_window, 'modeDefaultItem', checked=False, category=UiStrings().ViewMode, can_shortcuts=True)
        self.mode_setup_item = create_action(main_window, 'modeSetupItem', checked=False, category=UiStrings().ViewMode,
                                             can_shortcuts=True)
        self.mode_live_item = create_action(main_window, 'modeLiveItem', checked=True, category=UiStrings().ViewMode,
                                            can_shortcuts=True)
        self.mode_group = QtGui.QActionGroup(main_window)
        self.mode_group.addAction(self.mode_default_item)
        self.mode_group.addAction(self.mode_setup_item)
        self.mode_group.addAction(self.mode_live_item)
        self.mode_default_item.setChecked(True)
        action_list.add_category(UiStrings().Tools, CategoryOrder.standard_menu)
        self.tools_add_tool_item = create_action(main_window,
                                                 'toolsAddToolItem', icon=':/tools/tools_add.png',
                                                 category=UiStrings().Tools, can_shortcuts=True)
        self.tools_open_data_folder = create_action(main_window,
                                                    'toolsOpenDataFolder', icon=':/general/general_open.png',
                                                    category=UiStrings().Tools, can_shortcuts=True)
        self.tools_first_time_wizard = create_action(main_window,
                                                     'toolsFirstTimeWizard', icon=':/general/general_revert.png',
                                                     category=UiStrings().Tools, can_shortcuts=True)
        self.update_theme_images = create_action(main_window,
                                                 'updateThemeImages', category=UiStrings().Tools, can_shortcuts=True)
        action_list.add_category(UiStrings().Settings, CategoryOrder.standard_menu)
        self.settings_plugin_list_item = create_action(main_window,
                                                       'settingsPluginListItem',
                                                       icon=':/system/settings_plugin_list.png',
                                                       can_shortcuts=True,
                                                       category=UiStrings().Settings,
                                                       triggers=self.on_plugin_item_clicked)
        # i18n Language Items
        self.auto_language_item = create_action(main_window, 'autoLanguageItem', checked=LanguageManager.auto_language)
        self.language_group = QtGui.QActionGroup(main_window)
        self.language_group.setExclusive(True)
        self.language_group.setObjectName('languageGroup')
        add_actions(self.language_group, [self.auto_language_item])
        qm_list = LanguageManager.get_qm_list()
        saved_language = LanguageManager.get_language()
        for key in sorted(qm_list.keys()):
            language_item = create_action(main_window, key, checked=qm_list[key] == saved_language)
            add_actions(self.language_group, [language_item])
        self.settings_shortcuts_item = create_action(main_window, 'settingsShortcutsItem',
                                                     icon=':/system/system_configure_shortcuts.png',
                                                     category=UiStrings().Settings, can_shortcuts=True)
        # Formatting Tags were also known as display tags.
        self.formatting_tag_item = create_action(main_window, 'displayTagItem',
                                                 icon=':/system/tag_editor.png', category=UiStrings().Settings,
                                                 can_shortcuts=True)
        self.settings_configure_item = create_action(main_window, 'settingsConfigureItem',
                                                     icon=':/system/system_settings.png', can_shortcuts=True,
                                                     category=UiStrings().Settings)
        # Give QT Extra Hint that this is the Preferences Menu Item
        self.settings_configure_item.setMenuRole(QtGui.QAction.PreferencesRole)
        self.settings_import_item = create_action(main_window, 'settingsImportItem',
                                                  category=UiStrings().Import, can_shortcuts=True)
        self.settings_export_item = create_action(main_window, 'settingsExportItem',
                                                  category=UiStrings().Export, can_shortcuts=True)
        action_list.add_category(UiStrings().Help, CategoryOrder.standard_menu)
        self.about_item = create_action(main_window, 'aboutItem', icon=':/system/system_about.png',
                                        can_shortcuts=True, category=UiStrings().Help,
                                        triggers=self.on_about_item_clicked)
        # Give QT Extra Hint that this is an About Menu Item
        self.about_item.setMenuRole(QtGui.QAction.AboutRole)
        if is_win():
            self.local_help_file = os.path.join(AppLocation.get_directory(AppLocation.AppDir), 'OpenLP.chm')
            self.offline_help_item = create_action(main_window, 'offlineHelpItem',
                                                   icon=':/system/system_help_contents.png',
                                                   can_shortcuts=True,
                                                   category=UiStrings().Help, triggers=self.on_offline_help_clicked)
        self.on_line_help_item = create_action(main_window, 'onlineHelpItem',
                                               icon=':/system/system_online_help.png',
                                               can_shortcuts=True,
                                               category=UiStrings().Help, triggers=self.on_online_help_clicked)
        self.web_site_item = create_action(main_window, 'webSiteItem', can_shortcuts=True, category=UiStrings().Help)
        # Shortcuts not connected to buttons or menu entries.
        self.search_shortcut_action = create_action(main_window,
                                                    'searchShortcut', can_shortcuts=True,
                                                    category=translate('OpenLP.MainWindow', 'General'),
                                                    triggers=self.on_search_shortcut_triggered)
        '''
        Leave until the import projector options are finished
        add_actions(self.file_import_menu, (self.settings_import_item, self.import_theme_item,
                    self.import_projector_item, self.import_language_item, None))
        '''
        add_actions(self.file_import_menu, (self.settings_import_item, self.import_theme_item,
                    self.import_language_item, None))
        add_actions(self.file_export_menu, (self.settings_export_item, self.export_theme_item,
                    self.export_language_item, None))
        add_actions(self.file_menu, (self.file_new_item, self.file_open_item,
                    self.file_save_item, self.file_save_as_item, self.recent_files_menu.menuAction(), None,
                    self.file_import_menu.menuAction(), self.file_export_menu.menuAction(), None,
                    self.print_service_order_item, self.file_exit_item))
        add_actions(self.view_mode_menu, (self.mode_default_item, self.mode_setup_item, self.mode_live_item))
        add_actions(self.view_menu, (self.view_mode_menu.menuAction(), None, self.view_media_manager_item,
                    self.view_projector_manager_item, self.view_service_manager_item, self.view_theme_manager_item,
                    None, self.view_preview_panel, self.view_live_panel, None, self.lock_panel))
        # i18n add Language Actions
        add_actions(self.settings_language_menu, (self.auto_language_item, None))
        add_actions(self.settings_language_menu, self.language_group.actions())
        # Qt on OS X looks for keywords in the menu items title to determine which menu items get added to the main
        # menu. If we are running on Mac OS X the menu items whose title contains those keywords but don't belong in the
        # main menu need to be marked as such with QAction.NoRole.
        if is_macosx():
            self.settings_shortcuts_item.setMenuRole(QtGui.QAction.NoRole)
            self.formatting_tag_item.setMenuRole(QtGui.QAction.NoRole)
        add_actions(self.settings_menu, (self.settings_plugin_list_item, self.settings_language_menu.menuAction(),
                    None, self.formatting_tag_item, self.settings_shortcuts_item, self.settings_configure_item))
        add_actions(self.tools_menu, (self.tools_add_tool_item, None))
        add_actions(self.tools_menu, (self.tools_open_data_folder, None))
        add_actions(self.tools_menu, (self.tools_first_time_wizard, None))
        add_actions(self.tools_menu, [self.update_theme_images])
        if is_win():
            add_actions(self.help_menu, (self.offline_help_item, self.on_line_help_item, None, self.web_site_item,
                        self.about_item))
        else:
            add_actions(self.help_menu, (self.on_line_help_item, None, self.web_site_item, self.about_item))
        add_actions(self.menu_bar, (self.file_menu.menuAction(), self.view_menu.menuAction(),
                    self.tools_menu.menuAction(), self.settings_menu.menuAction(), self.help_menu.menuAction()))
        add_actions(self, [self.search_shortcut_action])
        # Initialise the translation
        self.retranslateUi(main_window)
        self.media_tool_box.setCurrentIndex(0)
        # Connect up some signals and slots
        self.file_menu.aboutToShow.connect(self.update_recent_files_menu)
        # Hide the entry, as it does not have any functionality yet.
        self.tools_add_tool_item.setVisible(False)
        self.import_language_item.setVisible(False)
        self.export_language_item.setVisible(False)
        self.set_lock_panel(panel_locked)
        self.settings_imported = False

    def retranslateUi(self, main_window):
        """
        Set up the translation system
        """
        main_window.setWindowTitle(UiStrings().OLPV2x)
        self.file_menu.setTitle(translate('OpenLP.MainWindow', '&File'))
        self.file_import_menu.setTitle(translate('OpenLP.MainWindow', '&Import'))
        self.file_export_menu.setTitle(translate('OpenLP.MainWindow', '&Export'))
        self.recent_files_menu.setTitle(translate('OpenLP.MainWindow', '&Recent Files'))
        self.view_menu.setTitle(translate('OpenLP.MainWindow', '&View'))
        self.view_mode_menu.setTitle(translate('OpenLP.MainWindow', 'M&ode'))
        self.tools_menu.setTitle(translate('OpenLP.MainWindow', '&Tools'))
        self.settings_menu.setTitle(translate('OpenLP.MainWindow', '&Settings'))
        self.settings_language_menu.setTitle(translate('OpenLP.MainWindow', '&Language'))
        self.help_menu.setTitle(translate('OpenLP.MainWindow', '&Help'))
        self.media_manager_dock.setWindowTitle(translate('OpenLP.MainWindow', 'Library'))
        self.service_manager_dock.setWindowTitle(translate('OpenLP.MainWindow', 'Service Manager'))
        self.theme_manager_dock.setWindowTitle(translate('OpenLP.MainWindow', 'Theme Manager'))
        self.projector_manager_dock.setWindowTitle(translate('OpenLP.MainWindow', 'Projector Manager'))
        self.file_new_item.setText(translate('OpenLP.MainWindow', '&New'))
        self.file_new_item.setToolTip(UiStrings().NewService)
        self.file_new_item.setStatusTip(UiStrings().CreateService)
        self.file_open_item.setText(translate('OpenLP.MainWindow', '&Open'))
        self.file_open_item.setToolTip(UiStrings().OpenService)
        self.file_open_item.setStatusTip(translate('OpenLP.MainWindow', 'Open an existing service.'))
        self.file_save_item.setText(translate('OpenLP.MainWindow', '&Save'))
        self.file_save_item.setToolTip(UiStrings().SaveService)
        self.file_save_item.setStatusTip(translate('OpenLP.MainWindow', 'Save the current service to disk.'))
        self.file_save_as_item.setText(translate('OpenLP.MainWindow', 'Save &As...'))
        self.file_save_as_item.setToolTip(translate('OpenLP.MainWindow', 'Save Service As'))
        self.file_save_as_item.setStatusTip(translate('OpenLP.MainWindow',
                                            'Save the current service under a new name.'))
        self.print_service_order_item.setText(UiStrings().PrintService)
        self.print_service_order_item.setStatusTip(translate('OpenLP.MainWindow', 'Print the current service.'))
        self.file_exit_item.setText(translate('OpenLP.MainWindow', 'E&xit'))
        self.file_exit_item.setStatusTip(translate('OpenLP.MainWindow', 'Quit OpenLP'))
        self.import_theme_item.setText(translate('OpenLP.MainWindow', '&Theme'))
        self.import_language_item.setText(translate('OpenLP.MainWindow', '&Language'))
        self.export_theme_item.setText(translate('OpenLP.MainWindow', '&Theme'))
        self.export_language_item.setText(translate('OpenLP.MainWindow', '&Language'))
        self.settings_shortcuts_item.setText(translate('OpenLP.MainWindow', 'Configure &Shortcuts...'))
        self.formatting_tag_item.setText(translate('OpenLP.MainWindow', 'Configure &Formatting Tags...'))
        self.settings_configure_item.setText(translate('OpenLP.MainWindow', '&Configure OpenLP...'))
        self.settings_export_item.setStatusTip(
            translate('OpenLP.MainWindow', 'Export OpenLP settings to a specified *.config file'))
        self.settings_export_item.setText(translate('OpenLP.MainWindow', 'Settings'))
        self.settings_import_item.setStatusTip(
            translate('OpenLP.MainWindow', 'Import OpenLP settings from a specified *.config file previously '
                                           'exported on this or another machine'))
        self.settings_import_item.setText(translate('OpenLP.MainWindow', 'Settings'))
        self.view_projector_manager_item.setText(translate('OPenLP.MainWindow', '&Projector Manager'))
        self.view_projector_manager_item.setToolTip(translate('OpenLP.MainWindow', 'Toggle Projector Manager'))
        self.view_projector_manager_item.setStatusTip(translate('OpenLP.MainWindow',
                                                                'Toggle the visibility of the Projector Manager'))
        self.view_media_manager_item.setText(translate('OpenLP.MainWindow', '&Media Manager'))
        self.view_media_manager_item.setToolTip(translate('OpenLP.MainWindow', 'Toggle Media Manager'))
        self.view_media_manager_item.setStatusTip(translate('OpenLP.MainWindow',
                                                  'Toggle the visibility of the media manager.'))
        self.view_theme_manager_item.setText(translate('OpenLP.MainWindow', '&Theme Manager'))
        self.view_theme_manager_item.setToolTip(translate('OpenLP.MainWindow', 'Toggle Theme Manager'))
        self.view_theme_manager_item.setStatusTip(translate('OpenLP.MainWindow',
                                                  'Toggle the visibility of the theme manager.'))
        self.view_service_manager_item.setText(translate('OpenLP.MainWindow', '&Service Manager'))
        self.view_service_manager_item.setToolTip(translate('OpenLP.MainWindow', 'Toggle Service Manager'))
        self.view_service_manager_item.setStatusTip(translate('OpenLP.MainWindow',
                                                    'Toggle the visibility of the service manager.'))
        self.view_preview_panel.setText(translate('OpenLP.MainWindow', '&Preview Panel'))
        self.view_preview_panel.setToolTip(translate('OpenLP.MainWindow', 'Toggle Preview Panel'))
        self.view_preview_panel.setStatusTip(
            translate('OpenLP.MainWindow', 'Toggle the visibility of the preview panel.'))
        self.view_live_panel.setText(translate('OpenLP.MainWindow', '&Live Panel'))
        self.view_live_panel.setToolTip(translate('OpenLP.MainWindow', 'Toggle Live Panel'))
        self.lock_panel.setText(translate('OpenLP.MainWindow', 'L&ock Panels'))
        self.lock_panel.setStatusTip(translate('OpenLP.MainWindow', 'Prevent the panels being moved.'))
        self.view_live_panel.setStatusTip(translate('OpenLP.MainWindow', 'Toggle the visibility of the live panel.'))
        self.settings_plugin_list_item.setText(translate('OpenLP.MainWindow', '&Plugin List'))
        self.settings_plugin_list_item.setStatusTip(translate('OpenLP.MainWindow', 'List the Plugins'))
        self.about_item.setText(translate('OpenLP.MainWindow', '&About'))
        self.about_item.setStatusTip(translate('OpenLP.MainWindow', 'More information about OpenLP'))
        if is_win():
            self.offline_help_item.setText(translate('OpenLP.MainWindow', '&User Guide'))
        self.on_line_help_item.setText(translate('OpenLP.MainWindow', '&Online Help'))
        self.search_shortcut_action.setText(UiStrings().Search)
        self.search_shortcut_action.setToolTip(
            translate('OpenLP.MainWindow', 'Jump to the search box of the current active plugin.'))
        self.web_site_item.setText(translate('OpenLP.MainWindow', '&Web Site'))
        for item in self.language_group.actions():
            item.setText(item.objectName())
            item.setStatusTip(translate('OpenLP.MainWindow', 'Set the interface language to %s') % item.objectName())
        self.auto_language_item.setText(translate('OpenLP.MainWindow', '&Autodetect'))
        self.auto_language_item.setStatusTip(translate('OpenLP.MainWindow', 'Use the system language, if available.'))
        self.tools_add_tool_item.setText(translate('OpenLP.MainWindow', 'Add &Tool...'))
        self.tools_add_tool_item.setStatusTip(translate('OpenLP.MainWindow',
                                                        'Add an application to the list of tools.'))
        self.tools_open_data_folder.setText(translate('OpenLP.MainWindow', 'Open &Data Folder...'))
        self.tools_open_data_folder.setStatusTip(translate('OpenLP.MainWindow',
                                                 'Open the folder where songs, bibles and other data resides.'))
        self.tools_first_time_wizard.setText(translate('OpenLP.MainWindow', 'Re-run First Time Wizard'))
        self.tools_first_time_wizard.setStatusTip(translate('OpenLP.MainWindow',
                                                  'Re-run the First Time Wizard, importing songs, Bibles and themes.'))
        self.update_theme_images.setText(translate('OpenLP.MainWindow', 'Update Theme Images'))
        self.update_theme_images.setStatusTip(translate('OpenLP.MainWindow',
                                                        'Update the preview images for all themes.'))
        self.mode_default_item.setText(translate('OpenLP.MainWindow', '&Default'))
        self.mode_default_item.setStatusTip(translate('OpenLP.MainWindow', 'Set the view mode back to the default.'))
        self.mode_setup_item.setText(translate('OpenLP.MainWindow', '&Setup'))
        self.mode_setup_item.setStatusTip(translate('OpenLP.MainWindow', 'Set the view mode to Setup.'))
        self.mode_live_item.setText(translate('OpenLP.MainWindow', '&Live'))
        self.mode_live_item.setStatusTip(translate('OpenLP.MainWindow', 'Set the view mode to Live.'))


class MainWindow(QtGui.QMainWindow, Ui_MainWindow, RegistryProperties):
    """
    The main window.
    """
    log.info('MainWindow loaded')

    def __init__(self):
        """
        This constructor sets up the interface, the various managers, and the plugins.
        """
        super(MainWindow, self).__init__()
        Registry().register('main_window', self)
        self.clipboard = self.application.clipboard()
        self.arguments = self.application.args
        # Set up settings sections for the main application (not for use by plugins).
        self.ui_settings_section = 'user interface'
        self.general_settings_section = 'core'
        self.advanced_settings_section = 'advanced'
        self.shortcuts_settings_section = 'shortcuts'
        self.service_manager_settings_section = 'servicemanager'
        self.songs_settings_section = 'songs'
        self.themes_settings_section = 'themes'
        self.projector_settings_section = 'projector'
        self.players_settings_section = 'players'
        self.display_tags_section = 'displayTags'
        self.header_section = 'SettingsImport'
        self.recent_files = []
        self.timer_id = 0
        self.new_data_path = None
        self.copy_data = False
        Settings().set_up_default_values()
        self.about_form = AboutForm(self)
        MediaController()
        SettingsForm(self)
        self.formatting_tag_form = FormattingTagForm(self)
        self.shortcut_form = ShortcutListForm(self)
        # Set up the path with plugins
        PluginManager(self)
        ImageManager()
        Renderer()
        # Set up the interface
        self.setupUi(self)
        # Define the media Dock Manager
        self.media_dock_manager = MediaDockManager(self.media_tool_box)
        # Load settings after setupUi so default UI sizes are overwritten
        # Once settings are loaded update the menu with the recent files.
        self.update_recent_files_menu()
        self.plugin_form = PluginForm(self)
        # Set up signals and slots
        self.media_manager_dock.visibilityChanged.connect(self.view_media_manager_item.setChecked)
        self.service_manager_dock.visibilityChanged.connect(self.view_service_manager_item.setChecked)
        self.theme_manager_dock.visibilityChanged.connect(self.view_theme_manager_item.setChecked)
        self.projector_manager_dock.visibilityChanged.connect(self.view_projector_manager_item.setChecked)
        self.import_theme_item.triggered.connect(self.theme_manager_contents.on_import_theme)
        self.export_theme_item.triggered.connect(self.theme_manager_contents.on_export_theme)
        self.web_site_item.triggered.connect(self.on_help_web_site_clicked)
        self.tools_open_data_folder.triggered.connect(self.on_tools_open_data_folder_clicked)
        self.tools_first_time_wizard.triggered.connect(self.on_first_time_wizard_clicked)
        self.update_theme_images.triggered.connect(self.on_update_theme_images)
        self.formatting_tag_item.triggered.connect(self.on_formatting_tag_item_clicked)
        self.settings_configure_item.triggered.connect(self.on_settings_configure_iem_clicked)
        self.settings_shortcuts_item.triggered.connect(self.on_settings_shortcuts_item_clicked)
        self.settings_import_item.triggered.connect(self.on_settings_import_item_clicked)
        self.settings_export_item.triggered.connect(self.on_settings_export_item_clicked)
        # i18n set signals for languages
        self.language_group.triggered.connect(LanguageManager.set_language)
        self.mode_default_item.triggered.connect(self.on_mode_default_item_clicked)
        self.mode_setup_item.triggered.connect(self.on_mode_setup_item_clicked)
        self.mode_live_item.triggered.connect(self.on_mode_live_item_clicked)
        # Media Manager
        self.media_tool_box.currentChanged.connect(self.on_media_tool_box_changed)
        self.application.set_busy_cursor()
        # Simple message boxes
        Registry().register_function('theme_update_global', self.default_theme_changed)
        QtCore.QObject.connect(self, QtCore.SIGNAL('openlp_version_check'),  self.version_notice)
        Registry().register_function('config_screen_changed', self.screen_changed)
        Registry().register_function('bootstrap_post_set_up', self.bootstrap_post_set_up)
        # Reset the cursor
        self.application.set_normal_cursor()

    def bootstrap_post_set_up(self):
        """
        process the bootstrap post setup request
        """
        self.preview_controller.panel.setVisible(Settings().value('user interface/preview panel'))
        self.live_controller.panel.setVisible(Settings().value('user interface/live panel'))
        self.load_settings()
        self.restore_current_media_manager_item()
        Registry().execute('theme_update_global')

    def restore_current_media_manager_item(self):
        """
        Called on start up to restore the last active media plugin.
        """
        log.info('Load data from Settings')
        if Settings().value('advanced/save current plugin'):
            saved_plugin_id = Settings().value('advanced/current media plugin')
            if saved_plugin_id != -1:
                self.media_tool_box.setCurrentIndex(saved_plugin_id)

    def on_search_shortcut_triggered(self):
        """
        Called when the search shortcut has been pressed.
        """
        # Make sure the media_dock is visible.
        if not self.media_manager_dock.isVisible():
            self.media_manager_dock.setVisible(True)
        widget = self.media_tool_box.currentWidget()
        if widget:
            widget.on_focus()

    def on_media_tool_box_changed(self, index):
        """
        Focus a widget when the media toolbox changes.
        """
        widget = self.media_tool_box.widget(index)
        if widget:
            widget.on_focus()

    def version_notice(self, version):
        """
        Notifies the user that a newer version of OpenLP is available.
        Triggered by delay thread and cannot display popup.

        :param version: The Version to be displayed.
        """
        log.debug('version_notice')
        version_text = translate('OpenLP.MainWindow', 'Version %s of OpenLP is now available for download (you are '
                                 'currently running version %s). \n\nYou can download the latest version from '
                                 'http://openlp.org/.')
        QtGui.QMessageBox.question(self, translate('OpenLP.MainWindow', 'OpenLP Version Updated'),
                                   version_text % (version, get_application_version()[u'full']))

    def show(self):
        """
        Show the main form, as well as the display form
        """
        QtGui.QWidget.show(self)
        if self.live_controller.display.isVisible():
            self.live_controller.display.setFocus()
        self.activateWindow()
        if self.arguments:
            self.open_cmd_line_files()
        elif Settings().value(self.general_settings_section + '/auto open'):
            self.service_manager_contents.load_last_file()
        view_mode = Settings().value('%s/view mode' % self.general_settings_section)
        if view_mode == 'default':
            self.mode_default_item.setChecked(True)
        elif view_mode == 'setup':
            self.set_view_mode(True, True, False, True, False, True)
            self.mode_setup_item.setChecked(True)
        elif view_mode == 'live':
            self.set_view_mode(False, True, False, False, True, True)
            self.mode_live_item.setChecked(True)

    def app_startup(self):
        """
        Give all the plugins a chance to perform some tasks at startup
        """
        self.application.process_events()
        for plugin in self.plugin_manager.plugins:
            if plugin.is_active():
                plugin.app_startup()
                self.application.process_events()

    def first_time(self):
        """
        Import themes if first time
        """
        self.application.process_events()
        for plugin in self.plugin_manager.plugins:
            if hasattr(plugin, 'first_time'):
                self.application.process_events()
                plugin.first_time()
        self.application.process_events()
        temp_dir = os.path.join(str(gettempdir()), 'openlp')
        shutil.rmtree(temp_dir, True)

    def on_first_time_wizard_clicked(self):
        """
        Re-run the first time wizard.  Prompts the user for run confirmation.If wizard is run, songs, bibles and
        themes are imported.  The default theme is changed (if necessary).  The plugins in pluginmanager are
        set active/in-active to match the selection in the wizard.
        """
        answer = QtGui.QMessageBox.warning(self,
                                           translate('OpenLP.MainWindow', 'Re-run First Time Wizard?'),
                                           translate('OpenLP.MainWindow', 'Are you sure you want to re-run the First '
                                                     'Time Wizard?\n\nRe-running this wizard may make changes to your '
                                                     'current OpenLP configuration and possibly add songs to your '
                                                     'existing songs list and change your default theme.'),
                                           QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes |
                                                                             QtGui.QMessageBox.No),
                                           QtGui.QMessageBox.No)
        if answer == QtGui.QMessageBox.No:
            return
        first_run_wizard = FirstTimeForm(self)
        first_run_wizard.initialize(ScreenList())
        first_run_wizard.exec_()
        if first_run_wizard.was_cancelled:
            return
        self.application.set_busy_cursor()
        self.first_time()
        for plugin in self.plugin_manager.plugins:
            self.active_plugin = plugin
            old_status = self.active_plugin.status
            self.active_plugin.set_status()
            if old_status != self.active_plugin.status:
                if self.active_plugin.status == PluginStatus.Active:
                    self.active_plugin.toggle_status(PluginStatus.Active)
                    self.active_plugin.app_startup()
                else:
                    self.active_plugin.toggle_status(PluginStatus.Inactive)
        # Set global theme and
        Registry().execute('theme_update_global')
        # Load the themes from files
        self.theme_manager_contents.load_first_time_themes()
        # Update the theme widget
        self.theme_manager_contents.load_themes()
        # Check if any Bibles downloaded.  If there are, they will be processed.
        Registry().execute('bibles_load_list', True)
        self.application.set_normal_cursor()

    def is_display_blank(self):
        """
        Check and display message if screen blank on setup.
        """
        settings = Settings()
        self.live_controller.main_display_set_background()
        if settings.value('%s/screen blank' % self.general_settings_section):
            if settings.value('%s/blank warning' % self.general_settings_section):
                QtGui.QMessageBox.question(self, translate('OpenLP.MainWindow', 'OpenLP Main Display Blanked'),
                                           translate('OpenLP.MainWindow', 'The Main Display has been blanked out'))

    def error_message(self, title, message):
        """
        Display an error message

        :param title: The title of the warning box.
        :param message: The message to be displayed.
        """
        if hasattr(self.application, 'splash'):
            self.application.splash.close()
        QtGui.QMessageBox.critical(self, title, message)

    def warning_message(self, title, message):
        """
        Display a warning message

        :param title:  The title of the warning box.
        :param message: The message to be displayed.
        """
        if hasattr(self.application, 'splash'):
            self.application.splash.close()
        QtGui.QMessageBox.warning(self, title, message)

    def information_message(self, title, message):
        """
        Display an informational message

        :param title: The title of the warning box.
        :param message: The message to be displayed.
        """
        if hasattr(self.application, 'splash'):
            self.application.splash.close()
        QtGui.QMessageBox.information(self, title, message)

    def on_help_web_site_clicked(self):
        """
        Load the OpenLP website
        """
        import webbrowser
        webbrowser.open_new('http://openlp.org/')

    def on_offline_help_clicked(self):
        """
        Load the local OpenLP help file
        """
        os.startfile(self.local_help_file)

    def on_online_help_clicked(self):
        """
        Load the online OpenLP manual
        """
        import webbrowser
        webbrowser.open_new('http://manual.openlp.org/')

    def on_about_item_clicked(self):
        """
        Show the About form
        """
        self.about_form.exec_()

    def on_plugin_item_clicked(self):
        """
        Show the Plugin form
        """
        self.plugin_form.load()
        self.plugin_form.exec_()

    def on_tools_open_data_folder_clicked(self):
        """
        Open data folder
        """
        path = AppLocation.get_data_path()
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("file:///" + path))

    def on_update_theme_images(self):
        """
        Updates the new theme preview images.
        """
        self.theme_manager_contents.update_preview_images()

    def on_formatting_tag_item_clicked(self):
        """
        Show the Settings dialog
        """
        self.formatting_tag_form.exec_()

    def on_settings_configure_iem_clicked(self):
        """
        Show the Settings dialog
        """
        self.settings_form.exec_()

    def paintEvent(self, event):
        """
        We need to make sure, that the SlidePreview's size is correct.
        """
        self.preview_controller.preview_size_changed()
        self.live_controller.preview_size_changed()

    def on_settings_shortcuts_item_clicked(self):
        """
        Show the shortcuts dialog
        """
        if self.shortcut_form.exec_():
            self.shortcut_form.save()

    def on_settings_import_item_clicked(self):
        """
        Import settings from an export INI file
        """
        answer = QtGui.QMessageBox.critical(self, translate('OpenLP.MainWindow', 'Import settings?'),
                                            translate('OpenLP.MainWindow', 'Are you sure you want to import '
                                                                           'settings?\n\n Importing settings will '
                                                                           'make permanent changes to your current '
                                                                           'OpenLP configuration.\n\n Importing '
                                                                           'incorrect settings may cause erratic '
                                                                           'behaviour or OpenLP to terminate '
                                                                           'abnormally.'),
                                            QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes |
                                                                              QtGui.QMessageBox.No),
                                            QtGui.QMessageBox.No)
        if answer == QtGui.QMessageBox.No:
            return
        import_file_name = QtGui.QFileDialog.getOpenFileName(self, translate('OpenLP.MainWindow', 'Open File'), '',
                                                             translate('OpenLP.MainWindow', 'OpenLP Export Settings '
                                                                                            'Files (*.conf)'))
        if not import_file_name:
            return
        setting_sections = []
        # Add main sections.
        setting_sections.extend([self.general_settings_section])
        setting_sections.extend([self.advanced_settings_section])
        setting_sections.extend([self.ui_settings_section])
        setting_sections.extend([self.shortcuts_settings_section])
        setting_sections.extend([self.service_manager_settings_section])
        setting_sections.extend([self.themes_settings_section])
        setting_sections.extend([self.projector_settings_section])
        setting_sections.extend([self.players_settings_section])
        setting_sections.extend([self.display_tags_section])
        setting_sections.extend([self.header_section])
        setting_sections.extend(['crashreport'])
        # Add plugin sections.
        setting_sections.extend([plugin.name for plugin in self.plugin_manager.plugins])
        # Copy the settings file to the tmp dir, because we do not want to change the original one.
        temp_directory = os.path.join(str(gettempdir()), 'openlp')
        check_directory_exists(temp_directory)
        temp_config = os.path.join(temp_directory, os.path.basename(import_file_name))
        shutil.copyfile(import_file_name, temp_config)
        settings = Settings()
        import_settings = Settings(temp_config, Settings.IniFormat)
        # Convert image files
        log.info('hook upgrade_plugin_settings')
        self.plugin_manager.hook_upgrade_plugin_settings(import_settings)
        # Remove/rename old settings to prepare the import.
        import_settings.remove_obsolete_settings()
        # Lets do a basic sanity check. If it contains this string we can assume it was created by OpenLP and so we'll
        # load what we can from it, and just silently ignore anything we don't recognise.
        if import_settings.value('SettingsImport/type') != 'OpenLP_settings_export':
            QtGui.QMessageBox.critical(self, translate('OpenLP.MainWindow', 'Import settings'),
                                       translate('OpenLP.MainWindow', 'The file you have selected does not appear to '
                                                 'be a valid OpenLP settings file.\n\nProcessing has terminated and '
                                                 'no changes have been made.'),
                                       QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))
            return
        import_keys = import_settings.allKeys()
        for section_key in import_keys:
            # We need to handle the really bad files.
            try:
                section, key = section_key.split('/')
            except ValueError:
                section = 'unknown'
                key = ''
            # Switch General back to lowercase.
            if section == 'General' or section == '%General':
                section = 'general'
                section_key = section + "/" + key
            # Make sure it's a valid section for us.
            if section not in setting_sections:
                continue
        # We have a good file, import it.
        for section_key in import_keys:
            if 'eneral' in section_key:
                section_key = section_key.lower()
            try:
                value = import_settings.value(section_key)
            except KeyError:
                log.warning('The key "%s" does not exist (anymore), so it will be skipped.' % section_key)
            if value is not None:
                settings.setValue('%s' % (section_key), value)
        now = datetime.now()
        settings.beginGroup(self.header_section)
        settings.setValue('file_imported', import_file_name)
        settings.setValue('file_date_imported', now.strftime("%Y-%m-%d %H:%M"))
        settings.endGroup()
        settings.sync()
        # We must do an immediate restart or current configuration will overwrite what was just imported when
        # application terminates normally.   We need to exit without saving configuration.
        QtGui.QMessageBox.information(self, translate('OpenLP.MainWindow', 'Import settings'),
                                      translate('OpenLP.MainWindow', 'OpenLP will now close.  Imported settings will '
                                                'be applied the next time you start OpenLP.'),
                                      QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))
        self.settings_imported = True
        self.clean_up()
        QtCore.QCoreApplication.exit()

    def on_settings_export_item_clicked(self):
        """
        Export settings to a .conf file in INI format
        """
        export_file_name = QtGui.QFileDialog.getSaveFileName(self,
                                                             translate('OpenLP.MainWindow', 'Export Settings File'),
                                                             '',
                                                             translate('OpenLP.MainWindow', 'OpenLP Export Settings '
                                                                                            'File (*.conf)'))
        if not export_file_name:
            return
            # Make sure it's a .conf file.
        if not export_file_name.endswith('conf'):
            export_file_name += '.conf'
        temp_file = os.path.join(gettempdir(), 'openlp', 'exportConf.tmp')
        self.save_settings()
        setting_sections = []
        # Add main sections.
        setting_sections.extend([self.general_settings_section])
        setting_sections.extend([self.advanced_settings_section])
        setting_sections.extend([self.ui_settings_section])
        setting_sections.extend([self.shortcuts_settings_section])
        setting_sections.extend([self.service_manager_settings_section])
        setting_sections.extend([self.themes_settings_section])
        setting_sections.extend([self.display_tags_section])
        # Add plugin sections.
        for plugin in self.plugin_manager.plugins:
            setting_sections.extend([plugin.name])
        # Delete old files if found.
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(export_file_name):
            os.remove(export_file_name)
        settings = Settings()
        settings.remove(self.header_section)
        # Get the settings.
        keys = settings.allKeys()
        export_settings = Settings(temp_file, Settings.IniFormat)
        # Add a header section.
        # This is to insure it's our conf file for import.
        now = datetime.now()
        application_version = get_application_version()
        # Write INI format using Qsettings.
        # Write our header.
        export_settings.beginGroup(self.header_section)
        export_settings.setValue('Make_Changes', 'At_Own_RISK')
        export_settings.setValue('type', 'OpenLP_settings_export')
        export_settings.setValue('file_date_created', now.strftime("%Y-%m-%d %H:%M"))
        export_settings.setValue('version', application_version['full'])
        export_settings.endGroup()
        # Write all the sections and keys.
        for section_key in keys:
            # FIXME: We are conflicting with the standard "General" section.
            if 'eneral' in section_key:
                section_key = section_key.lower()
            try:
                key_value = settings.value(section_key)
            except KeyError:
                QtGui.QMessageBox.critical(self, translate('OpenLP.MainWindow', 'Export setting error'),
                                           translate('OpenLP.MainWindow', 'The key "%s" does not have a default value '
                                                     'so it will be skipped in this export.') % section_key,
                                           QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))
                key_value = None
            if key_value is not None:
                export_settings.setValue(section_key, key_value)
        export_settings.sync()
        # Temp CONF file has been written.  Blanks in keys are now '%20'.
        # Read the  temp file and output the user's CONF file with blanks to
        # make it more readable.
        temp_conf = open(temp_file, 'r')
        try:
            export_conf = open(export_file_name, 'w')
            for file_record in temp_conf:
                # Get rid of any invalid entries.
                if file_record.find('@Invalid()') == -1:
                    file_record = file_record.replace('%20', ' ')
                    export_conf.write(file_record)
            temp_conf.close()
            export_conf.close()
            os.remove(temp_file)
        except OSError as ose:
                QtGui.QMessageBox.critical(self, translate('OpenLP.MainWindow', 'Export setting error'),
                                           translate('OpenLP.MainWindow', 'An error occurred while exporting the '
                                                                          'settings: %s') % ose.strerror,
                                           QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))

    def on_mode_default_item_clicked(self):
        """
        Put OpenLP into "Default" view mode.
        """
        self.set_view_mode(True, True, True, True, True, True, 'default')

    def on_mode_setup_item_clicked(self):
        """
        Put OpenLP into "Setup" view mode.
        """
        self.set_view_mode(True, True, False, True, False, True, 'setup')

    def on_mode_live_item_clicked(self):
        """
        Put OpenLP into "Live" view mode.
        """
        self.set_view_mode(False, True, False, False, True, True, 'live')

    def set_view_mode(self, media=True, service=True, theme=True, preview=True, live=True, projector=True, mode=''):
        """
        Set OpenLP to a different view mode.
        """
        if mode:
            settings = Settings()
            settings.setValue('%s/view mode' % self.general_settings_section, mode)
        self.media_manager_dock.setVisible(media)
        self.service_manager_dock.setVisible(service)
        self.theme_manager_dock.setVisible(theme)
        self.projector_manager_dock.setVisible(projector)
        self.set_preview_panel_visibility(preview)
        self.set_live_panel_visibility(live)

    def screen_changed(self):
        """
        The screen has changed so we have to update components such as the renderer.
        """
        log.debug('screen_changed')
        self.application.set_busy_cursor()
        self.image_manager.update_display()
        self.renderer.update_display()
        self.preview_controller.screen_size_changed()
        self.live_controller.screen_size_changed()
        self.setFocus()
        self.activateWindow()
        self.application.set_normal_cursor()

    def closeEvent(self, event):
        """
        Hook to close the main window and display windows on exit
        """
        # The MainApplication did not even enter the event loop (this happens
        # when OpenLP is not fully loaded). Just ignore the event.
        if not self.application.is_event_loop_active:
            event.ignore()
            return
        # If we just did a settings import, close without saving changes.
        if self.settings_imported:
            self.clean_up(False)
            event.accept()
        if self.service_manager_contents.is_modified():
            ret = self.service_manager_contents.save_modified_service()
            if ret == QtGui.QMessageBox.Save:
                if self.service_manager_contents.decide_save_method():
                    self.clean_up()
                    event.accept()
                else:
                    event.ignore()
            elif ret == QtGui.QMessageBox.Discard:
                self.clean_up()
                event.accept()
            else:
                event.ignore()
        else:
            if Settings().value('advanced/enable exit confirmation'):
                ret = QtGui.QMessageBox.question(self, translate('OpenLP.MainWindow', 'Close OpenLP'),
                                                 translate('OpenLP.MainWindow', 'Are you sure you want to close '
                                                                                'OpenLP?'),
                                                 QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes |
                                                                                   QtGui.QMessageBox.No),
                                                 QtGui.QMessageBox.Yes)
                if ret == QtGui.QMessageBox.Yes:
                    self.clean_up()
                    event.accept()
                else:
                    event.ignore()
            else:
                self.clean_up()
                event.accept()

    def clean_up(self, save_settings=True):
        """
        Runs all the cleanup code before OpenLP shuts down.

        :param save_settings: Switch to prevent saving settings. Defaults to **True**.
        """
        self.image_manager.stop_manager = True
        while self.image_manager.image_thread.isRunning():
            time.sleep(0.1)
        if save_settings:
            if Settings().value('advanced/save current plugin'):
                Settings().setValue('advanced/current media plugin', self.media_tool_box.currentIndex())
        # Call the cleanup method to shutdown plugins.
        log.info('cleanup plugins')
        self.plugin_manager.finalise_plugins()
        if save_settings:
            # Save settings
            self.save_settings()
        # Check if we need to change the data directory
        if self.new_data_path:
            self.change_data_directory()
        # Close down the display
        if self.live_controller.display:
            self.live_controller.display.close()
            self.live_controller.display = None
        # Clean temporary files used by services
        self.service_manager_contents.clean_up()
        if is_win():
            # Needed for Windows to stop crashes on exit
            Registry().remove('application')

    def set_service_modified(self, modified, file_name):
        """
        This method is called from the ServiceManager to set the title of the main window.

        :param modified: Whether or not this service has been modified.
        :param file_name: The file name of the service file.
        """
        if modified:
            title = '%s - %s*' % (UiStrings().OLPV2x, file_name)
        else:
            title = '%s - %s' % (UiStrings().OLPV2x, file_name)
        self.setWindowTitle(title)

    def show_status_message(self, message):
        """
        Show a message in the status bar
        """
        self.status_bar.showMessage(message)

    def default_theme_changed(self):
        """
        Update the default theme indicator in the status bar
        """
        self.default_theme_label.setText(translate('OpenLP.MainWindow', 'Default Theme: %s') %
                                         Settings().value('themes/global theme'))

    def toggle_media_manager(self):
        """
        Toggle the visibility of the media manager
        """
        self.media_manager_dock.setVisible(not self.media_manager_dock.isVisible())

    def toggle_projector_manager(self):
        """
        Toggle visibility of the projector manager
        """
        self.projector_manager_dock.setVisible(not self.projector_manager_dock.isVisible())

    def toggle_service_manager(self):
        """
        Toggle the visibility of the service manager
        """
        self.service_manager_dock.setVisible(not self.service_manager_dock.isVisible())

    def toggle_theme_manager(self):
        """
        Toggle the visibility of the theme manager
        """
        self.theme_manager_dock.setVisible(not self.theme_manager_dock.isVisible())

    def set_preview_panel_visibility(self, visible):
        """
        Sets the visibility of the preview panel including saving the setting and updating the menu.

        :param visible: A bool giving the state to set the panel to
                True - Visible
                False - Hidden

        """
        self.preview_controller.panel.setVisible(visible)
        Settings().setValue('user interface/preview panel', visible)
        self.view_preview_panel.setChecked(visible)

    def set_lock_panel(self, lock):
        """
        Sets the ability to stop the toolbars being changed.
        """
        if lock:
            self.theme_manager_dock.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
            self.service_manager_dock.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
            self.media_manager_dock.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
            self.projector_manager_dock.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
            self.view_media_manager_item.setEnabled(False)
            self.view_service_manager_item.setEnabled(False)
            self.view_theme_manager_item.setEnabled(False)
            self.view_projector_manager_item.setEnabled(False)
            self.view_preview_panel.setEnabled(False)
            self.view_live_panel.setEnabled(False)
        else:
            self.theme_manager_dock.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
            self.service_manager_dock.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
            self.media_manager_dock.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
            self.projector_manager_dock.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
            self.view_media_manager_item.setEnabled(True)
            self.view_service_manager_item.setEnabled(True)
            self.view_theme_manager_item.setEnabled(True)
            self.view_projector_manager_item.setEnabled(True)
            self.view_preview_panel.setEnabled(True)
            self.view_live_panel.setEnabled(True)
        Settings().setValue('user interface/lock panel', lock)

    def set_live_panel_visibility(self, visible):
        """
        Sets the visibility of the live panel including saving the setting and updating the menu.


        :param visible: A bool giving the state to set the panel to
                True - Visible
                False - Hidden
        """
        self.live_controller.panel.setVisible(visible)
        Settings().setValue('user interface/live panel', visible)
        self.view_live_panel.setChecked(visible)

    def load_settings(self):
        """
        Load the main window settings.
        """
        log.debug('Loading QSettings')
        settings = Settings()
        # Remove obsolete entries.
        settings.remove('custom slide')
        settings.remove('service')
        settings.beginGroup(self.general_settings_section)
        self.recent_files = settings.value('recent files')
        settings.endGroup()
        settings.beginGroup(self.ui_settings_section)
        self.move(settings.value('main window position'))
        self.restoreGeometry(settings.value('main window geometry'))
        self.restoreState(settings.value('main window state'))
        self.live_controller.splitter.restoreState(settings.value('live splitter geometry'))
        self.preview_controller.splitter.restoreState(settings.value('preview splitter geometry'))
        self.control_splitter.restoreState(settings.value('main window splitter geometry'))
        # This needs to be called after restoreState(), because saveState() also saves the "Collapsible" property
        # which was True (by default) < OpenLP 2.1.
        self.control_splitter.setChildrenCollapsible(False)
        settings.endGroup()

    def save_settings(self):
        """
        Save the main window settings.
        """
        # Exit if we just did a settings import.
        if self.settings_imported:
            return
        log.debug('Saving QSettings')
        settings = Settings()
        settings.beginGroup(self.general_settings_section)
        settings.setValue('recent files', self.recent_files)
        settings.endGroup()
        settings.beginGroup(self.ui_settings_section)
        settings.setValue('main window position', self.pos())
        settings.setValue('main window state', self.saveState())
        settings.setValue('main window geometry', self.saveGeometry())
        settings.setValue('live splitter geometry', self.live_controller.splitter.saveState())
        settings.setValue('preview splitter geometry', self.preview_controller.splitter.saveState())
        settings.setValue('main window splitter geometry', self.control_splitter.saveState())
        settings.endGroup()

    def update_recent_files_menu(self):
        """
        Updates the recent file menu with the latest list of service files accessed.
        """
        recent_file_count = Settings().value('advanced/recent file count')
        existing_recent_files = [recentFile for recentFile in self.recent_files if os.path.isfile(str(recentFile))]
        recent_files_to_display = existing_recent_files[0:recent_file_count]
        self.recent_files_menu.clear()
        for file_id, filename in enumerate(recent_files_to_display):
            log.debug('Recent file name: %s', filename)
            action = create_action(self, '', text='&%d %s' % (file_id + 1,
                                   os.path.splitext(os.path.basename(str(filename)))[0]), data=filename,
                                   triggers=self.service_manager_contents.on_recent_service_clicked)
            self.recent_files_menu.addAction(action)
        clear_recent_files_action = create_action(self, '',
                                                  text=translate('OpenLP.MainWindow', 'Clear List', 'Clear List of '
                                                                                                    'recent files'),
                                                  statustip=translate('OpenLP.MainWindow', 'Clear the list of recent '
                                                                                           'files.'),
                                                  enabled=bool(self.recent_files),
                                                  triggers=self.clear_recent_file_menu)
        add_actions(self.recent_files_menu, (None, clear_recent_files_action))
        clear_recent_files_action.setEnabled(bool(self.recent_files))

    def add_recent_file(self, filename):
        """
        Adds a service to the list of recently used files.

        :param filename: The service filename to add
        """
        # The max_recent_files value does not have an interface and so never gets
        # actually stored in the settings therefore the default value of 20 will
        # always be used.
        max_recent_files = Settings().value('advanced/max recent files')
        if filename:
            # Add some cleanup to reduce duplication in the recent file list
            filename = os.path.abspath(filename)
            # abspath() only capitalises the drive letter if it wasn't provided
            # in the given filename which then causes duplication.
            if filename[1:3] == ':\\':
                filename = filename[0].upper() + filename[1:]
            if filename in self.recent_files:
                self.recent_files.remove(filename)
            if not isinstance(self.recent_files, list):
                self.recent_files = [self.recent_files]
            self.recent_files.insert(0, filename)
            while len(self.recent_files) > max_recent_files:
                self.recent_files.pop()

    def clear_recent_file_menu(self):
        """
        Clears the recent files.
        """
        self.recent_files = []

    def display_progress_bar(self, size):
        """
        Make Progress bar visible and set size
        """
        self.load_progress_bar.show()
        self.load_progress_bar.setMaximum(size)
        self.load_progress_bar.setValue(0)
        self.application.process_events()

    def increment_progress_bar(self):
        """
        Increase the Progress Bar value by 1
        """
        self.load_progress_bar.setValue(self.load_progress_bar.value() + 1)
        self.application.process_events()

    def finished_progress_bar(self):
        """
        Trigger it's removal after 2.5 second
        """
        self.timer_id = self.startTimer(2500)

    def timerEvent(self, event):
        """
        Remove the Progress bar from view.
        """
        if event.timerId() == self.timer_id:
            self.timer_id = 0
            self.load_progress_bar.hide()
            self.application.process_events()

    def set_new_data_path(self, new_data_path):
        """
        Set the new data path
        """
        self.new_data_path = new_data_path

    def set_copy_data(self, copy_data):
        """
        Set the flag to copy the data
        """
        self.copy_data = copy_data

    def change_data_directory(self):
        """
        Change the data directory.
        """
        log.info('Changing data path to %s' % self.new_data_path)
        old_data_path = str(AppLocation.get_data_path())
        # Copy OpenLP data to new location if requested.
        self.application.set_busy_cursor()
        if self.copy_data:
            log.info('Copying data to new path')
            try:
                self.show_status_message(
                    translate('OpenLP.MainWindow', 'Copying OpenLP data to new data directory location - %s '
                              '- Please wait for copy to finish').replace('%s', self.new_data_path))
                dir_util.copy_tree(old_data_path, self.new_data_path)
                log.info('Copy successful')
            except (IOError, os.error, DistutilsFileError) as why:
                self.application.set_normal_cursor()
                log.exception('Data copy failed %s' % str(why))
                QtGui.QMessageBox.critical(self, translate('OpenLP.MainWindow', 'New Data Directory Error'),
                                           translate('OpenLP.MainWindow', 'OpenLP Data directory copy failed\n\n%s').
                                           replace('%s', str(why)),
                                           QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))
                return False
        else:
            log.info('No data copy requested')
        # Change the location of data directory in config file.
        settings = QtCore.QSettings()
        settings.setValue('advanced/data path', self.new_data_path)
        # Check if the new data path is our default.
        if self.new_data_path == AppLocation.get_directory(AppLocation.DataDir):
            settings.remove('advanced/data path')
        self.application.set_normal_cursor()

    def open_cmd_line_files(self):
        """
        Open files passed in through command line arguments
        """
        args = []
        for a in self.arguments:
            args.extend([a])
        for filename in args:
            if not isinstance(filename, str):
                filename = str(filename, sys.getfilesystemencoding())
            if filename.endswith(('.osz', '.oszl')):
                self.service_manager_contents.load_file(filename)
