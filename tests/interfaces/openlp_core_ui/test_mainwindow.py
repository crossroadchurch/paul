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
Package to test the openlp.core.ui.mainwindow package.
"""
from unittest import TestCase


from openlp.core.common import Registry
from openlp.core.ui.mainwindow import MainWindow
from tests.interfaces import MagicMock, patch
from tests.helpers.testmixin import TestMixin


class TestMainWindow(TestCase, TestMixin):

    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.registry = Registry()
        self.setup_application()
        # Mock cursor busy/normal methods.
        self.app.set_busy_cursor = MagicMock()
        self.app.set_normal_cursor = MagicMock()
        self.app.args = []
        Registry().register('application', self.app)
        # Mock classes and methods used by mainwindow.
        with patch('openlp.core.ui.mainwindow.SettingsForm') as mocked_settings_form, \
                patch('openlp.core.ui.mainwindow.ImageManager') as mocked_image_manager, \
                patch('openlp.core.ui.mainwindow.LiveController') as mocked_live_controller, \
                patch('openlp.core.ui.mainwindow.PreviewController') as mocked_preview_controller, \
                patch('openlp.core.ui.mainwindow.OpenLPDockWidget') as mocked_dock_widget, \
                patch('openlp.core.ui.mainwindow.QtGui.QToolBox') as mocked_q_tool_box_class, \
                patch('openlp.core.ui.mainwindow.QtGui.QMainWindow.addDockWidget') as mocked_add_dock_method, \
                patch('openlp.core.ui.mainwindow.ServiceManager') as mocked_service_manager, \
                patch('openlp.core.ui.mainwindow.ThemeManager') as mocked_theme_manager, \
                patch('openlp.core.ui.mainwindow.ProjectorManager') as mocked_projector_manager, \
                patch('openlp.core.ui.mainwindow.Renderer') as mocked_renderer:
            self.main_window = MainWindow()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.main_window

    def restore_current_media_manager_item_test(self):
        """
        Regression test for bug #1152509.
        """
        # GIVEN: Mocked Settings().value method.
        with patch('openlp.core.ui.mainwindow.Settings.value') as mocked_value:
            # save current plugin: True; current media plugin: 2
            mocked_value.side_effect = [True, 2]

            # WHEN: Call the restore method.
            self.main_window.restore_current_media_manager_item()

            # THEN: The current widget should have been set.
            self.main_window.media_tool_box.setCurrentIndex.assert_called_with(2)

    def projector_manager_dock_locked_test(self):
        """
        Projector Manager enable UI options -  bug #1390702
        """
        # GIVEN: A mocked projector manager dock item:
        projector_dock = self.main_window.projector_manager_dock

        # WHEN: main_window.lock_panel action is triggered
        self.main_window.lock_panel.triggered.emit(True)

        # THEN: Projector manager dock should have been called with disable UI features
        projector_dock.setFeatures.assert_called_with(0)

    def projector_manager_dock_unlocked_test(self):
        """
        Projector Manager disable UI options -  bug #1390702
        """
        # GIVEN: A mocked projector manager dock item:
        projector_dock = self.main_window.projector_manager_dock

        # WHEN: main_window.lock_panel action is triggered
        self.main_window.lock_panel.triggered.emit(False)

        # THEN: Projector manager dock should have been called with enable UI features
        projector_dock.setFeatures.assert_called_with(7)
