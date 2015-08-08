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
Provide common toolbar handling for OpenLP
"""
import logging

from PyQt4 import QtCore, QtGui

from openlp.core.lib.ui import create_widget_action

log = logging.getLogger(__name__)


class OpenLPToolbar(QtGui.QToolBar):
    """
    Lots of toolbars around the place, so it makes sense to have a common way to manage them. This is the base toolbar
    class.
    """
    def __init__(self, parent):
        """
        Initialise the toolbar.
        """
        super(OpenLPToolbar, self).__init__(parent)
        # useful to be able to reuse button icons...
        self.setIconSize(QtCore.QSize(20, 20))
        self.actions = {}
        log.debug('Init done for %s' % parent.__class__.__name__)

    def add_toolbar_action(self, name, **kwargs):
        """
        A method to help developers easily add a button to the toolbar. A new QAction is created by calling
        ``create_action()``. The action is added to the toolbar and the toolbar is set as parent. For more details
        please look at openlp.core.lib.ui.create_action()
        """
        action = create_widget_action(self, name, **kwargs)
        self.actions[name] = action
        return action

    def add_toolbar_widget(self, widget):
        """
        Add a widget and store it's handle under the widgets object name.
        """
        action = self.addWidget(widget)
        self.actions[widget.objectName()] = action

    def set_widget_visible(self, widgets, visible=True):
        """
        Set the visibility for a widget or a list of widgets.

        :param widgets: A list of string with widget object names.
        :param visible: The new state as bool.
        """
        for handle in widgets:
            if handle in self.actions:
                self.actions[handle].setVisible(visible)
            else:
                log.warning('No handle "%s" in actions list.', str(handle))

    def set_widget_enabled(self, widgets, enabled=True):
        """
        Set the enabled state for a widget or a list of widgets.

        :param widgets: A list of string with widget object names.
        :param enabled: The new state as bool.
        """
        for handle in widgets:
            if handle in self.actions:
                self.actions[handle].setEnabled(enabled)
            else:
                log.warning('No handle "%s" in actions list.', str(handle))
