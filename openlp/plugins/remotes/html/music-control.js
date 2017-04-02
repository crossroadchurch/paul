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

    verse_control_list = "";
    verse_list = "";

    if (OpenLP.slide_type == "songs"){
      verse_list = OpenLP.song_order.split(" ");
      subpage_list = OpenLP.subpages.split(" ");
      
      subpage_sum = 0
      for (i=0; i < verse_list.length; i++){
        if (verse_list[i].charAt(0) == "(") {
          verse_control_list = verse_control_list + 
            "<button class='verse-button current-verse-button' onclick='OpenLP.changeVerse(" + subpage_sum + ")'>" + 
            verse_list[i].replace("(", "").replace(")","") +
            "</button>";
        } else {
          verse_control_list = verse_control_list + 
            "<button class='verse-button' onclick='OpenLP.changeVerse(" + subpage_sum + ")'>" + 
            verse_list[i] +
            "</button>";
        }
        subpage_sum = subpage_sum + parseInt(subpage_list[i]);
      }
    } else {
      verse_control_list = "<span class='non-song-title'>" + OpenLP.song_order + "</div>";
    }
    $("#verseorder").html(verse_control_list);

    /* Update widths of verse buttons to make sure they can all be seen */
    header_width = $("#header").width();
    keyandcapo_width = $("#keyandcapo").width();
    button_margin = parseInt($(".verse-button").css("margin-right"));
    buttons_width = header_width-keyandcapo_width - (button_margin * verse_list.length);
    max_button_width = Math.floor(buttons_width / verse_list.length);
    pref_width = 6 * parseInt($("html").css("font-size")); /* 6rem */
    actual_width = Math.min(pref_width, max_button_width);
    $(".verse-button").css("width", actual_width + "px");

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
          OpenLP.subpages = data.subpages;
          OpenLP.updateMusic();
        }
      }
    );
    $.getJSON(
      "/api/service/list",
      function (data, status) {
        item_list = data.results.items;
        if (item_list.length > 0) {
          temp_menu = "<ul class='jq-dropdown-menu'>";
          // Build up song choice menu, place divider at current song location
          for (i=0; i<item_list.length; i++){
            if (item_list[i].selected == false) {
              temp_menu = temp_menu + "<li class='menu-song-item'><a onclick='OpenLP.changeSong(" + i + ")' class='menu-song-link'>" + item_list[i].title + "</a></li>";
            } else {
              temp_menu = temp_menu + "<li class='menu-song-current-item'><a>" + item_list[i].title + "</a></li>";
            }
          }
          temp_menu = temp_menu + "</ul>";        
        } else {
          temp_menu = "<ul class='jq-dropdown-menu'></ul>";
        }
        if (temp_menu != OpenLP.menustring) {
            $("#jq-dropdown-1").html(temp_menu);
            OpenLP.menustring = temp_menu;
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
  },

  changeVerse: function(id) {
    text = "{\"request\": {\"id\": " + id + "}}";
    $.getJSON(
      "/api/controller/live/set",
      {"data": text}
    );
  },

  changeSong: function(id) {
    text = "{\"request\": {\"id\": " + id + "}}";
    $.getJSON(
      "/api/service/set",
      {"data": text}
    );
  }
}

OpenLP.update_id = "None";
OpenLP.capo = 0;
OpenLP.menustring = "";

$(document).ready(function(){
    $("#caposelect").change(OpenLP.updateCapo);
    $("#controller-next").on("click", OpenLP.nextSlide);
    $("#controller-prev").on("click", OpenLP.previousSlide);
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
