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
    :mod: `openlp.core.ui.projector.sourceselectform` module

    Provides the dialog window for selecting video source for projector.
"""
import logging
log = logging.getLogger(__name__)
log.debug('editform loaded')

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot, QSize
from PyQt4.QtGui import QDialog, QButtonGroup, QDialogButtonBox, QFormLayout, QLineEdit, QRadioButton, \
    QStyle, QStylePainter, QStyleOptionTab, QTabBar, QTabWidget, QVBoxLayout, QWidget

from openlp.core.common import translate, is_macosx
from openlp.core.lib import build_icon
from openlp.core.lib.projector.db import ProjectorSource
from openlp.core.lib.projector.constants import PJLINK_DEFAULT_SOURCES, PJLINK_DEFAULT_CODES


def source_group(inputs, source_text):
    """
    Return a dictionary where key is source[0] and values are inputs
    grouped by source[0].

    source_text = dict{"key1": "key1-text",
                       "key2": "key2-text",
                       ...}
    return:
        dict{ key1[0]: { "key11": "key11-text",
                         "key12": "key12-text",
                         "key13": "key13-text",
                         ... }
              key2[0]: {"key21": "key21-text",
                        "key22": "key22-text",
                        ... }

    :param inputs: List of inputs
    :param source_text: Dictionary of {code: text} values to display
    :returns: dict
    """
    groupdict = {}
    keydict = {}
    checklist = inputs
    key = checklist[0][0]
    for item in checklist:
        if item[0] == key:
            groupdict[item] = source_text[item]
            continue
        else:
            keydict[key] = groupdict
            key = item[0]
            groupdict = {item: source_text[item]}
    keydict[key] = groupdict
    return keydict


def Build_Tab(group, source_key, default, projector, projectordb, edit=False):
    """
    Create the radio button page for a tab.
    Dictionary will be a 1-key entry where key=tab to setup, val=list of inputs.

    source_key: {"groupkey1": {"key11": "key11-text",
                               "key12": "key12-text",
                               ...
                              },
                 "groupkey2": {"key21": "key21-text",
                               "key22": "key22-text",
                               ....
                              },
                 ...
                }

    :param group: Button group widget to add buttons to
    :param source_key: Dictionary of sources for radio buttons
    :param default: Default radio button to check
    :param projector: Projector instance
    :param projectordb: ProjectorDB instance for session
    :param edit: If we're editing the source text
    """
    buttonchecked = False
    widget = QWidget()
    layout = QFormLayout() if edit else QVBoxLayout()
    layout.setSpacing(10)
    widget.setLayout(layout)
    tempkey = list(source_key.keys())[0]  # Should only be 1 key
    sourcelist = list(source_key[tempkey])
    sourcelist.sort()
    button_count = len(sourcelist)
    if edit:
        for key in sourcelist:
            item = QLineEdit()
            item.setObjectName('source_key_%s' % key)
            source_item = projectordb.get_source_by_code(code=key, projector_id=projector.db_item.id)
            if source_item is None:
                item.setText(PJLINK_DEFAULT_CODES[key])
            else:
                item.setText(source_item.text)
            layout.addRow(PJLINK_DEFAULT_CODES[key], item)
            group.append(item)
    else:
        for key in sourcelist:
            source_item = projectordb.get_source_by_code(code=key, projector_id=projector.db_item.id)
            if source_item is None:
                text = source_key[tempkey][key]
            else:
                text = source_item.text
            itemwidget = QRadioButton(text)
            itemwidget.setAutoExclusive(True)
            if default == key:
                itemwidget.setChecked(True)
                buttonchecked = itemwidget.isChecked() or buttonchecked
            group.addButton(itemwidget, int(key))
            layout.addWidget(itemwidget)
        layout.addStretch()
    return widget, button_count, buttonchecked


def set_button_tooltip(bar):
    """
    Set the toolip for the standard buttons used

    :param bar: QDialogButtonBar instance to update
    """
    for button in bar.buttons():
        if bar.standardButton(button) == QDialogButtonBox.Cancel:
            button.setToolTip(translate('OpenLP.SourceSelectForm',
                                        'Ignoring current changes and return to OpenLP'))
        elif bar.standardButton(button) == QDialogButtonBox.Reset:
            button.setToolTip(translate('OpenLP.SourceSelectForm',
                                        'Delete all user-defined text and revert to PJLink default text'))
        elif bar.standardButton(button) == QDialogButtonBox.Discard:
            button.setToolTip(translate('OpenLP.SourceSelectForm',
                                        'Discard changes and reset to previous user-defined text'))
        elif bar.standardButton(button) == QDialogButtonBox.Ok:
            button.setToolTip(translate('OpenLP.SourceSelectForm',
                                        'Save changes and return to OpenLP'))
        else:
            log.debug('No tooltip for button {}'.format(button.text()))


class FingerTabBarWidget(QTabBar):
    """
    Realign west -orientation tabs to left-right text rather than south-north text
    Borrowed from
    http://www.kidstrythisathome.com/2013/03/fingertabs-horizontal-tabs-with-horizontal-text-in-pyqt/
    """
    def __init__(self, parent=None, *args, **kwargs):
        """
        Reset tab text orientation on initialization

        :param width: Remove default width parameter in kwargs
        :param height: Remove default height parameter in kwargs
        """
        self.tabSize = QSize(kwargs.pop('width', 100), kwargs.pop('height', 25))
        QTabBar.__init__(self, parent, *args, **kwargs)

    def paintEvent(self, event):
        """
        Repaint tab in left-right text orientation.

        :param event: Repaint event signal
        """
        painter = QStylePainter(self)
        option = QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(option, index)
            tabRect = self.tabRect(index)
            tabRect.moveLeft(10)
            painter.drawControl(QStyle.CE_TabBarTabShape, option)
            painter.drawText(tabRect, QtCore.Qt.AlignVCenter |
                             QtCore.Qt.TextDontClip,
                             self.tabText(index))
        painter.end()

    def tabSizeHint(self, index):
        """
        Return tabsize

        :param index: Tab index to fetch tabsize from
        :returns: instance tabSize
        """
        return self.tabSize


class FingerTabWidget(QTabWidget):
    """
    A QTabWidget equivalent which uses our FingerTabBarWidget

    Based on thread discussion
    http://www.riverbankcomputing.com/pipermail/pyqt/2005-December/011724.html
    """
    def __init__(self, parent, *args):
        """
        Initialize FingerTabWidget instance
        """
        QTabWidget.__init__(self, parent, *args)
        self.setTabBar(FingerTabBarWidget(self))


class SourceSelectTabs(QDialog):
    """
    Class for handling selecting the source for the projector to use.
    Uses tabbed interface.
    """
    def __init__(self, parent, projectordb, edit=False):
        """
        Build the source select dialog using tabbed interface.

        :param projectordb: ProjectorDB session to use
        """
        log.debug('Initializing SourceSelectTabs()')
        super(SourceSelectTabs, self).__init__(parent)
        self.setMinimumWidth(350)
        self.projectordb = projectordb
        self.edit = edit
        if self.edit:
            title = translate('OpenLP.SourceSelectForm', 'Edit Projector Source Text')
        else:
            title = translate('OpenLP.SourceSelectForm', 'Select Projector Source')
        self.setWindowTitle(title)
        self.setObjectName('source_select_tabs')
        self.setWindowIcon(build_icon(':/icon/openlp-log-32x32.png'))
        self.setModal(True)
        self.layout = QVBoxLayout()
        self.layout.setObjectName('source_select_tabs_layout')
        if is_macosx():
            self.tabwidget = QTabWidget(self)
        else:
            self.tabwidget = FingerTabWidget(self)
        self.tabwidget.setObjectName('source_select_tabs_tabwidget')
        self.tabwidget.setUsesScrollButtons(False)
        if is_macosx():
            self.tabwidget.setTabPosition(QTabWidget.North)
        else:
            self.tabwidget.setTabPosition(QTabWidget.West)
        self.layout.addWidget(self.tabwidget)
        self.setLayout(self.layout)

    def exec_(self, projector):
        """
        Override initial method so we can build the tabs.

        :param projector: Projector instance to build source list from
        """
        self.projector = projector
        self.source_text = self.projectordb.get_source_list(projector=projector)
        self.source_group = source_group(projector.source_available, self.source_text)
        # self.source_group = {'4': {'41': 'Storage 1'}, '5': {"51": 'Network 1'}}
        self.button_group = [] if self.edit else QButtonGroup()
        keys = list(self.source_group.keys())
        keys.sort()
        if self.edit:
            for key in keys:
                (tab, button_count, buttonchecked) = Build_Tab(group=self.button_group,
                                                               source_key={key: self.source_group[key]},
                                                               default=self.projector.source,
                                                               projector=self.projector,
                                                               projectordb=self.projectordb,
                                                               edit=self.edit)
                thistab = self.tabwidget.addTab(tab, PJLINK_DEFAULT_SOURCES[key])
                if buttonchecked:
                    self.tabwidget.setCurrentIndex(thistab)
            self.button_box = QDialogButtonBox(QtGui.QDialogButtonBox.Reset |
                                               QtGui.QDialogButtonBox.Discard |
                                               QtGui.QDialogButtonBox.Ok |
                                               QtGui.QDialogButtonBox.Cancel)
        else:
            for key in keys:
                (tab, button_count, buttonchecked) = Build_Tab(group=self.button_group,
                                                               source_key={key: self.source_group[key]},
                                                               default=self.projector.source,
                                                               projector=self.projector,
                                                               projectordb=self.projectordb,
                                                               edit=self.edit)
                thistab = self.tabwidget.addTab(tab, PJLINK_DEFAULT_SOURCES[key])
                if buttonchecked:
                    self.tabwidget.setCurrentIndex(thistab)
            self.button_box = QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                               QtGui.QDialogButtonBox.Cancel)
        self.button_box.clicked.connect(self.button_clicked)
        self.layout.addWidget(self.button_box)
        set_button_tooltip(self.button_box)
        selected = super(SourceSelectTabs, self).exec_()
        return selected

    @pyqtSlot(object)
    def button_clicked(self, button):
        """
        Checks which button was clicked

        :param button: Button that was clicked
        :returns: Ok:      Saves current edits
                  Delete:  Resets text to last-saved text
                  Reset:   Reset all text to PJLink default text
                  Cancel:  Cancel text edit
        """
        if self.button_box.standardButton(button) == self.button_box.Cancel:
            self.done(0)
        elif self.button_box.standardButton(button) == self.button_box.Reset:
            self.done(100)
        elif self.button_box.standardButton(button) == self.button_box.Discard:
            self.delete_sources()
        elif self.button_box.standardButton(button) == self.button_box.Ok:
            return self.accept_me()
        else:
            return 100

    def delete_sources(self):
        msg = QtGui.QMessageBox()
        msg.setText(translate('OpenLP.SourceSelectForm', 'Delete entries for this projector'))
        msg.setInformativeText(translate('OpenLP.SourceSelectForm',
                                         'Are you sure you want to delete ALL user-defined '
                                         'source input text for this projector?'))
        msg.setStandardButtons(msg.Cancel | msg.Ok)
        msg.setDefaultButton(msg.Cancel)
        ans = msg.exec_()
        if ans == msg.Cancel:
            return
        self.projectordb.delete_all_objects(ProjectorSource, ProjectorSource.projector_id == self.projector.db_item.id)
        self.done(100)

    def accept_me(self):
        """
        Slot to accept 'OK' button
        """
        projector = self.projector.db_item
        if self.edit:
            for key in self.button_group:
                code = key.objectName().split("_")[-1]
                text = key.text().strip()
                if key.text().strip().lower() == PJLINK_DEFAULT_CODES[code].strip().lower():
                    continue
                item = self.projectordb.get_source_by_code(code=code, projector_id=projector.id)
                if item is None:
                    log.debug("(%s) Adding new source text %s: %s" % (projector.ip, code, text))
                    item = ProjectorSource(projector_id=projector.id, code=code, text=text)
                else:
                    item.text = text
                    log.debug('(%s) Updating source code %s with text="%s"' % (projector.ip, item.code, item.text))
                self.projectordb.add_source(item)
            selected = 0
        else:
            selected = self.button_group.checkedId()
            log.debug('SourceSelectTabs().accepted() Setting source to %s' % selected)
        self.done(selected)


class SourceSelectSingle(QDialog):
    """
    Class for handling selecting the source for the projector to use.
    Uses single dialog interface.
    """
    def __init__(self, parent, projectordb, edit=False):
        """
        Build the source select dialog.

        :param projectordb: ProjectorDB session to use
        """
        log.debug('Initializing SourceSelectSingle()')
        self.projectordb = projectordb
        super(SourceSelectSingle, self).__init__(parent)
        self.edit = edit
        if self.edit:
            title = translate('OpenLP.SourceSelectForm', 'Edit Projector Source Text')
        else:
            title = translate('OpenLP.SourceSelectForm', 'Select Projector Source')
        self.setObjectName('source_select_single')
        self.setWindowIcon(build_icon(':/icon/openlp-log-32x32.png'))
        self.setModal(True)
        self.edit = edit

    def exec_(self, projector, edit=False):
        """
        Override initial method so we can build the tabs.

        :param projector: Projector instance to build source list from
        """
        self.projector = projector
        self.layout = QFormLayout() if self.edit else QVBoxLayout()
        self.layout.setObjectName('source_select_tabs_layout')
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
        self.setMinimumWidth(350)
        self.button_group = [] if self.edit else QButtonGroup()
        self.source_text = self.projectordb.get_source_list(projector=projector)
        keys = list(self.source_text.keys())
        keys.sort()
        key_count = len(keys)
        button_list = []
        if self.edit:
            for key in keys:
                item = QLineEdit()
                item.setObjectName('source_key_%s' % key)
                source_item = self.projectordb.get_source_by_code(code=key, projector_id=self.projector.db_item.id)
                if source_item is None:
                    item.setText(PJLINK_DEFAULT_CODES[key])
                else:
                    item.old_text = item.text()
                    item.setText(source_item.text)
                self.layout.addRow(PJLINK_DEFAULT_CODES[key], item)
                self.button_group.append(item)
            self.button_box = QDialogButtonBox(QtGui.QDialogButtonBox.Reset |
                                               QtGui.QDialogButtonBox.Discard |
                                               QtGui.QDialogButtonBox.Ok |
                                               QtGui.QDialogButtonBox.Cancel)
        else:
            for key in keys:
                source_text = self.projectordb.get_source_by_code(code=key, projector_id=self.projector.db_item.id)
                text = self.source_text[key] if source_text is None else source_text.text
                button = QtGui.QRadioButton(text)
                button.setChecked(True if key == projector.source else False)
                self.layout.addWidget(button)
                self.button_group.addButton(button, int(key))
                button_list.append(key)
            self.button_box = QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                               QtGui.QDialogButtonBox.Cancel)
        self.button_box.clicked.connect(self.button_clicked)
        self.layout.addWidget(self.button_box)
        self.setMinimumHeight(key_count*25)
        set_button_tooltip(self.button_box)
        selected = super(SourceSelectSingle, self).exec_()
        return selected

    @pyqtSlot(object)
    def button_clicked(self, button):
        """
        Checks which button was clicked

        :param button: Button that was clicked
        :returns: Ok:      Saves current edits
                  Delete:  Resets text to last-saved text
                  Reset:   Reset all text to PJLink default text
                  Cancel:  Cancel text edit
        """
        if self.button_box.standardButton(button) == self.button_box.Cancel:
            self.done(0)
        elif self.button_box.standardButton(button) == self.button_box.Reset:
            self.done(100)
        elif self.button_box.standardButton(button) == self.button_box.Discard:
            self.delete_sources()
        elif self.button_box.standardButton(button) == self.button_box.Ok:
            return self.accept_me()
        else:
            return 100

    def delete_sources(self):
        msg = QtGui.QMessageBox()
        msg.setText(translate('OpenLP.SourceSelectForm', 'Delete entries for this projector'))
        msg.setInformativeText(translate('OpenLP.SourceSelectForm',
                                         'Are you sure you want to delete ALL user-defined '
                                         'source input text for this projector?'))
        msg.setStandardButtons(msg.Cancel | msg.Ok)
        msg.setDefaultButton(msg.Cancel)
        ans = msg.exec_()
        if ans == msg.Cancel:
            return
        self.projectordb.delete_all_objects(ProjectorSource, ProjectorSource.projector_id == self.projector.db_item.id)
        self.done(100)

    @pyqtSlot()
    def accept_me(self):
        """
        Slot to accept 'OK' button
        """
        projector = self.projector.db_item
        if self.edit:
            for key in self.button_group:
                code = key.objectName().split("_")[-1]
                text = key.text().strip()
                if key.text().strip().lower() == PJLINK_DEFAULT_CODES[code].strip().lower():
                    continue
                item = self.projectordb.get_source_by_code(code=code, projector_id=projector.id)
                if item is None:
                    log.debug("(%s) Adding new source text %s: %s" % (projector.ip, code, text))
                    item = ProjectorSource(projector_id=projector.id, code=code, text=text)
                else:
                    item.text = text
                    log.debug('(%s) Updating source code %s with text="%s"' % (projector.ip, item.code, item.text))
                self.projectordb.add_source(item)
            selected = 0
        else:
            selected = self.button_group.checkedId()
            log.debug('SourceSelectDialog().accepted() Setting source to %s' % selected)
        self.done(selected)
