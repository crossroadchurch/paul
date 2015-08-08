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

from PyQt4 import QtGui

from openlp.core.lib import Plugin, StringContent, build_icon, translate
from openlp.core.lib.ui import UiStrings, create_action
from openlp.core.utils.actions import ActionList
from openlp.plugins.bibles.lib import BibleManager, BiblesTab, BibleMediaItem, LayoutStyle, DisplayStyle, \
    LanguageSelection
from openlp.plugins.bibles.lib.mediaitem import BibleSearch
from openlp.plugins.bibles.forms import BibleUpgradeForm

log = logging.getLogger(__name__)


__default_settings__ = {
    'bibles/db type': 'sqlite',
    'bibles/db username': '',
    'bibles/db password': '',
    'bibles/db hostname': '',
    'bibles/db database': '',
    'bibles/last search type': BibleSearch.Reference,
    'bibles/verse layout style': LayoutStyle.VersePerSlide,
    'bibles/book name language': LanguageSelection.Bible,
    'bibles/display brackets': DisplayStyle.NoBrackets,
    'bibles/is verse number visible': True,
    'bibles/display new chapter': False,
    'bibles/second bibles': True,
    'bibles/advanced bible': '',
    'bibles/quick bible': '',
    'bibles/proxy name': '',
    'bibles/proxy address': '',
    'bibles/proxy username': '',
    'bibles/proxy password': '',
    'bibles/bible theme': '',
    'bibles/verse separator': '',
    'bibles/range separator': '',
    'bibles/list separator': '',
    'bibles/end separator': '',
    'bibles/last directory import': ''
}


class BiblePlugin(Plugin):
    """
    The Bible plugin provides a plugin for managing and displaying Bibles.
    """
    log.info('Bible Plugin loaded')

    def __init__(self):
        super(BiblePlugin, self).__init__('bibles', __default_settings__, BibleMediaItem, BiblesTab)
        self.weight = -9
        self.icon_path = ':/plugins/plugin_bibles.png'
        self.icon = build_icon(self.icon_path)
        self.manager = BibleManager(self)

    def initialise(self):
        """
        Initialise the Bible plugin.
        """
        log.info('bibles Initialising')
        super(BiblePlugin, self).initialise()
        self.import_bible_item.setVisible(True)
        action_list = ActionList.get_instance()
        action_list.add_action(self.import_bible_item, UiStrings().Import)
        # Set to invisible until we can export bibles
        self.export_bible_item.setVisible(False)
        self.tools_upgrade_item.setVisible(bool(self.manager.old_bible_databases))

    def finalise(self):
        """
        Tidy up on exit
        """
        log.info('Plugin Finalise')
        self.manager.finalise()
        Plugin.finalise(self)
        action_list = ActionList.get_instance()
        action_list.remove_action(self.import_bible_item, UiStrings().Import)
        self.import_bible_item.setVisible(False)
        self.export_bible_item.setVisible(False)

    def app_startup(self):
        """
        Perform tasks on application startup
        """
        super(BiblePlugin, self).app_startup()
        if self.manager.old_bible_databases:
            if QtGui.QMessageBox.information(
                    self.main_window, translate('OpenLP', 'Information'),
                    translate('OpenLP', 'Bible format has changed.\nYou have to upgrade your '
                                        'existing Bibles.\nShould OpenLP upgrade now?'),
                    QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)) == \
                    QtGui.QMessageBox.Yes:
                self.on_tools_upgrade_item_triggered()

    def add_import_menu_item(self, import_menu):
        """
        Add an import menu item

        :param import_menu: The menu to insert the menu item into.
        """
        self.import_bible_item = create_action(import_menu, 'importBibleItem',
                                               text=translate('BiblesPlugin', '&Bible'), visible=False,
                                               triggers=self.on_bible_import_click)
        import_menu.addAction(self.import_bible_item)

    def add_export_menu_item(self, export_menu):
        """
        Add an export menu item

        :param export_menu: The menu to insert the menu item into.
        """
        self.export_bible_item = create_action(export_menu, 'exportBibleItem',
                                               text=translate('BiblesPlugin', '&Bible'), visible=False)
        export_menu.addAction(self.export_bible_item)

    def add_tools_menu_item(self, tools_menu):
        """
        Give the bible plugin the opportunity to add items to the **Tools** menu.

        :param tools_menu:  The actual **Tools** menu item, so that your actions can use it as their parent.
        """
        log.debug('add tools menu')
        self.tools_upgrade_item = create_action(
            tools_menu, 'toolsUpgradeItem',
            text=translate('BiblesPlugin', '&Upgrade older Bibles'),
            statustip=translate('BiblesPlugin', 'Upgrade the Bible databases to the latest format.'),
            visible=False, triggers=self.on_tools_upgrade_item_triggered)
        tools_menu.addAction(self.tools_upgrade_item)

    def on_tools_upgrade_item_triggered(self):
        """
        Upgrade older bible databases.
        """
        if not hasattr(self, 'upgrade_wizard'):
            self.upgrade_wizard = BibleUpgradeForm(self.main_window, self.manager, self)
        # If the import was not cancelled then reload.
        if self.upgrade_wizard.exec_():
            self.media_item.reload_bibles()

    def on_bible_import_click(self):
        """
        Show the Bible Import wizard
        """
        if self.media_item:
            self.media_item.on_import_click()

    def about(self):
        """
        Return the about text for the plugin manager
        """
        about_text = translate('BiblesPlugin', '<strong>Bible Plugin</strong>'
                               '<br />The Bible plugin provides the ability to display Bible '
                               'verses from different sources during the service.')
        return about_text

    def uses_theme(self, theme):
        """
        Called to find out if the bible plugin is currently using a theme. Returns ``True`` if the theme is being used,
        otherwise returns ``False``.

        :param theme: The theme
        """
        return str(self.settings_tab.bible_theme) == theme

    def rename_theme(self, old_theme, new_theme):
        """
        Rename the theme the bible plugin is using making the plugin use the
        new name.

        :param old_theme: The name of the theme the plugin should stop using. Unused for this particular plugin.
        :param new_theme:  The new name the plugin should now use.
        """
        self.settings_tab.bible_theme = new_theme
        self.settings_tab.save()

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('BiblesPlugin', 'Bible', 'name singular'),
            'plural': translate('BiblesPlugin', 'Bibles', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('BiblesPlugin', 'Bibles', 'container title')
        }
        # Middle Header Bar
        tooltips = {
            'load': '',
            'import': translate('BiblesPlugin', 'Import a Bible.'),
            'new': translate('BiblesPlugin', 'Add a new Bible.'),
            'edit': translate('BiblesPlugin', 'Edit the selected Bible.'),
            'delete': translate('BiblesPlugin', 'Delete the selected Bible.'),
            'preview': translate('BiblesPlugin', 'Preview the selected Bible.'),
            'live': translate('BiblesPlugin', 'Send the selected Bible live.'),
            'service': translate('BiblesPlugin', 'Add the selected Bible to the service.')
        }
        self.set_plugin_ui_text_strings(tooltips)
