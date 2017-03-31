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

    if (OpenLP.slide_type == "songs"){

      current_slide_lines = OpenLP.current_slide.split(/(<br>)/);
      current_text = '';

      for (line in current_slide_lines){
        if (current_slide_lines[line] == "<br>"){
          current_text = current_text + '<br />';
        } else {
          current_line_segments = current_slide_lines[line].split(/(<chord[\w\+#\/"='' ]*\/>)/);
          if (current_line_segments[0] != '') {
            // Process head of line
            current_text = current_text + '<span class="lyric-chord-block"><span class="lyric-chunk">' + current_line_segments[0] + '</span></span>';
          }
          // Process tail of line: <Tail> ::= (<Chord>|(<Chord><Lyric>))*
          prev_chunk_is_chord = false;
          hanging_lyric_pos = -1;
          for (segment=1; segment < current_line_segments.length; segment++){
            cur_seg = current_line_segments[segment];
            if (cur_seg.charAt(0) == "<"){
              // Current is chord
              cur_seg = cur_seg.replace(/<chord name[\s]?=[\s]?'/, '<span class="chord-chunk">');
              cur_seg = cur_seg.replace(/'[\s]?\/>/, "</span>");
              if (prev_chunk_is_chord == true) {
                current_text = current_text + '</span><span class="lyric-chord-block">' + cur_seg;
              } else {
                current_text = current_text + '<span class="lyric-chord-block">' + cur_seg;
              }
              prev_chunk_is_chord = true;
            } else {
              // Current is lyric
              if ((hanging_lyric_pos > 0) && (cur_seg.charAt(0).match(/[a-z]/i))) {
                current_text = current_text.slice(0, hanging_lyric_pos+1) + " midword" + current_text.slice(hanging_lyric_pos+1);
              }
              // recalc hanging_lyric_pos based on current_text length + offset
              hanging_lyric_pos = current_text.length + 23;
              current_text = current_text + '<span class="lyric-chunk">' + cur_seg + '</span></span>';
              prev_chunk_is_chord = false;
              if (!cur_seg.slice(-1).match(/[a-z]/i)){
                hanging_lyric_pos = -1;
              }
            }
          }
          if (prev_chunk_is_chord == true){
            current_text = current_text + '</span>';
          }
        }
      }
      $("#currentslide").html(current_text);

      next_slide_lines = OpenLP.next_slide.split(/(<br>)/);
      next_text = '';

      for (line in next_slide_lines){
        if (next_slide_lines[line] == "<br>"){
          next_text = next_text + '<br />';
        } else {
          next_line_segments = next_slide_lines[line].split(/(<chord[\w\+#\/"='' ]*\/>)/);
          if (next_line_segments[0] != '') {
            // Process head of line
            next_text = next_text + '<span class="next-lyric-chord-block"><span class="next-lyric-chunk">' + next_line_segments[0] + '</span></span>';
          }
          // Process tail of line: <Tail> ::= (<Chord>|(<Chord><Lyric>))*
          prev_chunk_is_chord = false;
          hanging_lyric_pos = -1;
          for (segment=1; segment < next_line_segments.length; segment++){
            cur_seg = next_line_segments[segment];
            if (cur_seg.charAt(0) == "<"){
              // Current is chord
              cur_seg = cur_seg.replace(/<chord name[\s]?=[\s]?'/, '<span class="next-chord-chunk">');
              cur_seg = cur_seg.replace(/'[\s]?\/>/, "</span>");
              if (prev_chunk_is_chord == true) {
                next_text = next_text + '</span><span class="next-lyric-chord-block">' + cur_seg;
              } else {
                next_text = next_text + '<span class="next-lyric-chord-block">' + cur_seg;
              }
              prev_chunk_is_chord = true;
            } else {
              // Current is lyric
              if ((hanging_lyric_pos > 0) && (cur_seg.charAt(0).match(/[a-z]/i))) {
                next_text = next_text.slice(0, hanging_lyric_pos+1) + " midword" + next_text.slice(hanging_lyric_pos+1);
              }
              // recalc hanging_lyric_pos based on current_text length + offset
              hanging_lyric_pos = next_text.length + 28;
              next_text = next_text + '<span class="next-lyric-chunk">' + cur_seg + '</span></span>';
              prev_chunk_is_chord = false;
              if (!cur_seg.slice(-1).match(/[a-z]/i)){
                hanging_lyric_pos = -1;
              }
            }
          }
          if (prev_chunk_is_chord == true){
            next_text = next_text + '</span>';
          }
        }
      }
      $("#nextslide").html(next_text);

      $('#currentslide>span').each(function(){
        element = $(this);
        if (element.children().length > 1){
          lyricWidth = $(element.children('.lyric-chunk')).width();
          chordOuterWidth = $(element.children('.chord-chunk')).outerWidth();
          if (lyricWidth < chordOuterWidth){
            if ($(element.children('.midword')).length > 0){
              spacerWidth = chordOuterWidth-element.width();
              element.append('<span class="midword-spacer">-</span>');
              if (spacerWidth < 16){ // TODO: Replace with relative size condition
                element.children('.midword-spacer').width(16);
              } else {
                element.children('.midword-spacer').width(spacerWidth);
              }
            } else {
              element.css("padding-right", chordOuterWidth-element.width());
            }
          }
        }
      });

    $('#nextslide>span').each(function(){
        element = $(this);
        if (element.children().length > 1){
          lyricWidth = $(element.children('.next-lyric-chunk')).width();
          chordOuterWidth = $(element.children('.next-chord-chunk')).outerWidth();
          if (lyricWidth < chordOuterWidth){
            if ($(element.children('.midword')).length > 0){
              spacerWidth = chordOuterWidth-element.width();
              element.append('<span class="next-midword-spacer">-</span>');
              if (spacerWidth < 16){ // TODO: Replace with relative size condition
                element.children('.next-midword-spacer').width(16);
              } else {
                element.children('.next-midword-spacer').width(spacerWidth);
              }
            } else {
              element.css("padding-right", chordOuterWidth-element.width());
            }
          }
        }
      });

    } else if (OpenLP.slide_type == "custom" || OpenLP.slide_type == "bibles"){
      current_text = "<div class =\"nonsong-block\"><p class=\"nonsong-line\">";
      current_text = current_text + OpenLP.current_slide.replace(/<br>/g, "</p><p class=\"nonsong-line\">");
      current_text = current_text + "</div>";
      next_text = "<div class =\"next-nonsong-block\"><p class=\"nonsong-line\">";
      next_text = next_text + OpenLP.next_slide.replace(/<br>/g, "</p><p class=\"nonsong-line\">");
      next_text = next_text + "</div>";
      $("#currentslide").html(current_text);
      $("#nextslide").html(next_text);
    }
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
          OpenLP.slide_type = data.slide_type;
          OpenLP.updateMusic();
        }
      }
    );
  },

  updateCapo: function() {
    OpenLP.capo = $("#caposelect").val();
    OpenLP.update_id = "Refresh";
  },

  nextSlide: function (event) {
    event.preventDefault();
    $.getJSON("/api/controller/live/next");
  },
  previousSlide: function (event) {
    event.preventDefault();
    $.getJSON("/api/controller/live/previous");
  }
}

OpenLP.update_id = "None";
OpenLP.capo = 0;

$(document).ready(function(){
    $("#caposelect").change(OpenLP.updateCapo);
    $("#controller-next").live("click", OpenLP.nextSlide);
    $("#controller-prev").live("click", OpenLP.previousSlide);
});


// Adjust document body size based on ?size=n parameter, if it exists
params = window.location.search.slice(1);
body_size = "16px";
if (params != ""){
  param_arr = params.split('&');
  for(var i=0; i<param_arr.length; i++){
    param_pair = param_arr[i].split('=');
    if (param_pair[0] == 'size'){
      body_size = param_pair[1] + "px";
    }
  }
}
$("html").css("font-size", body_size);

$.ajaxSetup({ cache: false });
setInterval("OpenLP.pollServer();", 500);
OpenLP.pollServer();
