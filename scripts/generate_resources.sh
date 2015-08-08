#!/bin/sh
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
#
# This script automates the generation of resources.py for OpenLP saving a
# backup of the old resources, inserting the coding and copyright header and
# conforming it to the project coding standards.
#
# To make use of the script:
# 1 - Add the new image files in resources/images/
# 2 - Modify resources/images/openlp-2.qrc as appropriate
# 3 - run sh scripts/generate_resources.sh
#
# Once you have confirmed the resources are correctly modified to an updated,
# working state you may optionally remove openlp/core/resources.py.old
#
###############################################################################
# Backup the existing resources
mv openlp/core/resources.py openlp/core/resources.py.old

# Create the new data from the updated qrc
pyrcc4 -py3 -o openlp/core/resources.py.new resources/images/openlp-2.qrc

# Remove patch breaking lines
cat openlp/core/resources.py.new | sed '/# Created: /d;/#      by: /d' > openlp/core/resources.py

# Patch resources.py to OpenLP coding style
patch --posix -s openlp/core/resources.py scripts/resources.patch

# Remove temporary file
rm openlp/core/resources.py.new 2>/dev/null
rm openlp/core/resources.py.old 2>/dev/null
rm openlp/core/resources.py.orig 2>/dev/null
