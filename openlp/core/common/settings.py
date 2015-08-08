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
This class contains the core default settings.
"""
import datetime
import logging
import os

from PyQt4 import QtCore, QtGui

from openlp.core.common import ThemeLevel, SlideLimits, UiStrings, is_win, is_linux


log = logging.getLogger(__name__)


# Fix for bug #1014422.
X11_BYPASS_DEFAULT = True
if is_linux():
    # Default to False on Gnome.
    X11_BYPASS_DEFAULT = bool(not os.environ.get('GNOME_DESKTOP_SESSION_ID'))
    # Default to False on Xfce.
    if os.environ.get('DESKTOP_SESSION') == 'xfce':
        X11_BYPASS_DEFAULT = False


def recent_files_conv(value):
    """
    If the value is not a list convert it to a list
    :param value: Value to convert
    :return: value as a List
    """
    if isinstance(value, list):
        return value
    elif isinstance(value, str):
        return [value]
    elif isinstance(value, bytes):
        return [value.decode()]
    return []


class Settings(QtCore.QSettings):
    """
    Class to wrap QSettings.

    * Exposes all the methods of QSettings.
    * Adds functionality for OpenLP Portable. If the ``defaultFormat`` is set to
    ``IniFormat``, and the path to the Ini file is set using ``set_filename``,
    then the Settings constructor (without any arguments) will create a Settings
    object for accessing settings stored in that Ini file.

    ``__default_settings__``
        This dict contains all core settings with their default values.

    ``__obsolete_settings__``
        Each entry is structured in the following way::

            ('general/enable slide loop', 'advanced/slide limits', [(SlideLimits.Wrap, True), (SlideLimits.End, False)])

        The first entry is the *old key*; it will be removed.

        The second entry is the *new key*; we will add it to the config. If this is just an empty string, we just remove
        the old key. The last entry is a list containing two-pair tuples. If the list is empty, no conversion is made.
        If the first value is callable i.e. a function, the function will be called with the old setting's value.
        Otherwise each pair describes how to convert the old setting's value::

            (SlideLimits.Wrap, True)

        This means, that if the value of ``general/enable slide loop`` is equal (``==``) ``True`` then we set
        ``advanced/slide limits`` to ``SlideLimits.Wrap``. **NOTE**, this means that the rules have to cover all cases!
        So, if the type of the old value is bool, then there must be two rules.
    """
    __default_settings__ = {
        'advanced/add page break': False,
        'advanced/alternate rows': not is_win(),
        'advanced/current media plugin': -1,
        'advanced/data path': '',
        'advanced/default color': '#ffffff',
        'advanced/default image': ':/graphics/openlp-splash-screen.png',
        # 7 stands for now, 0 to 6 is Monday to Sunday.
        'advanced/default service day': 7,
        'advanced/default service enabled': True,
        'advanced/default service hour': 11,
        'advanced/default service minute': 0,
        'advanced/default service name': UiStrings().DefaultServiceName,
        'advanced/display size': 0,
        'advanced/double click live': False,
        'advanced/enable exit confirmation': True,
        'advanced/expand service item': False,
        'advanced/hide mouse': True,
        'advanced/is portable': False,
        'advanced/max recent files': 20,
        'advanced/print file meta data': False,
        'advanced/print notes': False,
        'advanced/print slide text': False,
        'advanced/recent file count': 4,
        'advanced/save current plugin': False,
        'advanced/slide limits': SlideLimits.End,
        'advanced/single click preview': False,
        'advanced/x11 bypass wm': X11_BYPASS_DEFAULT,
        'crashreport/last directory': '',
        'formattingTags/html_tags': '',
        'core/audio repeat list': False,
        'core/auto open': False,
        'core/auto preview': False,
        'core/audio start paused': True,
        'core/auto unblank': False,
        'core/blank warning': False,
        'core/ccli number': '',
        'core/has run wizard': False,
        'core/language': '[en]',
        'core/last version test': '',
        'core/loop delay': 5,
        'core/recent files': [],
        'core/save prompt': False,
        'core/screen blank': False,
        'core/show splash': True,
        'core/songselect password': '',
        'core/songselect username': '',
        'core/update check': True,
        'core/view mode': 'default',
        # The other display settings (display position and dimensions) are defined in the ScreenList class due to a
        # circular dependency.
        'core/display on monitor': True,
        'core/override position': False,
        'core/application version': '0.0',
        'images/background color': '#000000',
        'media/players': 'webkit',
        'media/override player': QtCore.Qt.Unchecked,
        'players/background color': '#000000',
        'servicemanager/last directory': '',
        'servicemanager/last file': '',
        'servicemanager/service theme': '',
        'SettingsImport/file_date_created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        'SettingsImport/Make_Changes': 'At_Own_RISK',
        'SettingsImport/type': 'OpenLP_settings_export',
        'SettingsImport/version': '',
        'shortcuts/aboutItem': [QtGui.QKeySequence('Ctrl+F1')],
        'shortcuts/addToService': [],
        'shortcuts/audioPauseItem': [],
        'shortcuts/displayTagItem': [],
        'shortcuts/blankScreen': [QtGui.QKeySequence(QtCore.Qt.Key_Period)],
        'shortcuts/collapse': [QtGui.QKeySequence(QtCore.Qt.Key_Minus)],
        'shortcuts/desktopScreen': [QtGui.QKeySequence('D')],
        'shortcuts/delete': [],
        'shortcuts/down': [QtGui.QKeySequence(QtCore.Qt.Key_Down)],
        'shortcuts/editSong': [],
        'shortcuts/escapeItem': [QtGui.QKeySequence(QtCore.Qt.Key_Escape)],
        'shortcuts/expand': [QtGui.QKeySequence(QtCore.Qt.Key_Plus)],
        'shortcuts/exportThemeItem': [],
        'shortcuts/fileNewItem': [QtGui.QKeySequence('Ctrl+N')],
        'shortcuts/fileSaveAsItem': [QtGui.QKeySequence('Ctrl+Shift+S')],
        'shortcuts/fileExitItem': [QtGui.QKeySequence('Alt+F4')],
        'shortcuts/fileSaveItem': [QtGui.QKeySequence('Ctrl+S')],
        'shortcuts/fileOpenItem': [QtGui.QKeySequence('Ctrl+O')],
        'shortcuts/goLive': [],
        'shortcuts/importThemeItem': [],
        'shortcuts/importBibleItem': [],
        'shortcuts/listViewBiblesDeleteItem': [QtGui.QKeySequence(QtCore.Qt.Key_Delete)],
        'shortcuts/listViewBiblesPreviewItem': [QtGui.QKeySequence(QtCore.Qt.Key_Enter),
                                                QtGui.QKeySequence(QtCore.Qt.Key_Return)],
        'shortcuts/listViewBiblesLiveItem': [QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Enter),
                                             QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Return)],
        'shortcuts/listViewBiblesServiceItem': [QtGui.QKeySequence(QtCore.Qt.Key_Plus),
                                                QtGui.QKeySequence(QtCore.Qt.Key_Equal)],
        'shortcuts/listViewCustomDeleteItem': [QtGui.QKeySequence(QtCore.Qt.Key_Delete)],
        'shortcuts/listViewCustomPreviewItem': [QtGui.QKeySequence(QtCore.Qt.Key_Enter),
                                                QtGui.QKeySequence(QtCore.Qt.Key_Return)],
        'shortcuts/listViewCustomLiveItem': [QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Enter),
                                             QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Return)],
        'shortcuts/listViewCustomServiceItem': [QtGui.QKeySequence(QtCore.Qt.Key_Plus),
                                                QtGui.QKeySequence(QtCore.Qt.Key_Equal)],
        'shortcuts/listViewImagesDeleteItem': [QtGui.QKeySequence(QtCore.Qt.Key_Delete)],
        'shortcuts/listViewImagesPreviewItem': [QtGui.QKeySequence(QtCore.Qt.Key_Enter),
                                                QtGui.QKeySequence(QtCore.Qt.Key_Return)],
        'shortcuts/listViewImagesLiveItem': [QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Enter),
                                             QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Return)],
        'shortcuts/listViewImagesServiceItem': [QtGui.QKeySequence(QtCore.Qt.Key_Plus),
                                                QtGui.QKeySequence(QtCore.Qt.Key_Equal)],
        'shortcuts/listViewMediaDeleteItem': [QtGui.QKeySequence(QtCore.Qt.Key_Delete)],
        'shortcuts/listViewMediaPreviewItem': [QtGui.QKeySequence(QtCore.Qt.Key_Enter),
                                               QtGui.QKeySequence(QtCore.Qt.Key_Return)],
        'shortcuts/listViewMediaLiveItem': [QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Enter),
                                            QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Return)],
        'shortcuts/listViewMediaServiceItem': [QtGui.QKeySequence(QtCore.Qt.Key_Plus),
                                               QtGui.QKeySequence(QtCore.Qt.Key_Equal)],
        'shortcuts/listViewPresentationsDeleteItem': [QtGui.QKeySequence(QtCore.Qt.Key_Delete)],
        'shortcuts/listViewPresentationsPreviewItem': [QtGui.QKeySequence(QtCore.Qt.Key_Enter),
                                                       QtGui.QKeySequence(QtCore.Qt.Key_Return)],
        'shortcuts/listViewPresentationsLiveItem': [QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Enter),
                                                    QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Return)],
        'shortcuts/listViewPresentationsServiceItem': [QtGui.QKeySequence(QtCore.Qt.Key_Plus),
                                                       QtGui.QKeySequence(QtCore.Qt.Key_Equal)],
        'shortcuts/listViewSongsDeleteItem': [QtGui.QKeySequence(QtCore.Qt.Key_Delete)],
        'shortcuts/listViewSongsPreviewItem': [QtGui.QKeySequence(QtCore.Qt.Key_Enter),
                                               QtGui.QKeySequence(QtCore.Qt.Key_Return)],
        'shortcuts/listViewSongsLiveItem': [QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Enter),
                                            QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Return)],
        'shortcuts/listViewSongsServiceItem': [QtGui.QKeySequence(QtCore.Qt.Key_Plus),
                                               QtGui.QKeySequence(QtCore.Qt.Key_Equal)],
        'shortcuts/lockPanel': [],
        'shortcuts/modeDefaultItem': [],
        'shortcuts/modeLiveItem': [],
        'shortcuts/make_live': [QtGui.QKeySequence(QtCore.Qt.Key_Enter), QtGui.QKeySequence(QtCore.Qt.Key_Return)],
        'shortcuts/moveUp': [QtGui.QKeySequence(QtCore.Qt.Key_PageUp)],
        'shortcuts/moveTop': [QtGui.QKeySequence(QtCore.Qt.Key_Home)],
        'shortcuts/modeSetupItem': [],
        'shortcuts/moveBottom': [QtGui.QKeySequence(QtCore.Qt.Key_End)],
        'shortcuts/moveDown': [QtGui.QKeySequence(QtCore.Qt.Key_PageDown)],
        'shortcuts/nextTrackItem': [],
        'shortcuts/nextItem_live': [QtGui.QKeySequence(QtCore.Qt.Key_Down), QtGui.QKeySequence(QtCore.Qt.Key_PageDown)],
        'shortcuts/nextItem_preview': [QtGui.QKeySequence(QtCore.Qt.Key_Down),
                                       QtGui.QKeySequence(QtCore.Qt.Key_PageDown)],
        'shortcuts/nextService': [QtGui.QKeySequence(QtCore.Qt.Key_Right)],
        'shortcuts/newService': [],
        'shortcuts/offlineHelpItem': [],
        'shortcuts/onlineHelpItem': [QtGui.QKeySequence('Alt+F1')],
        'shortcuts/openService': [],
        'shortcuts/saveService': [],
        'shortcuts/previousItem_live': [QtGui.QKeySequence(QtCore.Qt.Key_Up), QtGui.QKeySequence(QtCore.Qt.Key_PageUp)],
        'shortcuts/playbackPause': [],
        'shortcuts/playbackPlay': [],
        'shortcuts/playbackStop': [],
        'shortcuts/playSlidesLoop': [],
        'shortcuts/playSlidesOnce': [],
        'shortcuts/previousService': [QtGui.QKeySequence(QtCore.Qt.Key_Left)],
        'shortcuts/previousItem_preview': [QtGui.QKeySequence(QtCore.Qt.Key_Up),
                                           QtGui.QKeySequence(QtCore.Qt.Key_PageUp)],
        'shortcuts/printServiceItem': [QtGui.QKeySequence('Ctrl+P')],
        'shortcuts/songExportItem': [],
        'shortcuts/songUsageStatus': [QtGui.QKeySequence(QtCore.Qt.Key_F4)],
        'shortcuts/searchShortcut': [QtGui.QKeySequence('Ctrl+F')],
        'shortcuts/settingsShortcutsItem': [],
        'shortcuts/settingsImportItem': [],
        'shortcuts/settingsPluginListItem': [QtGui.QKeySequence('Alt+F7')],
        'shortcuts/songUsageDelete': [],
        'shortcuts/settingsConfigureItem': [],
        'shortcuts/shortcutAction_B': [QtGui.QKeySequence('B')],
        'shortcuts/shortcutAction_C': [QtGui.QKeySequence('C')],
        'shortcuts/shortcutAction_E': [QtGui.QKeySequence('E')],
        'shortcuts/shortcutAction_I': [QtGui.QKeySequence('I')],
        'shortcuts/shortcutAction_O': [QtGui.QKeySequence('O')],
        'shortcuts/shortcutAction_P': [QtGui.QKeySequence('P')],
        'shortcuts/shortcutAction_V': [QtGui.QKeySequence('V')],
        'shortcuts/shortcutAction_0': [QtGui.QKeySequence('0')],
        'shortcuts/shortcutAction_1': [QtGui.QKeySequence('1')],
        'shortcuts/shortcutAction_2': [QtGui.QKeySequence('2')],
        'shortcuts/shortcutAction_3': [QtGui.QKeySequence('3')],
        'shortcuts/shortcutAction_4': [QtGui.QKeySequence('4')],
        'shortcuts/shortcutAction_5': [QtGui.QKeySequence('5')],
        'shortcuts/shortcutAction_6': [QtGui.QKeySequence('6')],
        'shortcuts/shortcutAction_7': [QtGui.QKeySequence('7')],
        'shortcuts/shortcutAction_8': [QtGui.QKeySequence('8')],
        'shortcuts/shortcutAction_9': [QtGui.QKeySequence('9')],
        'shortcuts/settingsExportItem': [],
        'shortcuts/songUsageReport': [],
        'shortcuts/songImportItem': [],
        'shortcuts/themeScreen': [QtGui.QKeySequence('T')],
        'shortcuts/toolsReindexItem': [],
        'shortcuts/toolsFindDuplicates': [],
        'shortcuts/toolsAlertItem': [QtGui.QKeySequence('F7')],
        'shortcuts/toolsFirstTimeWizard': [],
        'shortcuts/toolsOpenDataFolder': [],
        'shortcuts/toolsAddToolItem': [],
        'shortcuts/updateThemeImages': [],
        'shortcuts/up': [QtGui.QKeySequence(QtCore.Qt.Key_Up)],
        'shortcuts/viewProjectorManagerItem': [QtGui.QKeySequence('F6')],
        'shortcuts/viewThemeManagerItem': [QtGui.QKeySequence('F10')],
        'shortcuts/viewMediaManagerItem': [QtGui.QKeySequence('F8')],
        'shortcuts/viewPreviewPanel': [QtGui.QKeySequence('F11')],
        'shortcuts/viewLivePanel': [QtGui.QKeySequence('F12')],
        'shortcuts/viewServiceManagerItem': [QtGui.QKeySequence('F9')],
        'shortcuts/webSiteItem': [],
        'themes/global theme': '',
        'themes/last directory': '',
        'themes/last directory export': '',
        'themes/last directory import': '',
        'themes/theme level': ThemeLevel.Song,
        'themes/wrap footer': False,
        'user interface/live panel': True,
        'user interface/live splitter geometry': QtCore.QByteArray(),
        'user interface/lock panel': False,
        'user interface/main window geometry': QtCore.QByteArray(),
        'user interface/main window position': QtCore.QPoint(0, 0),
        'user interface/main window splitter geometry': QtCore.QByteArray(),
        'user interface/main window state': QtCore.QByteArray(),
        'user interface/preview panel': True,
        'user interface/preview splitter geometry': QtCore.QByteArray(),
        'projector/db type': 'sqlite',
        'projector/db username': '',
        'projector/db password': '',
        'projector/db hostname': '',
        'projector/db database': '',
        'projector/enable': True,
        'projector/connect on start': False,
        'projector/last directory import': '',
        'projector/last directory export': '',
        'projector/poll time': 20,  # PJLink  timeout is 30 seconds
        'projector/socket timeout': 5,  # 5 second socket timeout
        'projector/source dialog type': 0  # Source select dialog box type
    }
    __file_path__ = ''
    __obsolete_settings__ = [
        # Changed during 1.9.x development.
        ('bibles/bookname language', 'bibles/book name language', []),
        ('general/enable slide loop', 'advanced/slide limits', [(SlideLimits.Wrap, True), (SlideLimits.End, False)]),
        ('songs/ccli number', 'core/ccli number', []),
        ('media/use phonon', '', []),
        # Changed during 2.1.x development.
        ('advanced/stylesheet fix', '', []),
        ('bibles/last directory 1', 'bibles/last directory import', []),
        ('media/background color', 'players/background color', []),
        ('themes/last directory', 'themes/last directory import', []),
        ('themes/last directory 1', 'themes/last directory export', []),
        ('songs/last directory 1', 'songs/last directory import', []),
        ('songusage/last directory 1', 'songusage/last directory export', []),
        ('user interface/mainwindow splitter geometry', 'user interface/main window splitter geometry', []),
        ('shortcuts/makeLive', 'shortcuts/make_live', []),
        ('general/audio repeat list', 'core/audio repeat list', []),
        ('general/auto open', 'core/auto open', []),
        ('general/auto preview', 'core/auto preview', []),
        ('general/audio start paused', 'core/audio start paused', []),
        ('general/auto unblank', 'core/auto unblank', []),
        ('general/blank warning', 'core/blank warning', []),
        ('general/ccli number', 'core/ccli number', []),
        ('general/has run wizard', 'core/has run wizard', []),
        ('general/language', 'core/language', []),
        ('general/last version test', 'core/last version test', []),
        ('general/loop delay', 'core/loop delay', []),
        ('general/recent files', 'core/recent files', [(recent_files_conv, None)]),
        ('general/save prompt', 'core/save prompt', []),
        ('general/screen blank', 'core/screen blank', []),
        ('general/show splash', 'core/show splash', []),
        ('general/songselect password', 'core/songselect password', []),
        ('general/songselect username', 'core/songselect username', []),
        ('general/update check', 'core/update check', []),
        ('general/view mode', 'core/view mode', []),
        ('general/display on monitor', 'core/display on monitor', []),
        ('general/override position', 'core/override position', []),
        ('general/x position', 'core/x position', []),
        ('general/y position', 'core/y position', []),
        ('general/monitor', 'core/monitor', []),
        ('general/height', 'core/height', []),
        ('general/monitor', 'core/monitor', []),
        ('general/width', 'core/width', [])
    ]

    @staticmethod
    def extend_default_settings(default_values):
        """
        Static method to merge the given ``default_values`` with the ``Settings.__default_settings__``.

        :param default_values: A dict with setting keys and their default values.
        """
        Settings.__default_settings__.update(default_values)

    @staticmethod
    def set_filename(ini_file):
        """
        Sets the complete path to an Ini file to be used by Settings objects.

        Does not affect existing Settings objects.
        """
        Settings.__file_path__ = ini_file

    @staticmethod
    def set_up_default_values():
        """
        This static method is called on start up. It is used to perform any operation on the __default_settings__ dict.
        """
        # Make sure the string is translated (when building the dict the string is not translated because the translate
        # function was not set up as this stage).
        Settings.__default_settings__['advanced/default service name'] = UiStrings().DefaultServiceName

    def __init__(self, *args):
        """
        Constructor which checks if this should be a native settings object, or an INI file.
        """
        if not args and Settings.__file_path__ and Settings.defaultFormat() == Settings.IniFormat:
            QtCore.QSettings.__init__(self, Settings.__file_path__, Settings.IniFormat)
        else:
            QtCore.QSettings.__init__(self, *args)

    def get_default_value(self, key):
        """
        Get the default value of the given key
        """
        if self.group():
            key = self.group() + '/' + key
        return Settings.__default_settings__[key]

    def remove_obsolete_settings(self):
        """
        This method is only called to clean up the config. It removes old settings and it renames settings. See
        ``__obsolete_settings__`` for more details.
        """
        for old_key, new_key, rules in Settings.__obsolete_settings__:
            # Once removed we don't have to do this again.
            if self.contains(old_key):
                if new_key:
                    # Get the value of the old_key.
                    old_value = super(Settings, self).value(old_key)
                    # When we want to convert the value, we have to figure out the default value (because we cannot get
                    # the default value from the central settings dict.
                    if rules:
                        default_value = rules[0][1]
                        old_value = self._convert_value(old_value, default_value)
                    # Iterate over our rules and check what the old_value should be "converted" to.
                    for new, old in rules:
                        # If the value matches with the condition (rule), then use the provided value. This is used to
                        # convert values. E. g. an old value 1 results in True, and 0 in False.
                        if callable(new):
                            old_value = new(old_value)
                        elif old == old_value:
                            old_value = new
                            break
                    self.setValue(new_key, old_value)
                self.remove(old_key)

    def value(self, key):
        """
        Returns the value for the given ``key``. The returned ``value`` is of the same type as the default value in the
        *Settings.__default_settings__* dict.

        :param key: The key to return the value from.
        """
        # if group() is not empty the group has not been specified together with the key.
        if self.group():
            default_value = Settings.__default_settings__[self.group() + '/' + key]
        else:
            default_value = Settings.__default_settings__[key]
        setting = super(Settings, self).value(key, default_value)
        return self._convert_value(setting, default_value)

    def _convert_value(self, setting, default_value):
        """
        This converts the given ``setting`` to the type of the given ``default_value``.

        :param setting: The setting to convert. This could be ``true`` for example.Settings()
        :param default_value: Indication the type the setting should be converted to. For example ``True``
        (type is boolean), meaning that we convert the string ``true`` to a python boolean.

        **Note**, this method only converts a few types and might need to be extended if a certain type is missing!
        """
        # On OS X (and probably on other platforms too) empty value from QSettings is represented as type
        # PyQt4.QtCore.QPyNullVariant. This type has to be converted to proper 'None' Python type.
        if isinstance(setting, QtCore.QPyNullVariant) and setting.isNull():
            setting = None
        # Handle 'None' type (empty value) properly.
        if setting is None:
            # An empty string saved to the settings results in a None type being returned.
            # Convert it to empty unicode string.
            if isinstance(default_value, str):
                return ''
            # An empty list saved to the settings results in a None type being returned.
            else:
                return []
        # Convert the setting to the correct type.
        if isinstance(default_value, bool):
            if isinstance(setting, bool):
                return setting
            # Sometimes setting is string instead of a boolean.
            return setting == 'true'
        if isinstance(default_value, int):
            return int(setting)
        return setting

    def get_files_from_config(self, plugin):
        """
        This removes the settings needed for old way we saved files (e. g. the image paths for the image plugin). A list
        of file paths are returned.

         **Note**: Only a list of paths is returned; this does not convert anything!

         :param plugin: The Plugin object.The caller has to convert/save the list himself; o
        """
        files_list = []
        # We need QSettings instead of Settings here to bypass our central settings dict.
        # Do NOT do this anywhere else!
        settings = QtCore.QSettings(self.fileName(), Settings.IniFormat)
        settings.beginGroup(plugin.settings_section)
        if settings.contains('%s count' % plugin.name):
            # Get the count.
            list_count = int(settings.value('%s count' % plugin.name, 0))
            if list_count:
                for counter in range(list_count):
                    # The keys were named e. g.: "image 0"
                    item = settings.value('%s %d' % (plugin.name, counter), '')
                    if item:
                        files_list.append(item)
                    settings.remove('%s %d' % (plugin.name, counter))
            settings.remove('%s count' % plugin.name)
        settings.endGroup()
        return files_list
