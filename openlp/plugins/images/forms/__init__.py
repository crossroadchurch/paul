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
Forms in OpenLP are made up of two classes. One class holds all the graphical elements, like buttons and lists, and the
other class holds all the functional code, like slots and loading and saving.

The first class, commonly known as the **Dialog** class, is typically named ``Ui_<name>Dialog``. It is a slightly
modified version of the class that the ``pyuic4`` command produces from Qt4's .ui file. Typical modifications will be
converting most strings from "" to '' and using OpenLP's ``translate()`` function for translating strings.

The second class, commonly known as the **Form** class, is typically named ``<name>Form``. This class is the one which
is instantiated and used. It uses dual inheritance to inherit from (usually) QtGui.QDialog and the Ui class mentioned
above, like so::

    class AuthorsForm(QtGui.QDialog, Ui_AuthorsDialog):

        def __init__(self, parent=None):
            super(AuthorsForm, self).__init__(parent)
            self.setupUi(self)

This allows OpenLP to use ``self.object`` for all the GUI elements while keeping them separate from the functionality,
so that it is easier to recreate the GUI from the .ui files later if necessary.
"""

from .addgroupform import AddGroupForm
from .choosegroupform import ChooseGroupForm
