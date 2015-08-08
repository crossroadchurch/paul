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
The :mod:`ui` module provides standard UI components for OpenLP.
"""
import logging

from PyQt4 import QtCore, QtGui

from openlp.core.common import Registry, UiStrings, translate, is_macosx
from openlp.core.lib import build_icon
from openlp.core.utils.actions import ActionList


log = logging.getLogger(__name__)


def add_welcome_page(parent, image):
    """
    Generate an opening welcome page for a wizard using a provided image.

    :param parent: A ``QWizard`` object to add the welcome page to.
    :param image: A splash image for the wizard.
    """
    parent.welcome_page = QtGui.QWizardPage()
    parent.welcome_page.setPixmap(QtGui.QWizard.WatermarkPixmap, QtGui.QPixmap(image))
    parent.welcome_page.setObjectName('welcome_page')
    parent.welcome_layout = QtGui.QVBoxLayout(parent.welcome_page)
    parent.welcome_layout.setObjectName('WelcomeLayout')
    parent.title_label = QtGui.QLabel(parent.welcome_page)
    parent.title_label.setObjectName('title_label')
    parent.welcome_layout.addWidget(parent.title_label)
    parent.welcome_layout.addSpacing(40)
    parent.information_label = QtGui.QLabel(parent.welcome_page)
    parent.information_label.setWordWrap(True)
    parent.information_label.setObjectName('information_label')
    parent.welcome_layout.addWidget(parent.information_label)
    parent.welcome_layout.addStretch()
    parent.addPage(parent.welcome_page)


def create_button_box(dialog, name, standard_buttons, custom_buttons=None):
    """
    Creates a QDialogButtonBox with the given buttons. The ``accepted()`` and ``rejected()`` signals of the button box
    are connected with the dialogs ``accept()`` and ``reject()`` slots.

    :param dialog: The parent object. This has to be a ``QDialog`` descendant.
    :param name: A string which is set as object name.
    :param standard_buttons: A list of strings for the used buttons. It might contain: ``ok``, ``save``, ``cancel``,
    ``close``, and ``defaults``.
    :param custom_buttons: A list of additional buttons. If an item is an instance of QtGui.QAbstractButton it is added
    with QDialogButtonBox.ActionRole. Otherwise the item has to be a tuple of a Button and a ButtonRole.
    """
    if custom_buttons is None:
        custom_buttons = []
    if standard_buttons is None:
        standard_buttons = []
    buttons = QtGui.QDialogButtonBox.NoButton
    if 'ok' in standard_buttons:
        buttons |= QtGui.QDialogButtonBox.Ok
    if 'save' in standard_buttons:
        buttons |= QtGui.QDialogButtonBox.Save
    if 'cancel' in standard_buttons:
        buttons |= QtGui.QDialogButtonBox.Cancel
    if 'close' in standard_buttons:
        buttons |= QtGui.QDialogButtonBox.Close
    if 'defaults' in standard_buttons:
        buttons |= QtGui.QDialogButtonBox.RestoreDefaults
    button_box = QtGui.QDialogButtonBox(dialog)
    button_box.setObjectName(name)
    button_box.setStandardButtons(buttons)
    for button in custom_buttons:
        if isinstance(button, QtGui.QAbstractButton):
            button_box.addButton(button, QtGui.QDialogButtonBox.ActionRole)
        else:
            button_box.addButton(*button)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    return button_box


def critical_error_message_box(title=None, message=None, parent=None, question=False):
    """
    Provides a standard critical message box for errors that OpenLP displays to users.

    :param title: The title for the message box.
    :param message: The message to display to the user.
    :param parent: The parent UI element to attach the dialog to.
    :param question: Should this message box question the user.
    """
    if question:
        return QtGui.QMessageBox.critical(parent, UiStrings().Error, message,
                                          QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes |
                                                                            QtGui.QMessageBox.No))
    return Registry().get('main_window').error_message(title if title else UiStrings().Error, message)


def create_horizontal_adjusting_combo_box(parent, name):
    """
    Creates a QComboBox with adapting width for media items.

    :param parent: The parent widget.
    :param name: A string set as object name for the combo box.
    """
    combo = QtGui.QComboBox(parent)
    combo.setObjectName(name)
    combo.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
    combo.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
    return combo


def create_button(parent, name, **kwargs):
    """
    Return an button with the object name set and the given parameters.

    :param parent:  A QtCore.QWidget for the buttons parent (required).
    :param name: A string which is set as object name (required).
    :param kwargs:

    ``role``
        A string which can have one value out of ``delete``, ``up``, and ``down``. This decides about default values
        for properties like text, icon, or tooltip.

    ``text``
        A string for the action text.

    ``icon``
        Either a QIcon, a resource string, or a file location string for the action icon.

    ``tooltip``
        A string for the action tool tip.

    ``enabled``
        False in case the button should be disabled.

    """
    if 'role' in kwargs:
        role = kwargs.pop('role')
        if role == 'delete':
            kwargs.setdefault('text', UiStrings().Delete)
            kwargs.setdefault('tooltip', translate('OpenLP.Ui', 'Delete the selected item.'))
        elif role == 'up':
            kwargs.setdefault('icon', ':/services/service_up.png')
            kwargs.setdefault('tooltip', translate('OpenLP.Ui', 'Move selection up one position.'))
        elif role == 'down':
            kwargs.setdefault('icon', ':/services/service_down.png')
            kwargs.setdefault('tooltip', translate('OpenLP.Ui', 'Move selection down one position.'))
        else:
            log.warning('The role "%s" is not defined in create_push_button().', role)
    if kwargs.pop('btn_class', '') == 'toolbutton':
        button = QtGui.QToolButton(parent)
    else:
        button = QtGui.QPushButton(parent)
    button.setObjectName(name)
    if kwargs.get('text'):
        button.setText(kwargs.pop('text'))
    if kwargs.get('icon'):
        button.setIcon(build_icon(kwargs.pop('icon')))
    if kwargs.get('tooltip'):
        button.setToolTip(kwargs.pop('tooltip'))
    if not kwargs.pop('enabled', True):
        button.setEnabled(False)
    if kwargs.get('click'):
        button.clicked.connect(kwargs.pop('click'))
    for key in list(kwargs.keys()):
        if key not in ['text', 'icon', 'tooltip', 'click']:
            log.warning('Parameter %s was not consumed in create_button().', key)
    return button


def create_action(parent, name, **kwargs):
    """
    Return an action with the object name set and the given parameters.

    :param parent:  A QtCore.QObject for the actions parent (required).
    :param name:  A string which is set as object name (required).
    :param kwargs:

    ``text``
        A string for the action text.

    ``icon``
        Either a QIcon, a resource string, or a file location string for the
        action icon.

    ``tooltip``
        A string for the action tool tip.

    ``statustip``
        A string for the action status tip.

    ``checked``
        A bool for the state. If ``None`` the Action is not checkable.

    ``enabled``
        False in case the action should be disabled.

    ``visible``
        False in case the action should be hidden.

    ``separator``
        True in case the action will be considered a separator.

    ``data``
        The action's data.

    ``can_shortcuts``
        Capability stating if this action can have shortcuts. If ``True`` the action is added to shortcut dialog

        otherwise it it not. Define your shortcut in the :class:`~openlp.core.lib.Settings` class. *Note*: When *not*
        ``True`` you *must not* set a shortcuts at all.

    ``context``
        A context for the shortcut execution.

    ``category``
        A category the action should be listed in the shortcut dialog.

    ``triggers``
        A slot which is connected to the actions ``triggered()`` slot.
    """
    action = QtGui.QAction(parent)
    action.setObjectName(name)
    if is_macosx():
        action.setIconVisibleInMenu(False)
    if kwargs.get('text'):
        action.setText(kwargs.pop('text'))
    if kwargs.get('icon'):
        action.setIcon(build_icon(kwargs.pop('icon')))
    if kwargs.get('tooltip'):
        action.setToolTip(kwargs.pop('tooltip'))
    if kwargs.get('statustip'):
        action.setStatusTip(kwargs.pop('statustip'))
    if kwargs.get('checked') is not None:
        action.setCheckable(True)
        action.setChecked(kwargs.pop('checked'))
    if not kwargs.pop('enabled', True):
        action.setEnabled(False)
    if not kwargs.pop('visible', True):
        action.setVisible(False)
    if kwargs.pop('separator', False):
        action.setSeparator(True)
    if 'data' in kwargs:
        action.setData(kwargs.pop('data'))
    if kwargs.pop('can_shortcuts', False):
        action_list = ActionList.get_instance()
        action_list.add_action(action, kwargs.pop('category', None))
    if 'context' in kwargs:
        action.setShortcutContext(kwargs.pop('context'))
    if kwargs.get('triggers'):
        action.triggered.connect(kwargs.pop('triggers'))
    for key in list(kwargs.keys()):
        if key not in ['text', 'icon', 'tooltip', 'statustip', 'checked', 'can_shortcuts', 'category', 'triggers']:
            log.warning('Parameter %s was not consumed in create_action().' % key)
    return action


def create_widget_action(parent, name='', **kwargs):
    """
    Return a new QAction by calling ``create_action(parent, name, **kwargs)``. The shortcut context defaults to
    ``QtCore.Qt.WidgetShortcut`` and the action is added to the parents action list.
    """
    kwargs.setdefault('context', QtCore.Qt.WidgetShortcut)
    action = create_action(parent, name, **kwargs)
    parent.addAction(action)
    return action


def set_case_insensitive_completer(cache, widget):
    """
    Sets a case insensitive text completer for a widget.

    :param cache: The list of items to use as suggestions.
    :param widget: A widget to set the completer (QComboBox or QLineEdit instance)
    """
    completer = QtGui.QCompleter(cache)
    completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
    widget.setCompleter(completer)


def create_valign_selection_widgets(parent):
    """
    Creates a standard label and combo box for asking users to select a vertical alignment.

    :param parent: The parent object. This should be a ``QWidget`` descendant.
    """
    label = QtGui.QLabel(parent)
    label.setText(translate('OpenLP.Ui', '&Vertical Align:'))
    combo_box = QtGui.QComboBox(parent)
    combo_box.addItems([UiStrings().Top, UiStrings().Middle, UiStrings().Bottom])
    label.setBuddy(combo_box)
    return label, combo_box


def find_and_set_in_combo_box(combo_box, value_to_find, set_missing=True):
    """
    Find a string in a combo box and set it as the selected item if present

    :param combo_box: The combo box to check for selected items
    :param value_to_find: The value to find
    :param set_missing: if not found leave value as current
    """
    index = combo_box.findText(value_to_find, QtCore.Qt.MatchExactly)
    if index == -1:
        # Not Found.
        index = 0 if set_missing else combo_box.currentIndex()
    combo_box.setCurrentIndex(index)
