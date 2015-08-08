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
The :mod:`screen` module provides management functionality for a machines'
displays.
"""

import logging
import copy

from PyQt4 import QtCore

from openlp.core.common import Registry, Settings, translate

log = logging.getLogger(__name__)


class ScreenList(object):
    """
    Wrapper to handle the parameters of the display screen.

    To get access to the screen list call ``ScreenList()``.
    """
    log.info('Screen loaded')
    __instance__ = None

    def __new__(cls):
        """
        Re-implement __new__ to create a true singleton.
        """
        if not cls.__instance__:
            cls.__instance__ = object.__new__(cls)
        return cls.__instance__

    @classmethod
    def create(cls, desktop):
        """
        Initialise the screen list.

        :param desktop:  A QDesktopWidget object.
        """
        screen_list = cls()
        screen_list.desktop = desktop
        screen_list.preview = None
        screen_list.current = None
        screen_list.override = None
        screen_list.screen_list = []
        screen_list.display_count = 0
        screen_list.screen_count_changed()
        screen_list.load_screen_settings()
        desktop.resized.connect(screen_list.screen_resolution_changed)
        desktop.screenCountChanged.connect(screen_list.screen_count_changed)
        return screen_list

    def screen_resolution_changed(self, number):
        """
        Called when the resolution of a screen has changed.

        ``number``
            The number of the screen, which size has changed.
        """
        log.info('screen_resolution_changed %d' % number)
        for screen in self.screen_list:
            if number == screen['number']:
                new_screen = {
                    'number': number,
                    'size': self.desktop.screenGeometry(number),
                    'primary': self.desktop.primaryScreen() == number
                }
                self.remove_screen(number)
                self.add_screen(new_screen)
                # The screen's default size is used, that is why we have to
                # update the override screen.
                if screen == self.override:
                    self.override = copy.deepcopy(new_screen)
                    self.set_override_display()
                Registry().execute('config_screen_changed')
                break

    def screen_count_changed(self, changed_screen=-1):
        """
        Called when a screen has been added or removed.

        ``changed_screen``
            The screen's number which has been (un)plugged.
        """
        # Do not log at start up.
        if changed_screen != -1:
            log.info('screen_count_changed %d' % self.desktop.screenCount())
        # Remove unplugged screens.
        for screen in copy.deepcopy(self.screen_list):
            if screen['number'] == self.desktop.screenCount():
                self.remove_screen(screen['number'])
        # Add new screens.
        for number in range(self.desktop.screenCount()):
            if not self.screen_exists(number):
                self.add_screen({
                    'number': number,
                    'size': self.desktop.screenGeometry(number),
                    'primary': (self.desktop.primaryScreen() == number)
                })
        # We do not want to send this message at start up.
        if changed_screen != -1:
            # Reload setting tabs to apply possible changes.
            Registry().execute('config_screen_changed')

    def get_screen_list(self):
        """
        Returns a list with the screens. This should only be used to display
        available screens to the user::

            ['Screen 1 (primary)', 'Screen 2']
        """
        screen_list = []
        for screen in self.screen_list:
            screen_name = '%s %d' % (translate('OpenLP.ScreenList', 'Screen'), screen['number'] + 1)
            if screen['primary']:
                screen_name = '%s (%s)' % (screen_name, translate('OpenLP.ScreenList', 'primary'))
            screen_list.append(screen_name)
        return screen_list

    def add_screen(self, screen):
        """
        Add a screen to the list of known screens.

        :param screen: A dict with the screen properties::

                {
                    'primary': True,
                    'number': 0,
                    'size': PyQt4.QtCore.QRect(0, 0, 1024, 768)
                }
        """
        log.info('Screen %d found with resolution %s' % (screen['number'], screen['size']))
        if screen['primary']:
            self.current = screen
            self.override = copy.deepcopy(self.current)
        self.screen_list.append(screen)
        self.display_count += 1

    def remove_screen(self, number):
        """
        Remove a screen from the list of known screens.

        :param number: The screen number (int).
        """
        log.info('remove_screen %d' % number)
        for screen in self.screen_list:
            if screen['number'] == number:
                self.screen_list.remove(screen)
                self.display_count -= 1
                break

    def screen_exists(self, number):
        """
        Confirms a screen is known.

        :param number: The screen number (int).
        """
        for screen in self.screen_list:
            if screen['number'] == number:
                return True
        return False

    def set_current_display(self, number):
        """
        Set up the current screen dimensions.

        :param number: The screen number (int).
        """
        log.debug('set_current_display %s' % number)
        if number + 1 > self.display_count:
            self.current = self.screen_list[0]
        else:
            self.current = self.screen_list[number]
            self.preview = copy.deepcopy(self.current)
        self.override = copy.deepcopy(self.current)
        if self.display_count == 1:
            self.preview = self.screen_list[0]

    def set_override_display(self):
        """
        Replace the current size with the override values, as the user wants to have their own screen attributes.
        """
        log.debug('set_override_display')
        self.current = copy.deepcopy(self.override)
        self.preview = copy.deepcopy(self.current)

    def reset_current_display(self):
        """
        Replace the current values with the correct values, as the user wants to use the correct screen attributes.
        """
        log.debug('reset_current_display')
        self.set_current_display(self.current['number'])

    def which_screen(self, window):
        """
        Return the screen number that the centre of the passed window is in.

        :param window: A QWidget we are finding the location of.
        """
        x = window.x() + (window.width() // 2)
        y = window.y() + (window.height() // 2)
        for screen in self.screen_list:
            size = screen['size']
            if x >= size.x() and x <= (size.x() + size.width()) and y >= size.y() and y <= (size.y() + size.height()):
                return screen['number']

    def load_screen_settings(self):
        """
        Loads the screen size and the monitor number from the settings.
        """
        # Add the screen settings to the settings dict. This has to be done here due to cyclic dependency.
        # Do not do this anywhere else.
        screen_settings = {
            'core/x position': self.current['size'].x(),
            'core/y position': self.current['size'].y(),
            'core/monitor': self.display_count - 1,
            'core/height': self.current['size'].height(),
            'core/width': self.current['size'].width()
        }
        Settings.extend_default_settings(screen_settings)
        settings = Settings()
        settings.beginGroup('core')
        monitor = settings.value('monitor')
        self.set_current_display(monitor)
        self.display = settings.value('display on monitor')
        override_display = settings.value('override position')
        x = settings.value('x position')
        y = settings.value('y position')
        width = settings.value('width')
        height = settings.value('height')
        self.override['size'] = QtCore.QRect(x, y, width, height)
        self.override['primary'] = False
        settings.endGroup()
        if override_display:
            self.set_override_display()
        else:
            self.reset_current_display()
