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

from openlp.core.common import Settings, translate
from openlp.core.lib import Plugin, StringContent, build_icon
from openlp.core.lib.db import Manager
from openlp.core.lib.ui import create_action, UiStrings
from openlp.core.lib.theme import VerticalType
from openlp.core.ui import AlertLocation
from openlp.core.utils.actions import ActionList
from openlp.plugins.alerts.lib import AlertsManager, AlertsTab
from openlp.plugins.alerts.lib.db import init_schema
from openlp.plugins.alerts.forms import AlertForm

log = logging.getLogger(__name__)

JAVASCRIPT = """
    function show_alert(alerttext, position){
        var text = document.getElementById('alert');
        text.innerHTML = alerttext;
        if(alerttext == '') {
            text.style.visibility = 'hidden';
            return 0;
        }
        if(position == ''){
            position = getComputedStyle(text, '').verticalAlign;
        }
        switch(position)
        {
            case 'top':
                text.style.top = '0px';
                break;
            case 'middle':
                text.style.top = ((window.innerHeight - text.clientHeight) / 2)
                    + 'px';
                break;
            case 'bottom':
                text.style.top = (window.innerHeight - text.clientHeight)
                    + 'px';
                break;
        }
        text.style.visibility = 'visible';
        return text.clientHeight;
    }

    function update_css(align, font, size, color, bgcolor){
        var text = document.getElementById('alert');
        text.style.fontSize = size + "pt";
        text.style.fontFamily = font;
        text.style.color = color;
        text.style.backgroundColor = bgcolor;
        switch(align)
        {
            case 'top':
                text.style.top = '0px';
                break;
            case 'middle':
                text.style.top = ((window.innerHeight - text.clientHeight) / 2)
                    + 'px';
                break;
            case 'bottom':
                text.style.top = (window.innerHeight - text.clientHeight)
                    + 'px';
                break;
        }
    }
"""
CSS = """
    #alert {
        position: absolute;
        left: 0px;
        top: 0px;
        z-index: 10;
        width: 100%%;
        vertical-align: %s;
        font-family: %s;
        font-size: %spt;
        color: %s;
        background-color: %s;
        word-wrap: break-word;
    }
"""

HTML = """
    <div id="alert" style="visibility:hidden"></div>
"""

__default_settings__ = {
    'alerts/font face': QtGui.QFont().family(),
    'alerts/font size': 40,
    'alerts/db type': 'sqlite',
    'alerts/db username': '',
    'alerts/db password': '',
    'alerts/db hostname': '',
    'alerts/db database': '',
    'alerts/location': AlertLocation.Bottom,
    'alerts/background color': '#660000',
    'alerts/font color': '#ffffff',
    'alerts/timeout': 5
}


class AlertsPlugin(Plugin):
    """
    The Alerts Plugin Class
    """
    log.info('Alerts Plugin loaded')

    def __init__(self):
        """
        Class __init__ method
        """
        super(AlertsPlugin, self).__init__('alerts', __default_settings__, settings_tab_class=AlertsTab)
        self.weight = -3
        self.icon_path = ':/plugins/plugin_alerts.png'
        self.icon = build_icon(self.icon_path)
        AlertsManager(self)
        self.manager = Manager('alerts', init_schema)
        self.alert_form = AlertForm(self)

    def add_tools_menu_item(self, tools_menu):
        """
        Give the alerts plugin the opportunity to add items to the **Tools** menu.

        :param tools_menu: The actual **Tools** menu item, so that your actions can use it as their parent.
        """
        log.info('add tools menu')
        self.tools_alert_item = create_action(tools_menu, 'toolsAlertItem',
                                              text=translate('AlertsPlugin', '&Alert'),
                                              icon=':/plugins/plugin_alerts.png',
                                              statustip=translate('AlertsPlugin', 'Show an alert message.'),
                                              visible=False, can_shortcuts=True, triggers=self.on_alerts_trigger)
        self.main_window.tools_menu.addAction(self.tools_alert_item)

    def initialise(self):
        """
        Initialise plugin
        """
        log.info('Alerts Initialising')
        super(AlertsPlugin, self).initialise()
        self.tools_alert_item.setVisible(True)
        action_list = ActionList.get_instance()
        action_list.add_action(self.tools_alert_item, UiStrings().Tools)

    def finalise(self):
        """
        Tidy up on exit
        """
        log.info('Alerts Finalising')
        self.manager.finalise()
        super(AlertsPlugin, self).finalise()
        self.tools_alert_item.setVisible(False)
        action_list = ActionList.get_instance()
        action_list.remove_action(self.tools_alert_item, 'Tools')

    def toggle_alerts_state(self):
        """
        Switch the alerts state
        """
        self.alerts_active = not self.alerts_active
        Settings().setValue(self.settings_section + '/active', self.alerts_active)

    def on_alerts_trigger(self):
        """
        Start of the Alerts dialog triggered from the main menu.
        """
        self.alert_form.load_list()
        self.alert_form.exec_()

    def about(self):
        """
        Plugin Alerts about method

        :return: text
        """
        about_text = translate('AlertsPlugin', '<strong>Alerts Plugin</strong>'
                               '<br />The alert plugin controls the displaying of alerts on the display screen.')
        return about_text

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('AlertsPlugin', 'Alert', 'name singular'),
            'plural': translate('AlertsPlugin', 'Alerts', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('AlertsPlugin', 'Alerts', 'container title')
        }

    def get_display_javascript(self):
        """
        Add Javascript to the main display.
        """
        return JAVASCRIPT

    def get_display_css(self):
        """
        Add CSS to the main display.
        """
        align = VerticalType.Names[self.settings_tab.location]
        return CSS % (align, self.settings_tab.font_face, self.settings_tab.font_size, self.settings_tab.font_color,
                      self.settings_tab.background_color)

    def get_display_html(self):
        """
        Add HTML to the main display.
        """
        return HTML

    def refresh_css(self, frame):
        """
        Trigger an update of the CSS in the main display.

        :param frame: The Web frame holding the page.
        """
        align = VerticalType.Names[self.settings_tab.location]
        frame.evaluateJavaScript('update_css("%s", "%s", "%s", "%s", "%s")' %
                                 (align, self.settings_tab.font_face, self.settings_tab.font_size,
                                  self.settings_tab.font_color, self.settings_tab.background_color))
