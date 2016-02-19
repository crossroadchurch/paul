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

    current_slide_lines = OpenLP.current_slide.split(/(<br>)/);
    current_text = ''

    for (line in current_slide_lines){
      if (current_slide_lines[line] == "<br>"){
        current_text = current_text + '<br />'
      } else {
        current_line_segments = current_slide_lines[line].split(/(<chord[\w\+#"='' ]* \/>)/);
        if (current_line_segments[0] != '') {
          // Process head of line
          current_text = current_text + '<span class="lyric-chord-block"><span class="lyric-chunk">' + current_line_segments[0] + '</span></span>'
        }
        // Process tail of line: <Tail> ::= (<Chord>|(<Chord><Lyric>))*
        prev_chunk_is_chord = false;
        hanging_lyric_pos = -1;
        for (segment=1; segment < current_line_segments.length; segment++){
          cur_seg = current_line_segments[segment];
          if (cur_seg.charAt(0) == "<"){
            // Current is chord
            cur_seg = cur_seg.replace(/<chord name = '/, '<span class="chord-chunk">');
            cur_seg = cur_seg.replace(/' \/>/, "</span>");
            if (prev_chunk_is_chord == true) {
              current_text = current_text + '</span><span class="lyric-chord-block">' + cur_seg;
            } else {
              current_text = current_text + '<span class="lyric-chord-block">' + cur_seg;
            }
            prev_chunk_is_chord = true;
          } else {
            // Current is lyric
            console.log("Start value: " + hanging_lyric_pos);
            if ((hanging_lyric_pos > 0) && (cur_seg.charAt(0).match(/[a-z]/i))) {
              console.log(current_text.slice(0, hanging_lyric_pos+1));
              console.log(current_text.slice(hanging_lyric_pos+1));
              current_text = current_text.slice(0, hanging_lyric_pos+1) + " midword" + current_text.slice(hanging_lyric_pos+1);
              console.log(current_text);
            }
            // recalc hanging_lyric_pos based on current_text length + offset
            hanging_lyric_pos = current_text.length + 23;
            current_text = current_text + '<span class="lyric-chunk">' + cur_seg + '</span></span>';
            prev_chunk_is_chord = false;
            if (!cur_seg.slice(-1).match(/[a-z]/i)){
              hanging_lyric_pos = -1;
            }
            console.log("End value: " + hanging_lyric_pos);
          }
        }
        if (prev_chunk_is_chord == true){
          current_text = current_text + '</span>';
        }
      }
    }
    $("#currentslide").html(current_text);

    next_text = OpenLP.next_slide.replace(/<chord name = '/g, '<span class="next-chord-line">');
    next_text = next_text.replace(/' \/>/g, "</span>");
    next_text = '<span class="next-lyric-line">' + next_text + '</span>';
    next_text = next_text.replace(/<br>/g, '</span><span class="next-lyric-line">');
    $("#nextslide").html(next_text);

    $('#currentslide>span').each(function(){
      element = $(this);
      if (element.children().length > 1){
        lyricWidth = $(element.children('.lyric-chunk')).width();
        chordWidth = $(element.children('.chord-chunk')).width();
        if (lyricWidth < chordWidth){
          if ($(element.children('.midword')).length > 0){
            element.append('<span class="midword-spacer">-</span>');
            element.children('.midword-spacer').width(chordWidth-element.width());
          } else {
            element.css("padding-right", chordWidth-element.width());
          }
        }
      }
    });
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
  },

  updateCapo: function() {
    OpenLP.capo = $("#caposelect").val();
    OpenLP.update_id = "Refresh";
  }
}

OpenLP.update_id = "None";
OpenLP.capo = 0;

$(document).ready(function(){
    $("#caposelect").change(OpenLP.updateCapo);
});

$.ajaxSetup({ cache: false });
setInterval("OpenLP.pollServer();", 500);
OpenLP.pollServer();