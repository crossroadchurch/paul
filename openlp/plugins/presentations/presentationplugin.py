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
The :mod:`presentationplugin` module provides the ability for OpenLP to display presentations from a variety of document
formats.
"""
import os
import logging

from PyQt4 import QtCore

from openlp.core.common import AppLocation, Settings, translate
from openlp.core.lib import Plugin, StringContent, build_icon
from openlp.plugins.presentations.lib import PresentationController, PresentationMediaItem, PresentationTab


log = logging.getLogger(__name__)


__default_settings__ = {'presentations/override app': QtCore.Qt.Unchecked,
                        'presentations/enable_pdf_program': QtCore.Qt.Unchecked,
                        'presentations/pdf_program': '',
                        'presentations/Impress': QtCore.Qt.Checked,
                        'presentations/Powerpoint': QtCore.Qt.Checked,
                        'presentations/Powerpoint Viewer': QtCore.Qt.Checked,
                        'presentations/Pdf': QtCore.Qt.Checked,
                        'presentations/presentations files': [],
                        'presentations/thumbnail_scheme': '',
                        'presentations/powerpoint slide click advance': QtCore.Qt.Unchecked,
                        'presentations/powerpoint control window': QtCore.Qt.Unchecked
                        }


class PresentationPlugin(Plugin):
    """
    This plugin allowed a Presentation to be opened, controlled and displayed on the output display. The plugin controls
    third party applications such as OpenOffice.org Impress, Microsoft PowerPoint and the PowerPoint viewer.
    """
    log = logging.getLogger('PresentationPlugin')

    def __init__(self):
        """
        PluginPresentation constructor.
        """
        log.debug('Initialised')
        self.controllers = {}
        Plugin.__init__(self, 'presentations', __default_settings__, __default_settings__)
        self.weight = -8
        self.icon_path = ':/plugins/plugin_presentations.png'
        self.icon = build_icon(self.icon_path)

    def create_settings_tab(self, parent):
        """
        Create the settings Tab.
        """
        visible_name = self.get_string(StringContent.VisibleName)
        self.settings_tab = PresentationTab(parent, self.name, visible_name['title'], self.controllers, self.icon_path)

    def initialise(self):
        """
        Initialise the plugin. Determine which controllers are enabled are start their processes.
        """
        log.info('Presentations Initialising')
        super(PresentationPlugin, self).initialise()
        for controller in self.controllers:
            if self.controllers[controller].enabled():
                try:
                    self.controllers[controller].start_process()
                except Exception:
                    log.warning('Failed to start controller process')
                    self.controllers[controller].available = False
        self.media_item.build_file_mask_string()

    def finalise(self):
        """
        Finalise the plugin. Ask all the enabled presentation applications to close down their applications and release
        resources.
        """
        log.info('Plugin Finalise')
        # Ask each controller to tidy up.
        for key in self.controllers:
            controller = self.controllers[key]
            if controller.enabled():
                controller.kill()
        super(PresentationPlugin, self).finalise()

    def create_media_manager_item(self):
        """
        Create the Media Manager List.
        """
        self.media_item = PresentationMediaItem(self.main_window.media_dock_manager.media_dock, self, self.controllers)

    def register_controllers(self, controller):
        """
        Register each presentation controller (Impress, PPT etc) and store for later use.
        """
        self.controllers[controller.name] = controller

    def check_pre_conditions(self):
        """
        Check to see if we have any presentation software available. If not do not install the plugin.
        """
        log.debug('check_pre_conditions')
        controller_dir = os.path.join(AppLocation.get_directory(AppLocation.PluginsDir), 'presentations', 'lib')
        for filename in os.listdir(controller_dir):
            if filename.endswith('controller.py') and not filename == 'presentationcontroller.py':
                path = os.path.join(controller_dir, filename)
                if os.path.isfile(path):
                    module_name = 'openlp.plugins.presentations.lib.' + os.path.splitext(filename)[0]
                    log.debug('Importing controller %s', module_name)
                    try:
                        __import__(module_name, globals(), locals(), [])
                    except ImportError:
                        log.warning('Failed to import %s on path %s', module_name, path)
        controller_classes = PresentationController.__subclasses__()
        for controller_class in controller_classes:
            controller = controller_class(self)
            self.register_controllers(controller)
        return bool(self.controllers)

    def app_startup(self):
        """
        Perform tasks on application startup.
        """
        # TODO: Can be removed when the upgrade path from 2.0.x to 2.2.x is no longer needed
        super().app_startup()
        files_from_config = Settings().value('presentations/presentations files')
        for file in files_from_config:
            try:
                self.media_item.clean_up_thumbnails(file, True)
            except AttributeError:
                pass
        self.media_item.list_view.clear()
        Settings().setValue('presentations/thumbnail_scheme', 'md5')
        self.media_item.validate_and_load(files_from_config)

    def about(self):
        """
        Return information about this plugin.
        """
        about_text = translate('PresentationPlugin', '<strong>Presentation '
                               'Plugin</strong><br />The presentation plugin provides the '
                               'ability to show presentations using a number of different '
                               'programs. The choice of available presentation programs is '
                               'available to the user in a drop down box.')
        return about_text

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin.
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('PresentationPlugin', 'Presentation', 'name singular'),
            'plural': translate('PresentationPlugin', 'Presentations', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('PresentationPlugin', 'Presentations', 'container title')
        }
        # Middle Header Bar
        tooltips = {
            'load': translate('PresentationPlugin', 'Load a new presentation.'),
            'import': '',
            'new': '',
            'edit': '',
            'delete': translate('PresentationPlugin', 'Delete the selected presentation.'),
            'preview': translate('PresentationPlugin', 'Preview the selected presentation.'),
            'live': translate('PresentationPlugin', 'Send the selected presentation live.'),
            'service': translate('PresentationPlugin', 'Add the selected presentation to the service.')
        }
        self.set_plugin_ui_text_strings(tooltips)
