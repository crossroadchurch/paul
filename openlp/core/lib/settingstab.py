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
The :mod:`~openlp.core.lib.settingstab` module contains the base SettingsTab class which plugins use for adding their
own tab to the settings dialog.
"""


from PyQt4 import QtGui


from openlp.core.common import RegistryProperties


class SettingsTab(QtGui.QWidget, RegistryProperties):
    """
    SettingsTab is a helper widget for plugins to define Tabs for the settings dialog.
    """
    def __init__(self, parent, title, visible_title=None, icon_path=None):
        """
        Constructor to create the Settings tab item.

        :param parent:
        :param title: The title of the tab, which is used internally for the tab handling.
        :param visible_title: The title of the tab, which is usually displayed on the tab.
        :param icon_path:
        """
        super(SettingsTab, self).__init__(parent)
        self.tab_title = title
        self.tab_title_visible = visible_title
        self.settings_section = self.tab_title.lower()
        self.tab_visited = False
        if icon_path:
            self.icon_path = icon_path
        self._setup()

    def _setup(self):
        """
        Run some initial setup. This method is separate from __init__ in order to mock it out in tests.
        """
        self.setupUi()
        self.retranslateUi()
        self.initialise()
        self.load()

    def setupUi(self):
        """
        Setup the tab's interface.
        """
        self.tab_layout = QtGui.QHBoxLayout(self)
        self.tab_layout.setObjectName('tab_layout')
        self.left_column = QtGui.QWidget(self)
        self.left_column.setObjectName('left_column')
        self.left_layout = QtGui.QVBoxLayout(self.left_column)
        self.left_layout.setMargin(0)
        self.left_layout.setObjectName('left_layout')
        self.tab_layout.addWidget(self.left_column)
        self.right_column = QtGui.QWidget(self)
        self.right_column.setObjectName('right_column')
        self.right_layout = QtGui.QVBoxLayout(self.right_column)
        self.right_layout.setMargin(0)
        self.right_layout.setObjectName('right_layout')
        self.tab_layout.addWidget(self.right_column)

    def resizeEvent(self, event=None):
        """
        Resize the sides in two equal halves if the layout allows this.
        """
        if event:
            QtGui.QWidget.resizeEvent(self, event)
        width = self.width() - self.tab_layout.spacing() - \
            self.tab_layout.contentsMargins().left() - self.tab_layout.contentsMargins().right()
        left_width = min(width - self.right_column.minimumSizeHint().width(), width // 2)
        left_width = max(left_width, self.left_column.minimumSizeHint().width())
        self.left_column.setFixedWidth(left_width)

    def retranslateUi(self):
        """
        Setup the interface translation strings.
        """
        pass

    def initialise(self):
        """
        Do any extra initialisation here.
        """
        pass

    def load(self):
        """
        Load settings from disk.
        """
        pass

    def save(self):
        """
        Save settings to disk.
        """
        pass

    def cancel(self):
        """
        Reset any settings if cancel triggered
        """
        self.load()

    def post_set_up(self, post_update=False):
        """
        Changes which need to be made after setup of application

        :param post_update: Indicates if called before or after updates.
        """
        pass

    def tab_visible(self):
        """
        Tab has just been made visible to the user
        """
        self.tab_visited = True
