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
This module contains tests for the openlp.core.lib.filedialog module
"""
from unittest import TestCase

from openlp.core.lib.colorbutton import ColorButton
from tests.functional import MagicMock, call, patch


class TestColorDialog(TestCase):
    """
    Test the :class:`~openlp.core.lib.colorbutton.ColorButton` class
    """
    def setUp(self):
        self.change_color_patcher = patch('openlp.core.lib.colorbutton.ColorButton.change_color')
        self.clicked_patcher = patch('openlp.core.lib.colorbutton.ColorButton.clicked')
        self.color_changed_patcher = patch('openlp.core.lib.colorbutton.ColorButton.colorChanged')
        self.qt_gui_patcher = patch('openlp.core.lib.colorbutton.QtGui')
        self.translate_patcher = patch('openlp.core.lib.colorbutton.translate', **{'return_value': 'Tool Tip Text'})
        self.addCleanup(self.change_color_patcher.stop)
        self.addCleanup(self.clicked_patcher.stop)
        self.addCleanup(self.color_changed_patcher.stop)
        self.addCleanup(self.qt_gui_patcher.stop)
        self.addCleanup(self.translate_patcher.stop)
        self.mocked_change_color = self.change_color_patcher.start()
        self.mocked_clicked = self.clicked_patcher.start()
        self.mocked_color_changed = self.color_changed_patcher.start()
        self.mocked_qt_gui = self.qt_gui_patcher.start()
        self.mocked_translate = self.translate_patcher.start()

    def constructor_test(self):
        """
        Test that constructing a ColorButton object works correctly
        """

        # GIVEN: The ColorButton class, a mocked change_color, setToolTip methods and clicked signal
        with patch('openlp.core.lib.colorbutton.ColorButton.setToolTip') as mocked_set_tool_tip:

            # WHEN: The ColorButton object is instantiated
            widget = ColorButton()

            # THEN: The widget __init__ method should have the correct properties and methods called
            self.assertEqual(widget.parent, None,
                             'The parent should be the same as the one that the class was instianted with')
            self.mocked_change_color.assert_called_once_with('#ffffff')
            mocked_set_tool_tip.assert_called_once_with('Tool Tip Text')
            self.mocked_clicked.connect.assert_called_once_with(widget.on_clicked)

    def change_color_test(self):
        """
        Test that change_color sets the new color and the stylesheet
        """
        self.change_color_patcher.stop()

        # GIVEN: An instance of the ColorButton object, and a mocked out setStyleSheet
        with patch('openlp.core.lib.colorbutton.ColorButton.setStyleSheet') as mocked_set_style_sheet:
            widget = ColorButton()

            # WHEN: Changing the color
            widget.change_color('#000000')

            # THEN: The _color attribute should be set to #000000 and setStyleSheet should have been called twice
            self.assertEqual(widget._color, '#000000', '_color should have been set to #000000')
            mocked_set_style_sheet.assert_has_calls(
                [call('background-color: #ffffff'), call('background-color: #000000')])

        self.mocked_change_color = self.change_color_patcher.start()

    def color_test(self):
        """
        Test that the color property method returns the set color
        """

        # GIVEN: An instance of ColorButton, with a set _color attribute
        widget = ColorButton()
        widget._color = '#000000'

        # WHEN: Accesing the color property
        value = widget.color

        # THEN: The value set in _color should be returned
        self.assertEqual(value, '#000000', 'The value returned should be equal to the one we set')

    def color_test(self):
        """
        Test that the color property method returns the set color
        """

        # GIVEN: An instance of ColorButton, with a set _color attribute
        widget = ColorButton()
        widget._color = '#000000'

        # WHEN: Accesing the color property
        value = widget.color

        # THEN: The value set in _color should be returned
        self.assertEqual(value, '#000000', 'The value returned should be equal to the one we set')

    def color_setter_test(self):
        """
        Test that the color property setter method sets the color
        """

        # GIVEN: An instance of ColorButton, with a mocked __init__
        with patch('openlp.core.lib.colorbutton.ColorButton.__init__', **{'return_value': None}):
            widget = ColorButton()

            # WHEN: Setting the color property
            widget.color = '#000000'

            # THEN: Then change_color should have been called with the value we set
            self.mocked_change_color.assert_called_once_with('#000000')

    def on_clicked_invalid_color_test(self):
        """
        Test the on_click method when an invalid color has been supplied
        """

        # GIVEN: An instance of ColorButton, and a set _color attribute
        widget = ColorButton()
        self.mocked_change_color.reset_mock()
        self.mocked_color_changed.reset_mock()
        widget._color = '#000000'

        # WHEN: The on_clicked method is called, and the color is invalid
        self.mocked_qt_gui.QColorDialog.getColor.return_value = MagicMock(**{'isValid.return_value': False})
        widget.on_clicked()

        # THEN: change_color should not have been called and the colorChanged signal should not have been emitted
        self.assertEqual(
            self.mocked_change_color.call_count, 0, 'change_color should not have been called with an invalid color')
        self.assertEqual(
            self.mocked_color_changed.emit.call_count, 0,
            'colorChange signal should not have been emitted with an invalid color')

    def on_clicked_same_color_test(self):
        """
        Test the on_click method when a new color has not been chosen
        """

        # GIVEN: An instance of ColorButton, and a set _color attribute
        widget = ColorButton()
        self.mocked_change_color.reset_mock()
        self.mocked_color_changed.reset_mock()
        widget._color = '#000000'

        # WHEN: The on_clicked method is called, and the color is valid, but the same as the existing color
        self.mocked_qt_gui.QColorDialog.getColor.return_value = MagicMock(
            **{'isValid.return_value': True, 'name.return_value': '#000000'})
        widget.on_clicked()

        # THEN: change_color should not have been called and the colorChanged signal should not have been emitted
        self.assertEqual(
            self.mocked_change_color.call_count, 0,
            'change_color should not have been called when the color has not changed')
        self.assertEqual(
            self.mocked_color_changed.emit.call_count, 0,
            'colorChange signal should not have been emitted when the color has not changed')

    def on_clicked_new_color_test(self):
        """
        Test the on_click method when a new color has been chosen and is valid
        """

        # GIVEN: An instance of ColorButton, and a set _color attribute
        widget = ColorButton()
        self.mocked_change_color.reset_mock()
        self.mocked_color_changed.reset_mock()
        widget._color = '#000000'

        # WHEN: The on_clicked method is called, and the color is valid, and different to the existing color
        self.mocked_qt_gui.QColorDialog.getColor.return_value = MagicMock(
            **{'isValid.return_value': True, 'name.return_value': '#ffffff'})
        widget.on_clicked()

        # THEN: change_color should have been called and the colorChanged signal should have been emitted
        self.mocked_change_color.assert_called_once_with('#ffffff')
        self.mocked_color_changed.emit.assert_called_once_with('#ffffff')
