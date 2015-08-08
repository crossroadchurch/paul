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
    :mod: `openlp.core.ui.projector.editform` module

    Provides the functions for adding/editing entries in the projector database.
"""

import logging
log = logging.getLogger(__name__)
log.debug('editform loaded')

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot, pyqtSignal
from PyQt4.QtGui import QDialog, QPlainTextEdit, QLineEdit, QDialogButtonBox, QLabel, QGridLayout

from openlp.core.common import translate, verify_ip_address
from openlp.core.lib import build_icon
from openlp.core.lib.projector.db import Projector
from openlp.core.lib.projector.constants import PJLINK_PORT


class Ui_ProjectorEditForm(object):
    """
    The :class:`~openlp.core.lib.ui.projector.editform.Ui_ProjectorEditForm` class defines
    the user interface for the ProjectorEditForm dialog.
    """
    def setupUi(self, edit_projector_dialog):
        """
        Create the interface layout.
        """
        edit_projector_dialog.setObjectName('edit_projector_dialog')
        edit_projector_dialog.setWindowIcon(build_icon(u':/icon/openlp-logo-32x32.png'))
        edit_projector_dialog.setMinimumWidth(400)
        edit_projector_dialog.setModal(True)
        # Define the basic layout
        self.dialog_layout = QGridLayout(edit_projector_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.dialog_layout.setSpacing(8)
        self.dialog_layout.setContentsMargins(8, 8, 8, 8)
        # IP Address
        self.ip_label = QLabel(edit_projector_dialog)
        self.ip_label.setObjectName('projector_edit_ip_label')
        self.ip_text = QLineEdit(edit_projector_dialog)
        self.ip_text.setObjectName('projector_edit_ip_text')
        self.dialog_layout.addWidget(self.ip_label, 0, 0)
        self.dialog_layout.addWidget(self.ip_text, 0, 1)
        # Port number
        self.port_label = QLabel(edit_projector_dialog)
        self.port_label.setObjectName('projector_edit_ip_label')
        self.port_text = QLineEdit(edit_projector_dialog)
        self.port_text.setObjectName('projector_edit_port_text')
        self.dialog_layout.addWidget(self.port_label, 1, 0)
        self.dialog_layout.addWidget(self.port_text, 1, 1)
        # PIN
        self.pin_label = QLabel(edit_projector_dialog)
        self.pin_label.setObjectName('projector_edit_pin_label')
        self.pin_text = QLineEdit(edit_projector_dialog)
        self.pin_label.setObjectName('projector_edit_pin_text')
        self.dialog_layout.addWidget(self.pin_label, 2, 0)
        self.dialog_layout.addWidget(self.pin_text, 2, 1)
        # Name
        self.name_label = QLabel(edit_projector_dialog)
        self.name_label.setObjectName('projector_edit_name_label')
        self.name_text = QLineEdit(edit_projector_dialog)
        self.name_text.setObjectName('projector_edit_name_text')
        self.dialog_layout.addWidget(self.name_label, 3, 0)
        self.dialog_layout.addWidget(self.name_text, 3, 1)
        # Location
        self.location_label = QLabel(edit_projector_dialog)
        self.location_label.setObjectName('projector_edit_location_label')
        self.location_text = QLineEdit(edit_projector_dialog)
        self.location_text.setObjectName('projector_edit_location_text')
        self.dialog_layout.addWidget(self.location_label, 4, 0)
        self.dialog_layout.addWidget(self.location_text, 4, 1)
        # Notes
        self.notes_label = QLabel(edit_projector_dialog)
        self.notes_label.setObjectName('projector_edit_notes_label')
        self.notes_text = QPlainTextEdit(edit_projector_dialog)
        self.notes_text.setObjectName('projector_edit_notes_text')
        self.dialog_layout.addWidget(self.notes_label, 5, 0, alignment=QtCore.Qt.AlignTop)
        self.dialog_layout.addWidget(self.notes_text, 5, 1)
        # Time for the buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Help |
                                           QDialogButtonBox.Save |
                                           QDialogButtonBox.Cancel)
        self.dialog_layout.addWidget(self.button_box, 8, 0, 1, 2)

    def retranslateUi(self, edit_projector_dialog):
        if self.new_projector:
            title = translate('OpenLP.ProjectorEditForm', 'Add New Projector')
            self.projector.port = PJLINK_PORT
        else:
            title = translate('OpenLP.ProjectorEditForm', 'Edit Projector')
        edit_projector_dialog.setWindowTitle(title)
        self.ip_label.setText(translate('OpenLP.ProjectorEditForm', 'IP Address'))
        self.ip_text.setText(self.projector.ip)
        self.ip_text.setFocus()
        self.port_label.setText(translate('OpenLP.ProjectorEditForm', 'Port Number'))
        self.port_text.setText(str(self.projector.port))
        self.pin_label.setText(translate('OpenLP.ProjectorEditForm', 'PIN'))
        self.pin_text.setText(self.projector.pin)
        self.name_label.setText(translate('OpenLP.ProjectorEditForm', 'Name'))
        self.name_text.setText(self.projector.name)
        self.location_label.setText(translate('OpenLP.ProjectorEditForm', 'Location'))
        self.location_text.setText(self.projector.location)
        self.notes_label.setText(translate('OpenLP.ProjectorEditForm', 'Notes'))
        self.notes_text.clear()
        self.notes_text.insertPlainText(self.projector.notes)


class ProjectorEditForm(QDialog, Ui_ProjectorEditForm):
    """
    Class to add or edit a projector entry in the database.

    Fields that are editable:
        ip = Column(String(100))
        port = Column(String(8))
        pin = Column(String(20))
        name = Column(String(20))
        location = Column(String(30))
        notes = Column(String(200))
    """
    newProjector = pyqtSignal(str)
    editProjector = pyqtSignal(object)

    def __init__(self, parent=None, projectordb=None):
        super(ProjectorEditForm, self).__init__(parent=parent)
        self.projectordb = projectordb
        self.setupUi(self)
        self.button_box.accepted.connect(self.accept_me)
        self.button_box.helpRequested.connect(self.help_me)
        self.button_box.rejected.connect(self.cancel_me)

    def exec_(self, projector=None):
        if projector is None:
            self.projector = Projector()
            self.new_projector = True
        else:
            self.projector = projector
            self.new_projector = False
        self.retranslateUi(self)
        reply = QDialog.exec_(self)
        return reply

    @pyqtSlot()
    def accept_me(self):
        """
        Validate input before accepting input.
        """
        log.debug('accept_me() signal received')
        if len(self.name_text.text().strip()) < 1:
            QtGui.QMessageBox.warning(self,
                                      translate('OpenLP.ProjectorEdit', 'Name Not Set'),
                                      translate('OpenLP.ProjectorEdit',
                                                'You must enter a name for this entry.<br />'
                                                'Please enter a new name for this entry.'))
            valid = False
            return
        name = self.name_text.text().strip()
        record = self.projectordb.get_projector_by_name(name)
        if record is not None and record.id != self.projector.id:
            QtGui.QMessageBox.warning(self,
                                      translate('OpenLP.ProjectorEdit', 'Duplicate Name'),
                                      translate('OpenLP.ProjectorEdit',
                                                'There is already an entry with name "%s" in '
                                                'the database as ID "%s". <br />'
                                                'Please enter a different name.' % (name, record.id)))
            valid = False
            return
        adx = self.ip_text.text()
        valid = verify_ip_address(adx)
        if valid:
            ip = self.projectordb.get_projector_by_ip(adx)
            if ip is None:
                valid = True
                self.new_projector = True
            elif ip.id != self.projector.id:
                QtGui.QMessageBox.warning(self,
                                          translate('OpenLP.ProjectorWizard', 'Duplicate IP Address'),
                                          translate('OpenLP.ProjectorWizard',
                                                    'IP address "%s"<br />is already in the database as ID %s.'
                                                    '<br /><br />Please Enter a different IP address.' % (adx, ip.id)))
                valid = False
                return
        else:
            QtGui.QMessageBox.warning(self,
                                      translate('OpenLP.ProjectorWizard', 'Invalid IP Address'),
                                      translate('OpenLP.ProjectorWizard',
                                                'IP address "%s"<br>is not a valid IP address.'
                                                '<br /><br />Please enter a valid IP address.' % adx))
            valid = False
            return
        port = int(self.port_text.text())
        if port < 1000 or port > 32767:
            QtGui.QMessageBox.warning(self,
                                      translate('OpenLP.ProjectorWizard', 'Invalid Port Number'),
                                      translate('OpenLP.ProjectorWizard',
                                                'Port numbers below 1000 are reserved for admin use only, '
                                                '<br />and port numbers above 32767 are not currently usable.'
                                                '<br /><br />Please enter a valid port number between '
                                                ' 1000 and 32767.'
                                                '<br /><br />Default PJLink port is %s' % PJLINK_PORT))
            valid = False
        if valid:
            self.projector.ip = self.ip_text.text()
            self.projector.pin = self.pin_text.text()
            self.projector.port = int(self.port_text.text())
            self.projector.name = self.name_text.text()
            self.projector.location = self.location_text.text()
            self.projector.notes = self.notes_text.toPlainText()
            if self.new_projector:
                saved = self.projectordb.add_projector(self.projector)
            else:
                saved = self.projectordb.update_projector(self.projector)
            if not saved:
                QtGui.QMessageBox.warning(self,
                                          translate('OpenLP.ProjectorEditForm', 'Database Error'),
                                          translate('OpenLP.ProjectorEditForm',
                                                    'There was an error saving projector '
                                                    'information. See the log for the error'))
                return saved
            if self.new_projector:
                self.newProjector.emit(adx)
            else:
                self.editProjector.emit(self.projector)
            self.close()

    @pyqtSlot()
    def help_me(self):
        """
        Show a help message about the input fields.
        """
        log.debug('help_me() signal received')

    @pyqtSlot()
    def cancel_me(self):
        """
        Cancel button clicked - just close.
        """
        log.debug('cancel_me() signal received')
        self.close()
