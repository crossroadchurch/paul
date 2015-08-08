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
The :mod:`~openlp.core.ui.shortcutlistform` module contains the form class"""
import logging
import re

from PyQt4 import QtCore, QtGui

from openlp.core.common import RegistryProperties, Settings, translate
from openlp.core.utils.actions import ActionList
from .shortcutlistdialog import Ui_ShortcutListDialog

REMOVE_AMPERSAND = re.compile(r'&{1}')

log = logging.getLogger(__name__)


class ShortcutListForm(QtGui.QDialog, Ui_ShortcutListDialog, RegistryProperties):
    """
    The shortcut list dialog
    """

    def __init__(self, parent=None):
        """
        Constructor
        """
        super(ShortcutListForm, self).__init__(parent)
        self.setupUi(self)
        self.changed_actions = {}
        self.action_list = ActionList.get_instance()
        self.dialog_was_shown = False
        self.primary_push_button.toggled.connect(self.on_primary_push_button_clicked)
        self.alternate_push_button.toggled.connect(self.on_alternate_push_button_clicked)
        self.tree_widget.currentItemChanged.connect(self.on_current_item_changed)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.clear_primary_button.clicked.connect(self.on_clear_primary_button_clicked)
        self.clear_alternate_button.clicked.connect(self.on_clear_alternate_button_clicked)
        self.button_box.clicked.connect(self.on_restore_defaults_clicked)
        self.default_radio_button.clicked.connect(self.on_default_radio_button_clicked)
        self.custom_radio_button.clicked.connect(self.on_custom_radio_button_clicked)

    def keyPressEvent(self, event):
        """
        Respond to certain key presses
        """
        if event.key() == QtCore.Qt.Key_Space:
            self.keyReleaseEvent(event)
        elif self.primary_push_button.isChecked() or self.alternate_push_button.isChecked():
            self.keyReleaseEvent(event)
        elif event.key() == QtCore.Qt.Key_Escape:
            event.accept()
            self.close()

    def keyReleaseEvent(self, event):
        """
        Respond to certain key presses
        """
        if not self.primary_push_button.isChecked() and not self.alternate_push_button.isChecked():
            return
        # Do not continue, as the event is for the dialog (close it).
        if self.dialog_was_shown and event.key() in (QtCore.Qt.Key_Escape, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            self.dialog_was_shown = False
            return
        key = event.key()
        if key in (QtCore.Qt.Key_Shift, QtCore.Qt.Key_Control, QtCore.Qt.Key_Meta, QtCore.Qt.Key_Alt):
            return
        key_string = QtGui.QKeySequence(key).toString()
        if event.modifiers() & QtCore.Qt.ControlModifier == QtCore.Qt.ControlModifier:
            key_string = 'Ctrl+' + key_string
        if event.modifiers() & QtCore.Qt.AltModifier == QtCore.Qt.AltModifier:
            key_string = 'Alt+' + key_string
        if event.modifiers() & QtCore.Qt.ShiftModifier == QtCore.Qt.ShiftModifier:
            key_string = 'Shift+' + key_string
        if event.modifiers() & QtCore.Qt.MetaModifier == QtCore.Qt.MetaModifier:
            key_string = 'Meta+' + key_string
        key_sequence = QtGui.QKeySequence(key_string)
        if self._validiate_shortcut(self._current_item_action(), key_sequence):
            if self.primary_push_button.isChecked():
                self._adjust_button(self.primary_push_button, False, text=key_sequence.toString())
            elif self.alternate_push_button.isChecked():
                self._adjust_button(self.alternate_push_button, False, text=key_sequence.toString())

    def exec_(self):
        """
        Execute the dialog
        """
        self.changed_actions = {}
        self.reload_shortcut_list()
        self._adjust_button(self.primary_push_button, False, False, '')
        self._adjust_button(self.alternate_push_button, False, False, '')
        return QtGui.QDialog.exec_(self)

    def reload_shortcut_list(self):
        """
        Reload the ``tree_widget`` list to add new and remove old actions.
        """
        self.tree_widget.clear()
        for category in self.action_list.categories:
            # Check if the category is for internal use only.
            if category.name is None:
                continue
            item = QtGui.QTreeWidgetItem([category.name])
            for action in category.actions:
                action_text = REMOVE_AMPERSAND.sub('', action.text())
                action_item = QtGui.QTreeWidgetItem([action_text])
                action_item.setIcon(0, action.icon())
                action_item.setData(0, QtCore.Qt.UserRole, action)
                tool_tip_text = action.toolTip()
                # Only display tool tips if they are helpful.
                if tool_tip_text != action_text:
                    # Display the tool tip in all three colums.
                    action_item.setToolTip(0, tool_tip_text)
                    action_item.setToolTip(1, tool_tip_text)
                    action_item.setToolTip(2, tool_tip_text)
                item.addChild(action_item)
            self.tree_widget.addTopLevelItem(item)
            item.setExpanded(True)
        self.refresh_shortcut_list()

    def refresh_shortcut_list(self):
        """
        This refreshes the item's shortcuts shown in the list. Note, this neither adds new actions nor removes old
        actions.
        """
        iterator = QtGui.QTreeWidgetItemIterator(self.tree_widget)
        while iterator.value():
            item = iterator.value()
            iterator += 1
            action = self._current_item_action(item)
            if action is None:
                continue
            shortcuts = self._action_shortcuts(action)
            if not shortcuts:
                item.setText(1, '')
                item.setText(2, '')
            elif len(shortcuts) == 1:
                item.setText(1, shortcuts[0].toString())
                item.setText(2, '')
            else:
                item.setText(1, shortcuts[0].toString())
                item.setText(2, shortcuts[1].toString())
        self.on_current_item_changed()

    def on_primary_push_button_clicked(self, toggled):
        """
        Save the new primary shortcut.
        """
        self.custom_radio_button.setChecked(True)
        if toggled:
            self.alternate_push_button.setChecked(False)
            self.primary_push_button.setText('')
            return
        action = self._current_item_action()
        if action is None:
            return
        shortcuts = self._action_shortcuts(action)
        new_shortcuts = [QtGui.QKeySequence(self.primary_push_button.text())]
        if len(shortcuts) == 2:
            new_shortcuts.append(shortcuts[1])
        self.changed_actions[action] = new_shortcuts
        self.refresh_shortcut_list()

    def on_alternate_push_button_clicked(self, toggled):
        """
        Save the new alternate shortcut.
        """
        self.custom_radio_button.setChecked(True)
        if toggled:
            self.primary_push_button.setChecked(False)
            self.alternate_push_button.setText('')
            return
        action = self._current_item_action()
        if action is None:
            return
        shortcuts = self._action_shortcuts(action)
        new_shortcuts = []
        if shortcuts:
            new_shortcuts.append(shortcuts[0])
        new_shortcuts.append(QtGui.QKeySequence(self.alternate_push_button.text()))
        self.changed_actions[action] = new_shortcuts
        if not self.primary_push_button.text():
            # When we do not have a primary shortcut, the just entered alternate shortcut will automatically become the
            # primary shortcut. That is why we have to adjust the primary button's text.
            self.primary_push_button.setText(self.alternate_push_button.text())
            self.alternate_push_button.setText('')
        self.refresh_shortcut_list()

    def on_item_double_clicked(self, item, column):
        """
        A item has been double clicked. The ``primaryPushButton`` will be checked and the item's shortcut will be
        displayed.
        """
        action = self._current_item_action(item)
        if action is None:
            return
        self.primary_push_button.setChecked(column in [0, 1])
        self.alternate_push_button.setChecked(column not in [0, 1])
        if column in [0, 1]:
            self.primary_push_button.setText('')
            self.primary_push_button.setFocus()
        else:
            self.alternate_push_button.setText('')
            self.alternate_push_button.setFocus()

    def on_current_item_changed(self, item=None, previousItem=None):
        """
        A item has been pressed. We adjust the button's text to the action's shortcut which is encapsulate in the item.
        """
        action = self._current_item_action(item)
        self.primary_push_button.setEnabled(action is not None)
        self.alternate_push_button.setEnabled(action is not None)
        primary_text = ''
        alternate_text = ''
        primary_label_text = ''
        alternate_label_text = ''
        if action is None:
            self.primary_push_button.setChecked(False)
            self.alternate_push_button.setChecked(False)
        else:
            if action.default_shortcuts:
                primary_label_text = action.default_shortcuts[0].toString()
                if len(action.default_shortcuts) == 2:
                    alternate_label_text = action.default_shortcuts[1].toString()
            shortcuts = self._action_shortcuts(action)
            # We do not want to loose pending changes, that is why we have to keep the text when, this function has not
            # been triggered by a signal.
            if item is None:
                primary_text = self.primary_push_button.text()
                alternate_text = self.alternate_push_button.text()
            elif len(shortcuts) == 1:
                primary_text = shortcuts[0].toString()
            elif len(shortcuts) == 2:
                primary_text = shortcuts[0].toString()
                alternate_text = shortcuts[1].toString()
        # When we are capturing a new shortcut, we do not want, the buttons to display the current shortcut.
        if self.primary_push_button.isChecked():
            primary_text = ''
        if self.alternate_push_button.isChecked():
            alternate_text = ''
        self.primary_push_button.setText(primary_text)
        self.alternate_push_button.setText(alternate_text)
        self.primary_label.setText(primary_label_text)
        self.alternate_label.setText(alternate_label_text)
        # We do not want to toggle and radio button, as the function has not been triggered by a signal.
        if item is None:
            return
        if primary_label_text == primary_text and alternate_label_text == alternate_text:
            self.default_radio_button.toggle()
        else:
            self.custom_radio_button.toggle()

    def on_restore_defaults_clicked(self, button):
        """
        Restores all default shortcuts.
        """
        if self.button_box.buttonRole(button) != QtGui.QDialogButtonBox.ResetRole:
            return
        if QtGui.QMessageBox.question(self, translate('OpenLP.ShortcutListDialog', 'Restore Default Shortcuts'),
                                      translate('OpenLP.ShortcutListDialog', 'Do you want to restore all '
                                                'shortcuts to their defaults?'),
                                      QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes |
                                                                        QtGui.QMessageBox.No)) == QtGui.QMessageBox.No:
            return
        self._adjust_button(self.primary_push_button, False, text='')
        self._adjust_button(self.alternate_push_button, False, text='')
        for category in self.action_list.categories:
            for action in category.actions:
                self.changed_actions[action] = action.default_shortcuts
        self.refresh_shortcut_list()

    def on_default_radio_button_clicked(self, toggled):
        """
        The default radio button has been clicked, which means we have to make sure, that we use the default shortcuts
        for the action.
        """
        if not toggled:
            return
        action = self._current_item_action()
        if action is None:
            return
        temp_shortcuts = self._action_shortcuts(action)
        self.changed_actions[action] = action.default_shortcuts
        self.refresh_shortcut_list()
        primary_button_text = ''
        alternate_button_text = ''
        if temp_shortcuts:
            primary_button_text = temp_shortcuts[0].toString()
        if len(temp_shortcuts) == 2:
            alternate_button_text = temp_shortcuts[1].toString()
        self.primary_push_button.setText(primary_button_text)
        self.alternate_push_button.setText(alternate_button_text)

    def on_custom_radio_button_clicked(self, toggled):
        """
        The custom shortcut radio button was clicked, thus we have to restore the custom shortcuts by calling those
        functions triggered by button clicks.
        """
        if not toggled:
            return
        self.on_primary_push_button_clicked(False)
        self.on_alternate_push_button_clicked(False)
        self.refresh_shortcut_list()

    def save(self):
        """
        Save the shortcuts. **Note**, that we do not have to load the shortcuts, as they are loaded in
        :class:`~openlp.core.utils.ActionList`.
        """
        settings = Settings()
        settings.beginGroup('shortcuts')
        for category in self.action_list.categories:
            # Check if the category is for internal use only.
            if category.name is None:
                continue
            for action in category.actions:
                if action in self.changed_actions:
                    old_shortcuts = list(map(QtGui.QKeySequence.toString, action.shortcuts()))
                    action.setShortcuts(self.changed_actions[action])
                    self.action_list.update_shortcut_map(action, old_shortcuts)
                settings.setValue(action.objectName(), action.shortcuts())
        settings.endGroup()

    def on_clear_primary_button_clicked(self, toggled):
        """
        Restore the defaults of this action.
        """
        self.primary_push_button.setChecked(False)
        action = self._current_item_action()
        if action is None:
            return
        shortcuts = self._action_shortcuts(action)
        new_shortcuts = []
        if action.default_shortcuts:
            new_shortcuts.append(action.default_shortcuts[0])
            # We have to check if the primary default shortcut is available. But  we only have to check, if the action
            # has a default primary shortcut (an "empty" shortcut is always valid and if the action does not have a
            # default primary shortcut, then the alternative shortcut (not the default one) will become primary
            # shortcut, thus the check will assume that an action were going to have the same shortcut twice.
            if not self._validiate_shortcut(action, new_shortcuts[0]) and new_shortcuts[0] != shortcuts[0]:
                return
        if len(shortcuts) == 2:
            new_shortcuts.append(shortcuts[1])
        self.changed_actions[action] = new_shortcuts
        self.refresh_shortcut_list()
        self.on_current_item_changed(self.tree_widget.currentItem())

    def on_clear_alternate_button_clicked(self, toggled):
        """
        Restore the defaults of this action.
        """
        self.alternate_push_button.setChecked(False)
        action = self._current_item_action()
        if action is None:
            return
        shortcuts = self._action_shortcuts(action)
        new_shortcuts = []
        if shortcuts:
            new_shortcuts.append(shortcuts[0])
        if len(action.default_shortcuts) == 2:
            new_shortcuts.append(action.default_shortcuts[1])
        if len(new_shortcuts) == 2:
            if not self._validiate_shortcut(action, new_shortcuts[1]):
                return
        self.changed_actions[action] = new_shortcuts
        self.refresh_shortcut_list()
        self.on_current_item_changed(self.tree_widget.currentItem())

    def _validiate_shortcut(self, changing_action, key_sequence):
        """
        Checks if the given ``changing_action `` can use the given ``key_sequence``. Returns ``True`` if the
        ``key_sequence`` can be used by the action, otherwise displays a dialog and returns ``False``.

        :param changing_action: The action which wants to use the ``key_sequence``.
        :param key_sequence: The key sequence which the action want so use.
        """
        is_valid = True
        for category in self.action_list.categories:
            for action in category.actions:
                shortcuts = self._action_shortcuts(action)
                if key_sequence not in shortcuts:
                    continue
                if action is changing_action:
                    if self.primary_push_button.isChecked() and shortcuts.index(key_sequence) == 0:
                        continue
                    if self.alternate_push_button.isChecked() and shortcuts.index(key_sequence) == 1:
                        continue
                # Have the same parent, thus they cannot have the same shortcut.
                if action.parent() is changing_action.parent():
                    is_valid = False
                # The new shortcut is already assigned, but if both shortcuts are only valid in a different widget the
                # new shortcut is valid, because they will not interfere.
                if action.shortcutContext() in [QtCore.Qt.WindowShortcut, QtCore.Qt.ApplicationShortcut]:
                    is_valid = False
                if changing_action.shortcutContext() in [QtCore.Qt.WindowShortcut, QtCore.Qt.ApplicationShortcut]:
                    is_valid = False
        if not is_valid:
            self.main_window.warning_message(translate('OpenLP.ShortcutListDialog', 'Duplicate Shortcut'),
                                             translate('OpenLP.ShortcutListDialog',
                                                       'The shortcut "%s" is already assigned to another action, please'
                                                       ' use a different shortcut.') % key_sequence.toString())
            self.dialog_was_shown = True
        return is_valid

    def _action_shortcuts(self, action):
        """
        This returns the shortcuts for the given ``action``, which also includes those shortcuts which are not saved
        yet but already assigned (as changes yre applied when closing the dialog).
        """
        if action in self.changed_actions:
            return self.changed_actions[action]
        return action.shortcuts()

    def _current_item_action(self, item=None):
        """
        Returns the action of the given ``item``. If no item is given, we return the action of the current item of
        the ``tree_widget``.
        """
        if item is None:
            item = self.tree_widget.currentItem()
            if item is None:
                return
        return item.data(0, QtCore.Qt.UserRole)

    def _adjust_button(self, button, checked=None, enabled=None, text=None):
        """
        Can be called to adjust more properties of the given ``button`` at once.
        """
        # Set the text before checking the button, because this emits a signal.
        if text is not None:
            button.setText(text)
        if checked is not None:
            button.setChecked(checked)
        if enabled is not None:
            button.setEnabled(enabled)
