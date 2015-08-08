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
The :mod:`~openlp.plugins.custom.customplugin` module contains the Plugin class
for the Custom Slides plugin.
"""

import logging

from openlp.core.lib import Plugin, StringContent, build_icon, translate
from openlp.core.lib.db import Manager
from openlp.plugins.custom.lib import CustomMediaItem, CustomTab
from openlp.plugins.custom.lib.db import CustomSlide, init_schema
from openlp.plugins.custom.lib.mediaitem import CustomSearch

log = logging.getLogger(__name__)

__default_settings__ = {
    'custom/db type': 'sqlite',
    'custom/db username': '',
    'custom/db password': '',
    'custom/db hostname': '',
    'custom/db database': '',
    'custom/last search type': CustomSearch.Titles,
    'custom/display footer': True,
    'custom/add custom from service': True
}


class CustomPlugin(Plugin):
    """
    This plugin enables the user to create, edit and display custom slide shows. Custom shows are divided into slides.
    Each show is able to have it's own theme.
    Custom shows are designed to replace the use of songs where the songs plugin has become restrictive.
    Examples could be Welcome slides, Bible Reading information, Orders of service.
    """
    log.info('Custom Plugin loaded')

    def __init__(self):
        super(CustomPlugin, self).__init__('custom', __default_settings__, CustomMediaItem, CustomTab)
        self.weight = -5
        self.db_manager = Manager('custom', init_schema)
        self.icon_path = ':/plugins/plugin_custom.png'
        self.icon = build_icon(self.icon_path)

    def about(self):
        about_text = translate('CustomPlugin', '<strong>Custom Slide Plugin </strong><br />The custom slide plugin '
                               'provides the ability to set up custom text slides that can be displayed on the screen '
                               'the same way songs are. This plugin provides greater freedom over the songs plugin.')
        return about_text

    def uses_theme(self, theme):
        """
        Called to find out if the custom plugin is currently using a theme.

        Returns True if the theme is being used, otherwise returns False.
        """
        if self.db_manager.get_all_objects(CustomSlide, CustomSlide.theme_name == theme):
            return True
        return False

    def rename_theme(self, old_theme, new_theme):
        """
        Renames a theme the custom plugin is using making the plugin use the new name.

        :param old_theme: The name of the theme the plugin should stop using.
        :param new_theme: The new name the plugin should now use.
        """
        customs_using_theme = self.db_manager.get_all_objects(CustomSlide, CustomSlide.theme_name == old_theme)
        for custom in customs_using_theme:
            custom.theme_name = new_theme
            self.db_manager.save_object(custom)

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('CustomPlugin', 'Custom Slide', 'name singular'),
            'plural': translate('CustomPlugin', 'Custom Slides', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('CustomPlugin', 'Custom Slides', 'container title')
        }
        # Middle Header Bar
        tooltips = {
            'load': translate('CustomPlugin', 'Load a new custom slide.'),
            'import': translate('CustomPlugin', 'Import a custom slide.'),
            'new': translate('CustomPlugin', 'Add a new custom slide.'),
            'edit': translate('CustomPlugin', 'Edit the selected custom slide.'),
            'delete': translate('CustomPlugin', 'Delete the selected custom slide.'),
            'preview': translate('CustomPlugin', 'Preview the selected custom slide.'),
            'live': translate('CustomPlugin', 'Send the selected custom slide live.'),
            'service': translate('CustomPlugin', 'Add the selected custom slide to the service.')
        }
        self.set_plugin_ui_text_strings(tooltips)

    def finalise(self):
        """
        Time to tidy up on exit
        """
        log.info('Custom Finalising')
        self.db_manager.finalise()
        Plugin.finalise(self)
