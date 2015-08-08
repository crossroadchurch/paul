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
Package to test the openlp.core.ui.media.phononplayer package.
"""
from unittest import TestCase
from tests.functional import patch

from openlp.core.ui.media.phononplayer import PhononPlayer


class TestPhononPlayer(TestCase):
    """
    Test the functions in the :mod:`phononplayer` module.
    """

    def check_available_mac_test(self):
        """
        Simple test of phononplayer availability on Mac OS X
        """
        # GIVEN: A PhononPlayer and a mocked is_macosx
        with patch('openlp.core.ui.media.phononplayer.is_macosx') as mocked_is_macosx:
            mocked_is_macosx.return_value = True
            phonon_player = PhononPlayer(None)

            # WHEN: An checking if the player is available
            available = phonon_player.check_available()

            # THEN: The player should not be available on Mac OS X
            self.assertEqual(False, available, 'The PhononPlayer should not be available on Mac OS X.')

    def check_available_non_mac_test(self):
        """
        Simple test of phononplayer availability when not on Mac OS X
        """
        # GIVEN: A PhononPlayer and a mocked is_macosx
        with patch('openlp.core.ui.media.phononplayer.is_macosx') as mocked_is_macosx:
            mocked_is_macosx.return_value = False
            phonon_player = PhononPlayer(None)

            # WHEN: An checking if the player is available
            available = phonon_player.check_available()

            # THEN: The player should be available when not on Mac OS X
            self.assertEqual(True, available, 'The PhononPlayer should be available when not on Mac OS X.')
