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
Provide Registry Services
"""
from openlp.core.common import Registry, de_hump


class RegistryMixin(object):
    """
    This adds registry components to classes to use at run time.
    """
    def __init__(self, parent):
        """
        Register the class and bootstrap hooks.
        """
        try:
            super(RegistryMixin, self).__init__(parent)
        except TypeError:
            super(RegistryMixin, self).__init__()
        Registry().register(de_hump(self.__class__.__name__), self)
        Registry().register_function('bootstrap_initialise', self.bootstrap_initialise)
        Registry().register_function('bootstrap_post_set_up', self.bootstrap_post_set_up)

    def bootstrap_initialise(self):
        """
        Dummy method to be overridden
        """
        pass

    def bootstrap_post_set_up(self):
        """
        Dummy method to be overridden
        """
        pass
