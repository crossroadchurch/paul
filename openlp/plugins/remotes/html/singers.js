/******************************************************************************
 * OpenLP - Open Source Lyrics Projection                                      *
 * --------------------------------------------------------------------------- *
 * Copyright (c) 2008-2015 OpenLP Developers                                   *
 * --------------------------------------------------------------------------- *
 * This program is free software; you can redistribute it and/or modify it     *
 * under the terms of the GNU General Public License as published by the Free  *
 * Software Foundation; version 2 of the License.                              *
 *                                                                             *
 * This program is distributed in the hope that it will be useful, but WITHOUT *
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    *
 * more details.                                                               *
 *                                                                             *
 * You should have received a copy of the GNU General Public License along     *
 * with this program; if not, write to the Free Software Foundation, Inc., 59  *
 * Temple Place, Suite 330, Boston, MA 02111-1307 USA                          *
 ******************************************************************************/
window.OpenLP = {

  updateMusic: function () {

    $("#playedkey").html(OpenLP.played_key);

    verse_order_list = "<ul><li>" + OpenLP.song_order.split(" ").join("</li><li>") + "</li></ul>";
    verse_order_list = verse_order_list.replace("(", '<span class="current-verse">');
    verse_order_list = verse_order_list.replace(")", '</span>');
    $("#verseorder").html(verse_order_list);

    // Take out chords, put each line in a <p> element
    current_slide_text = '<p>' + OpenLP.current_slide + '</p>';
    current_slide_text = current_slide_text.replace(/<br>/g, '</p>\n<p>');
    current_slide_text = current_slide_text.replace(/<chord[\w\+#\/"='' ]*\/>/g, '');
    $("#currentslide").html(current_slide_text);

    next_slide_text = '<p>' + OpenLP.next_slide + '</p>';
    next_slide_text = next_slide_text.replace(/<br>/g, '</p>\n<p>');
    next_slide_text = next_slide_text.replace(/<chord[\w\+#\/"='' ]*\/>/g, '');
    $("#nextslide").html(next_slide_text);

  },

  pollServer: function () {
    $.getJSON(
      "/silas/update=" + OpenLP.update_id + "&capo=" + OpenLP.capo,
      function (data, status) {
        if (data.status == "update") {
          OpenLP.update_id = data.update_id;
          OpenLP.current_slide = data.current_slide;
          OpenLP.next_slide = data.next_slide;
          OpenLP.song_order = data.song_order;
          OpenLP.played_key = data.played_key;
          OpenLP.updateMusic();
        }
      }
    );
  }

}

OpenLP.update_id = "None";

$.ajaxSetup({ cache: false });
setInterval("OpenLP.pollServer();", 500);
OpenLP.pollServer();
