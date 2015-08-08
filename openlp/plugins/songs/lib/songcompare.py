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
The :mod:`songcompare` module provides functionality to search for
duplicate songs. It has one single :function:`songs_probably_equal`.

The algorithm is based on the diff algorithm.
First a diffset is calculated for two songs.
To compensate for typos all differences that are smaller than a
limit (<max_typo_size) and are surrounded by larger equal blocks
(>min_fragment_size) are removed and the surrounding equal parts are merged.
Finally two conditions can qualify a song tuple to be a duplicate:
1. There is a block of equal content that is at least min_block_size large.
   This condition should hit for all larger songs that have a long enough
   equal part. Even if only one verse is equal this condition should still hit.
2. Two thirds of the smaller song is contained in the larger song.
   This condition should hit if one of the two songs (or both) is small (smaller
   than the min_block_size), but most of the song is contained in the other song.
"""

import difflib


MIN_FRAGMENT_SIZE = 5
MIN_BLOCK_SIZE = 70
MAX_TYPO_SIZE = 3


def songs_probably_equal(song_tupel):
    """
    Calculate and return whether two songs are probably equal.

    :param song_tupel: A tuple of two songs to compare.
    """
    song1, song2 = song_tupel
    pos1, lyrics1 = song1
    pos2, lyrics2 = song2
    if len(lyrics1) < len(lyrics2):
        small = lyrics1
        large = lyrics2
    else:
        small = lyrics2
        large = lyrics1
    differ = difflib.SequenceMatcher(a=large, b=small)
    diff_tuples = differ.get_opcodes()
    diff_no_typos = _remove_typos(diff_tuples)
    # Check 1: Similarity based on the absolute length of equal parts.
    # Calculate the total length of all equal blocks of the set.
    # Blocks smaller than min_block_size are not counted.
    length_of_equal_blocks = 0
    for element in diff_no_typos:
        if element[0] == "equal" and _op_length(element) >= MIN_BLOCK_SIZE:
            length_of_equal_blocks += _op_length(element)

    if length_of_equal_blocks >= MIN_BLOCK_SIZE:
        return pos1, pos2
    # Check 2: Similarity based on the relative length of the longest equal block.
    # Calculate the length of the largest equal block of the diff set.
    length_of_longest_equal_block = 0
    for element in diff_no_typos:
        if element[0] == "equal" and _op_length(element) > length_of_longest_equal_block:
            length_of_longest_equal_block = _op_length(element)
    if length_of_longest_equal_block > len(small) * 2 // 3:
        return pos1, pos2
    # Both checks failed. We assume the songs are not equal.
    return None


def _op_length(opcode):
    """
    Return the length of a given difference.

    :param opcode:  The difference.
    """
    return max(opcode[2] - opcode[1], opcode[4] - opcode[3])


def _remove_typos(diff):
    """
    Remove typos from a diff set. A typo is a small difference (<max_typo_size)
    surrounded by larger equal passages (>min_fragment_size).

    :param diff: The diff set to remove the typos from.
    """
    # Remove typo at beginning of the string.
    if len(diff) >= 2:
        if diff[0][0] != "equal" and _op_length(diff[0]) <= MAX_TYPO_SIZE and _op_length(diff[1]) >= MIN_FRAGMENT_SIZE:
            del diff[0]
    # Remove typos in the middle of the string.
    if len(diff) >= 3:
        for index in range(len(diff) - 3, -1, -1):
            if _op_length(diff[index]) >= MIN_FRAGMENT_SIZE and diff[index + 1][0] != "equal" and \
                    _op_length(diff[index + 1]) <= MAX_TYPO_SIZE and _op_length(diff[index + 2]) >= MIN_FRAGMENT_SIZE:
                del diff[index + 1]
    # Remove typo at the end of the string.
    if len(diff) >= 2:
        if _op_length(diff[-2]) >= MIN_FRAGMENT_SIZE and diff[-1][0] != "equal" \
                and _op_length(diff[-1]) <= MAX_TYPO_SIZE:
            del diff[-1]

    # Merge the bordering equal passages that occured by removing differences.
    for index in range(len(diff) - 2, -1, -1):
        if diff[index][0] == "equal" and _op_length(diff[index]) >= MIN_FRAGMENT_SIZE and \
                             diff[index + 1][0] == "equal" and _op_length(diff[index + 1]) >= MIN_FRAGMENT_SIZE:
            diff[index] = ("equal", diff[index][1], diff[index + 1][2], diff[index][3], diff[index + 1][4])
            del diff[index + 1]
    return diff
