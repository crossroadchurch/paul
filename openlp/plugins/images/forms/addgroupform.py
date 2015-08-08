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

from PyQt4 import QtGui

from openlp.core.common import translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.images.forms.addgroupdialog import Ui_AddGroupDialog


class AddGroupForm(QtGui.QDialog, Ui_AddGroupDialog):
    """
    This class implements the 'Add group' form for the Images plugin.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(AddGroupForm, self).__init__(parent)
        self.setupUi(self)

    def exec_(self, clear=True, show_top_level_group=False, selected_group=None):
        """
        Show the form.

        :param clear:  Set to False if the text input box should not be cleared when showing the dialog (default: True).
        :param show_top_level_group:  Set to True when "-- Top level group --" should be showed as first item
        (default: False).
        :param selected_group: The ID of the group that should be selected by default when showing the dialog.
        """
        if clear:
            self.name_edit.clear()
        self.name_edit.setFocus()
        if show_top_level_group and not self.parent_group_combobox.top_level_group_added:
            self.parent_group_combobox.insertItem(0, translate('ImagePlugin.MediaItem', '-- Top-level group --'), 0)
            self.parent_group_combobox.top_level_group_added = True
        if selected_group is not None:
            for i in range(self.parent_group_combobox.count()):
                if self.parent_group_combobox.itemData(i) == selected_group:
                    self.parent_group_combobox.setCurrentIndex(i)
        return QtGui.QDialog.exec_(self)

    def accept(self):
        """
        Override the accept() method from QDialog to make sure something is entered in the text input box.
        """
        if not self.name_edit.text():
            critical_error_message_box(message=translate('ImagePlugin.AddGroupForm',
                                                         'You need to type in a group name.'))
            self.name_edit.setFocus()
            return False
        else:
            return QtGui.QDialog.accept(self)
