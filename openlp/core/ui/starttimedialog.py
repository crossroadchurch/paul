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
The UI widgets for the time dialog
"""
from PyQt4 import QtCore, QtGui

from openlp.core.common import UiStrings, translate
from openlp.core.lib import build_icon
from openlp.core.lib.ui import create_button_box


class Ui_StartTimeDialog(object):
    """
    The UI widgets for the time dialog
    """
    def setupUi(self, StartTimeDialog):
        """
        Set up the UI
        """
        StartTimeDialog.setObjectName('StartTimeDialog')
        StartTimeDialog.setWindowIcon(build_icon(u':/icon/openlp-logo.svg'))
        StartTimeDialog.resize(350, 10)
        self.dialog_layout = QtGui.QGridLayout(StartTimeDialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.start_label = QtGui.QLabel(StartTimeDialog)
        self.start_label.setObjectName('start_label')
        self.start_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.dialog_layout.addWidget(self.start_label, 0, 1, 1, 1)
        self.finish_label = QtGui.QLabel(StartTimeDialog)
        self.finish_label.setObjectName('finish_label')
        self.finish_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.dialog_layout.addWidget(self.finish_label, 0, 2, 1, 1)
        self.length_label = QtGui.QLabel(StartTimeDialog)
        self.length_label.setObjectName('start_label')
        self.length_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.dialog_layout.addWidget(self.length_label, 0, 3, 1, 1)
        self.hour_label = QtGui.QLabel(StartTimeDialog)
        self.hour_label.setObjectName('hour_label')
        self.dialog_layout.addWidget(self.hour_label, 1, 0, 1, 1)
        self.hour_spin_box = QtGui.QSpinBox(StartTimeDialog)
        self.hour_spin_box.setObjectName('hour_spin_box')
        self.hour_spin_box.setMinimum(0)
        self.hour_spin_box.setMaximum(4)
        self.dialog_layout.addWidget(self.hour_spin_box, 1, 1, 1, 1)
        self.hour_finish_spin_box = QtGui.QSpinBox(StartTimeDialog)
        self.hour_finish_spin_box.setObjectName('hour_finish_spin_box')
        self.hour_finish_spin_box.setMinimum(0)
        self.hour_finish_spin_box.setMaximum(4)
        self.dialog_layout.addWidget(self.hour_finish_spin_box, 1, 2, 1, 1)
        self.hour_finish_label = QtGui.QLabel(StartTimeDialog)
        self.hour_finish_label.setObjectName('hour_label')
        self.hour_finish_label.setAlignment(QtCore.Qt.AlignRight)
        self.dialog_layout.addWidget(self.hour_finish_label, 1, 3, 1, 1)
        self.minute_label = QtGui.QLabel(StartTimeDialog)
        self.minute_label.setObjectName('minute_label')
        self.dialog_layout.addWidget(self.minute_label, 2, 0, 1, 1)
        self.minute_spin_box = QtGui.QSpinBox(StartTimeDialog)
        self.minute_spin_box.setObjectName('minute_spin_box')
        self.minute_spin_box.setMinimum(0)
        self.minute_spin_box.setMaximum(59)
        self.dialog_layout.addWidget(self.minute_spin_box, 2, 1, 1, 1)
        self.minute_finish_spin_box = QtGui.QSpinBox(StartTimeDialog)
        self.minute_finish_spin_box.setObjectName('minute_finish_spin_box')
        self.minute_finish_spin_box.setMinimum(0)
        self.minute_finish_spin_box.setMaximum(59)
        self.dialog_layout.addWidget(self.minute_finish_spin_box, 2, 2, 1, 1)
        self.minute_finish_label = QtGui.QLabel(StartTimeDialog)
        self.minute_finish_label.setObjectName('minute_label')
        self.minute_finish_label.setAlignment(QtCore.Qt.AlignRight)
        self.dialog_layout.addWidget(self.minute_finish_label, 2, 3, 1, 1)
        self.second_label = QtGui.QLabel(StartTimeDialog)
        self.second_label.setObjectName('second_label')
        self.dialog_layout.addWidget(self.second_label, 3, 0, 1, 1)
        self.second_spin_box = QtGui.QSpinBox(StartTimeDialog)
        self.second_spin_box.setObjectName('second_spin_box')
        self.second_spin_box.setMinimum(0)
        self.second_spin_box.setMaximum(59)
        self.second_finish_spin_box = QtGui.QSpinBox(StartTimeDialog)
        self.second_finish_spin_box.setObjectName('second_finish_spin_box')
        self.second_finish_spin_box.setMinimum(0)
        self.second_finish_spin_box.setMaximum(59)
        self.dialog_layout.addWidget(self.second_finish_spin_box, 3, 2, 1, 1)
        self.second_finish_label = QtGui.QLabel(StartTimeDialog)
        self.second_finish_label.setObjectName('second_label')
        self.second_finish_label.setAlignment(QtCore.Qt.AlignRight)
        self.dialog_layout.addWidget(self.second_finish_label, 3, 3, 1, 1)
        self.dialog_layout.addWidget(self.second_spin_box, 3, 1, 1, 1)
        self.button_box = create_button_box(StartTimeDialog, 'button_box', ['cancel', 'ok'])
        self.dialog_layout.addWidget(self.button_box, 5, 2, 1, 2)
        self.retranslateUi(StartTimeDialog)
        self.setMaximumHeight(self.sizeHint().height())

    def retranslateUi(self, StartTimeDialog):
        """
        Update the translations on the fly
        """
        self.setWindowTitle(translate('OpenLP.StartTime_form', 'Item Start and Finish Time'))
        self.hour_spin_box.setSuffix(UiStrings().Hours)
        self.minute_spin_box.setSuffix(UiStrings().Minutes)
        self.second_spin_box.setSuffix(UiStrings().Seconds)
        self.hour_finish_spin_box.setSuffix(UiStrings().Hours)
        self.minute_finish_spin_box.setSuffix(UiStrings().Minutes)
        self.second_finish_spin_box.setSuffix(UiStrings().Seconds)
        self.hour_label.setText(translate('OpenLP.StartTime_form', 'Hours:'))
        self.minute_label.setText(translate('OpenLP.StartTime_form', 'Minutes:'))
        self.second_label.setText(translate('OpenLP.StartTime_form', 'Seconds:'))
        self.start_label.setText(translate('OpenLP.StartTime_form', 'Start'))
        self.finish_label.setText(translate('OpenLP.StartTime_form', 'Finish'))
        self.length_label.setText(translate('OpenLP.StartTime_form', 'Length'))
