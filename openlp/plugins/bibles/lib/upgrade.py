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
The :mod:`upgrade` module provides a way for the database and schema that is the backend for the Bibles plugin.
"""
import logging

from sqlalchemy import delete, func, insert, select

log = logging.getLogger(__name__)
__version__ = 1


# TODO: When removing an upgrade path the ftw-data needs updating to the minimum supported version
def upgrade_1(session, metadata):
    """
    Version 1 upgrade.

    This upgrade renames a number of keys to a single naming convention.
    """
    metadata_table = metadata.tables['metadata']
    # Copy "Version" to "name" ("version" used by upgrade system)
    try:
        session.execute(insert(metadata_table).values(
            key='name',
            value=select(
                [metadata_table.c.value],
                metadata_table.c.key == 'Version'
            ).as_scalar()
        ))
        session.execute(delete(metadata_table).where(metadata_table.c.key == 'Version'))
    except:
        log.exception('Exception when upgrading Version')
    # Copy "Copyright" to "copyright"
    try:
        session.execute(insert(metadata_table).values(
            key='copyright',
            value=select(
                [metadata_table.c.value],
                metadata_table.c.key == 'Copyright'
            ).as_scalar()
        ))
        session.execute(delete(metadata_table).where(metadata_table.c.key == 'Copyright'))
    except:
        log.exception('Exception when upgrading Copyright')
    # Copy "Permissions" to "permissions"
    try:
        session.execute(insert(metadata_table).values(
            key='permissions',
            value=select(
                [metadata_table.c.value],
                metadata_table.c.key == 'Permissions'
            ).as_scalar()
        ))
        session.execute(delete(metadata_table).where(metadata_table.c.key == 'Permissions'))
    except:
        log.exception('Exception when upgrading Permissions')
    # Copy "Bookname language" to "book_name_language"
    try:
        value_count = session.execute(
            select(
                [func.count(metadata_table.c.value)],
                metadata_table.c.key == 'Bookname language'
            )
        ).scalar()
        if value_count > 0:
            session.execute(insert(metadata_table).values(
                key='book_name_language',
                value=select(
                    [metadata_table.c.value],
                    metadata_table.c.key == 'Bookname language'
                ).as_scalar()
            ))
            session.execute(delete(metadata_table).where(metadata_table.c.key == 'Bookname language'))
    except:
        log.exception('Exception when upgrading Bookname language')
    # Copy "download source" to "download_source"
    try:
        value_count = session.execute(
            select(
                [func.count(metadata_table.c.value)],
                metadata_table.c.key == 'download source'
            )
        ).scalar()
        log.debug('download source: %s', value_count)
        if value_count > 0:
            session.execute(insert(metadata_table).values(
                key='download_source',
                value=select(
                    [metadata_table.c.value],
                    metadata_table.c.key == 'download source'
                ).as_scalar()
            ))
            session.execute(delete(metadata_table).where(metadata_table.c.key == 'download source'))
    except:
        log.exception('Exception when upgrading download source')
    # Copy "download name" to "download_name"
    try:
        value_count = session.execute(
            select(
                [func.count(metadata_table.c.value)],
                metadata_table.c.key == 'download name'
            )
        ).scalar()
        log.debug('download name: %s', value_count)
        if value_count > 0:
            session.execute(insert(metadata_table).values(
                key='download_name',
                value=select(
                    [metadata_table.c.value],
                    metadata_table.c.key == 'download name'
                ).as_scalar()
            ))
            session.execute(delete(metadata_table).where(metadata_table.c.key == 'download name'))
    except:
        log.exception('Exception when upgrading download name')
    # Copy "proxy server" to "proxy_server"
    try:
        value_count = session.execute(
            select(
                [func.count(metadata_table.c.value)],
                metadata_table.c.key == 'proxy server'
            )
        ).scalar()
        log.debug('proxy server: %s', value_count)
        if value_count > 0:
            session.execute(insert(metadata_table).values(
                key='proxy_server',
                value=select(
                    [metadata_table.c.value],
                    metadata_table.c.key == 'proxy server'
                ).as_scalar()
            ))
            session.execute(delete(metadata_table).where(metadata_table.c.key == 'proxy server'))
    except:
        log.exception('Exception when upgrading proxy server')
    # Copy "proxy username" to "proxy_username"
    try:
        value_count = session.execute(
            select(
                [func.count(metadata_table.c.value)],
                metadata_table.c.key == 'proxy username'
            )
        ).scalar()
        log.debug('proxy username: %s', value_count)
        if value_count > 0:
            session.execute(insert(metadata_table).values(
                key='proxy_username',
                value=select(
                    [metadata_table.c.value],
                    metadata_table.c.key == 'proxy username'
                ).as_scalar()
            ))
            session.execute(delete(metadata_table).where(metadata_table.c.key == 'proxy username'))
    except:
        log.exception('Exception when upgrading proxy username')
    # Copy "proxy password" to "proxy_password"
    try:
        value_count = session.execute(
            select(
                [func.count(metadata_table.c.value)],
                metadata_table.c.key == 'proxy password'
            )
        ).scalar()
        log.debug('proxy password: %s', value_count)
        if value_count > 0:
            session.execute(insert(metadata_table).values(
                key='proxy_password',
                value=select(
                    [metadata_table.c.value],
                    metadata_table.c.key == 'proxy password'
                ).as_scalar()
            ))
            session.execute(delete(metadata_table).where(metadata_table.c.key == 'proxy password'))
    except:
        log.exception('Exception when upgrading proxy password')
    try:
        session.execute(delete(metadata_table).where(metadata_table.c.key == 'dbversion'))
    except:
        log.exception('Exception when deleting dbversion')
    session.commit()
