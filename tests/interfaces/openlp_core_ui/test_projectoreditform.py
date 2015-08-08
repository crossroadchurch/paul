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
Interface tests to test the openlp.core.ui.projector.editform.ProjectorEditForm()
class and methods.
"""

from unittest import TestCase

from openlp.core.common import Registry, Settings
from openlp.core.lib.projector.db import Projector, ProjectorDB
from openlp.core.ui import ProjectorEditForm

from tests.functional import patch
from tests.helpers.testmixin import TestMixin
from tests.resources.projector.data import TEST1_DATA, TEST2_DATA


class TestProjectorEditForm(TestCase, TestMixin):
    """
    Test the methods in the ProjectorEditForm class
    """
    def setUp(self):
        """
        Create the UI and setup necessary options

        :return: None
        """
        self.build_settings()
        self.setup_application()
        Registry.create()
        with patch('openlp.core.lib.projector.db.init_url') as mocked_init_url:
            mocked_init_url.return_value = 'sqlite://'
            self.projectordb = ProjectorDB()
            self.projector_form = ProjectorEditForm(projectordb=self.projectordb)

    def tearDown(self):
        """
        Close database session.
        Delete all C++ objects at end so we don't segfault.

        :return: None
        """
        self.projectordb.session.close()
        del(self.projector_form)
        self.destroy_settings()

    def edit_form_add_projector_test(self):
        """
        Test projector edit form with no parameters creates a new entry.

        :return: None
        """
        # GIVEN: Mocked setup
        with patch('openlp.core.ui.projector.editform.QDialog.exec_'):

            # WHEN: Calling edit form with no parameters
            self.projector_form.exec_()
            item = self.projector_form.projector

            # THEN: Should be creating a new instance
            self.assertTrue(self.projector_form.new_projector,
                            'Projector edit form should be marked as a new entry')
            self.assertTrue((item.ip is None and item.name is None),
                            'Projector edit form should have a new Projector() instance to edit')

    def edit_form_edit_projector_test(self):
        """
        Test projector edit form with existing projector entry

        :return:
        """
        # GIVEN: Mocked setup
        with patch('openlp.core.ui.projector.editform.QDialog.exec_'):

            # WHEN: Calling edit form with existing projector instance
            self.projector_form.exec_(projector=TEST1_DATA)
            item = self.projector_form.projector

            # THEN: Should be editing an existing entry
            self.assertFalse(self.projector_form.new_projector,
                             'Projector edit form should be marked as existing entry')
            self.assertTrue((item.ip is TEST1_DATA.ip and item.name is TEST1_DATA.name),
                            'Projector edit form should have TEST1_DATA() instance to edit')
