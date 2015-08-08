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
The :mod:`upgrade` module provides a way for the database and schema that is the
backend for the SongsUsage plugin
"""
import logging

from sqlalchemy import Column, types

from openlp.core.lib.db import get_upgrade_op

log = logging.getLogger(__name__)
__version__ = 1


def upgrade_1(session, metadata):
    """
    Version 1 upgrade.

    This upgrade adds two new fields to the songusage database

    :param session: SQLAlchemy Session object
    :param metadata: SQLAlchemy MetaData object
    """
    op = get_upgrade_op(session)
    op.add_column('songusage_data', Column('plugin_name', types.Unicode(20), server_default=''))
    op.add_column('songusage_data', Column('source', types.Unicode(10), server_default=''))
