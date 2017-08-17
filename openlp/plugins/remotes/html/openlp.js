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

book_data = [["Gen", "law", 50, "Genesis"],
  ["Exo", "law", 40, "Exodus"],
  ["Lev", "law", 27, "Leviticus"],
  ["Num", "law", 36, "Numbers"],
  ["Deut", "law", 34, "Deuteronomy"],
  ["Josh", "history", 24, "Joshua"],
  ["Judg", "history", 21, "Judges"],
  ["Ruth", "history", 4, "Ruth"],
  ["1 Sam", "history", 31, "1 Samuel"],
  ["2 Sam", "history", 24, "2 Samue;"],
  ["1 Ki", "history", 22, "1 Kings"],
  ["2 Ki", "history", 25, "2 Kings"],
  ["1 Chr", "history", 29, "1 Chronicles"],
  ["2 Chr", "history", 36, "2 Chronicles"],
  ["Ezra", "history", 10, "Ezra"],
  ["Neh", "history", 13, "Nehemiah"],
  ["Esth", "history", 10, "Esther"],
  ["Job", "wisdom", 42, "Job"],
  ["Psalm", "wisdom", 150, "Psalms"],
  ["Prov", "wisdom", 31, "Proverbs"],
  ["Eccl", "wisdom", 12, "Ecclesiastes"],
  ["Song", "wisdom", 8, "Song of Songs"],
  ["Isa", "major", 66, "Isaiah"],
  ["Jer", "major", 52, "Jeremiah"],
  ["Lam", "major", 5, "Lamentations"],
  ["Ezek", "major", 48, "Ezekiel"],
  ["Dan", "major", 12, "Daniel"],
  ["Hosea", "major", 14, "Hosea"],
  ["Joel", "minor", 3, "Joel"],
  ["Amos", "minor", 9, "Amos"],
  ["Obad", "minor", 1, "Obadiah"],
  ["Jonah", "minor", 4, "Jonah"],
  ["Micah", "minor", 7, "Micah"],
  ["Nahum", "minor", 3, "Nahum"],
  ["Hab", "minor", 3, "Habakkuk"],
  ["Zeph", "minor", 3, "Zephaniah"],
  ["Hag", "minor", 2, "Haggai"],
  ["Zech", "minor", 14, "Zechariah"],
  ["Mal", "minor", 4, "Malachi"],
  ["Matt", "gospel", 28, "Matthew"],
  ["Mark", "gospel", 16, "Mark"],
  ["Luke", "gospel", 24, "Luke"],
  ["John", "gospel", 21, "John"],
  ["Acts", "gospel", 28, "Acts"],
  ["Rom", "letters", 16, "Romans"],
  ["1 Cor", "letters", 16, "1 Corinthians"],
  ["2 Cor", "letters", 13, "2 Corinthian"],
  ["Gal", "letters", 6, "Galatians"],
  ["Eph", "letters", 6, "Ephesians"],
  ["Phil", "letters", 4, "Philippians"],
  ["Col", "letters", 4, "Colossians"],
  ["1 The", "letters", 5, "1 Thessalonians"],
  ["2 The", "letters", 3, "2 Thessalonians"],
  ["1 Tim", "letters", 6, "1 Timothy"],
  ["2 Tim", "letters", 4, "2 Timothy"],
  ["Titus", "letters", 3, "Titus"],
  ["Phmon", "letters", 1, "Philemon"],
  ["Heb", "letters", 13, "Hebrews"],
  ["James", "letters", 5, "James"],
  ["1 Pet", "letters", 5, "1 Peter"],
  ["2 Pet", "letters", 3, "2 Peter"],
  ["1 Jn", "letters", 5, "1 John"],
  ["2 Jn", "letters", 1, "2 John"],
  ["3 Jn", "letters", 1, "3 John"],
  ["Jude", "letters", 1, "Jude"],
  ["Rev", "letters", 22, "Revelation"]];
version_data = [];
chapters_shown = 1;

window.OpenLP = {
  getElement: function(event) {
    var targ;
    if (!event) {
      var event = window.event;
    }
    if (event.target) {
      targ = event.target;
    }
    else if (event.srcElement) {
      targ = event.srcElement;
    }
    if (targ.nodeType == 3) {
      // defeat Safari bug
      targ = targ.parentNode;
    }
    var isSecure = false;
    var isAuthorised = false;
    return $(targ);
  },
  getSearchablePlugins: function () {
    $.getJSON(
      "/api/plugin/search",
      function (data, status) {
        var select = $("#search-plugin");
        select.html("");
        $.each(data.results.items, function (idx, value) {
          select.append("<option value='" + value[0] + "'>" + value[1] + "</option>");
        });
        select.selectmenu("refresh");
      }
    );
  },
  loadService: function (event) {
    if (event) {
      event.preventDefault();
    }
    $.getJSON(
      "/api/service/list",
      function (data, status) {
        var ul = $("#service-manager > div[data-role=content] > ul[data-role=listview]");
        ul.html("");
        $.each(data.results.items, function (idx, value) {
          var text = value["title"];
          if (value["notes"]) {
            text += ' - ' + value["notes"];
          }
          var li = $("<li data-icon=\"false\">").append(
            $("<a href=\"#\">").attr("value", parseInt(idx, 10)).text(text));
          li.attr("uuid", value["id"])
          li.children("a").click(OpenLP.setItem);
          ul.append(li);
        });
        ul.listview("refresh");
      }
    );
  },
  loadController: function (event) {
    if (event) {
      event.preventDefault();
    }
    $.getJSON(
      "/api/controller/live/text",
      function (data, status) {
        var ul = $("#slide-controller > div[data-role=content] > ul[data-role=listview]");
        ul.html("");
        for (idx in data.results.slides) {
          var indexInt = parseInt(idx,10);
          var slide = data.results.slides[idx];
          var text = slide["tag"];
          if (text != "") {
            text = text + ": ";
          }
          if (slide["title"]) {
            text += slide["title"]
          } else {
            text += slide["text"];
          }
          if (slide["slide_notes"]) {
            text += ("<div style='font-size:smaller;font-weight:normal'>" + slide["slide_notes"] + "</div>");
          }
          text = text.replace(/\n/g, '<br />');
          if (slide["img"]) {
            text += "<img src='" + slide["img"].replace("/thumbnails/", "/thumbnails88x88/") + "'>";
          }
          var li = $("<li data-icon=\"false\">").append($("<a href=\"#\">").html(text));
          if (slide["selected"]) {
            li.attr("data-theme", "e");
          }
          li.children("a").click(OpenLP.setSlide);
          li.find("*").attr("value", indexInt );
          ul.append(li);
        }
        OpenLP.currentItem = data.results.item;
        ul.listview("refresh");
      }
    );
  },
  setItem: function (event) {
    event.preventDefault();
    var item = OpenLP.getElement(event);
    var id = item.attr("value");
    if (typeof id !== "number") {
        id = "\"" + id + "\"";
    }
    var text = "{\"request\": {\"id\": " + id + "}}";
    $.getJSON(
      "/api/service/set",
      {"data": text},
      function (data, status) {
        $.mobile.changePage("#slide-controller");
        $("#service-manager > div[data-role=content] ul[data-role=listview] li").attr("data-theme", "c").removeClass("ui-btn-up-e").addClass("ui-btn-up-c");
        while (item[0].tagName != "LI") {
          item = item.parent();
        }
        item.attr("data-theme", "e").removeClass("ui-btn-up-c").addClass("ui-btn-up-e");
        $("#service-manager > div[data-role=content] ul[data-role=listview]").listview("refresh");
      }
    );
  },
  setSlide: function (event) {
    event.preventDefault();
    var slide = OpenLP.getElement(event);
    var id = slide.attr("value");
    if (typeof id !== "number") {
        id = "\"" + id + "\"";
    }
    var text = "{\"request\": {\"id\": " + id + "}}";
    $.getJSON(
      "/api/controller/live/set",
      {"data": text},
      function (data, status) {
        $("#slide-controller div[data-role=content] ul[data-role=listview] li").attr("data-theme", "c").removeClass("ui-btn-up-e").addClass("ui-btn-up-c");
        while (slide[0].tagName != "LI") {
          slide = slide.parent();
        }
        slide.attr("data-theme", "e").removeClass("ui-btn-up-c").addClass("ui-btn-up-e");
        $("#slide-controller div[data-role=content] ul[data-role=listview]").listview("refresh");
      }
    );
  },
  pollServer: function () {
    $.getJSON(
      "/api/poll",
      function (data, status) {
        var prevItem = OpenLP.currentItem;
        OpenLP.currentSlide = data.results.slide;
        OpenLP.currentItem = data.results.item;
        OpenLP.isSecure = data.results.isSecure;
        OpenLP.isAuthorised = data.results.isAuthorised;
        if ($("#service-manager").is(":visible")) {
          if (OpenLP.currentService != data.results.service) {
            OpenLP.currentService = data.results.service;
            OpenLP.loadService();
          }
          $("#service-manager div[data-role=content] ul[data-role=listview] li").attr("data-theme", "c").removeClass("ui-btn-up-e").addClass("ui-btn-up-c");
          $("#service-manager div[data-role=content] ul[data-role=listview] li a").each(function () {
            var item = $(this);
            while (item[0].tagName != "LI") {
              item = item.parent();
            }
            if (item.attr("uuid") == OpenLP.currentItem) {
              item.attr("data-theme", "e").removeClass("ui-btn-up-c").addClass("ui-btn-up-e");
              return false;
            }
          });
          $("#service-manager div[data-role=content] ul[data-role=listview]").listview("refresh");
        }
        if ($("#slide-controller").is(":visible")) {
          if (prevItem != OpenLP.currentItem) {
            OpenLP.loadController();
            return;
          }
          var idx = 0;
          $("#slide-controller div[data-role=content] ul[data-role=listview] li").attr("data-theme", "c").removeClass("ui-btn-up-e").addClass("ui-btn-up-c");
          $("#slide-controller div[data-role=content] ul[data-role=listview] li a").each(function () {
            var item = $(this);
            if (idx == OpenLP.currentSlide) {
              while (item[0].tagName != "LI") {
                item = item.parent();
              }
              item.attr("data-theme", "e").removeClass("ui-btn-up-c").addClass("ui-btn-up-e");
              return false;
            }
            idx++;
          });
          $("#slide-controller div[data-role=content] ul[data-role=listview]").listview("refresh");
        }
      }
    );
  },
  nextItem: function (event) {
    event.preventDefault();
    $.getJSON("/api/service/next");
  },
  previousItem: function (event) {
    event.preventDefault();
    $.getJSON("/api/service/previous");
  },
  nextSlide: function (event) {
    event.preventDefault();
    $.getJSON("/api/controller/live/next");
  },
  previousSlide: function (event) {
    event.preventDefault();
    $.getJSON("/api/controller/live/previous");
  },
  blankDisplay: function (event) {
    event.preventDefault();
    $.getJSON("/api/display/blank");
  },
  themeDisplay: function (event) {
    event.preventDefault();
    $.getJSON("/api/display/theme");
  },
  desktopDisplay: function (event) {
    event.preventDefault();
    $.getJSON("/api/display/desktop");
  },
  showDisplay: function (event) {
    event.preventDefault();
    $.getJSON("/api/display/show");
  },
  showAlert: function (event) {
    event.preventDefault();
    var alert = OpenLP.escapeString($("#alert-text").val())
    var text = "{\"request\": {\"text\": \"" + alert + "\"}}";
    $.getJSON(
      "/api/alert",
      {"data": text},
      function () {
        $("#alert-text").val("");
      }
    );
  },
  search: function (event) {
    event.preventDefault();
    var query = OpenLP.escapeString($("#search-text").val())
    var text = "{\"request\": {\"text\": \"" + query + "\"}}";
    $.getJSON(
      "/api/" + $("#search-plugin").val() + "/search",
      {"data": text},
      function (data, status) {
        var ul = $("#search > div[data-role=content] > ul[data-role=listview]");
        ul.html("");
        if (data.results.items.length == 0) {
          var li = $("<li data-icon=\"false\">").text(translationStrings["no_results"]);
          ul.append(li);
        }
        else {
            $.each(data.results.items, function (idx, value) {
              if (typeof value[0] !== "number"){
                value[0] = OpenLP.escapeString(value[0])
              }
              ul.append($("<li>").append($("<a>").attr("href", "#options")
                  .attr("data-rel", "dialog").attr("value", value[0])
                  .click(OpenLP.showOptions).text(value[1])));
            });
        }
        ul.listview("refresh");
      }
    );
  },
  showOptions: function (event) {
    event.preventDefault();
    var element = OpenLP.getElement(event);
    $("#selected-item").val(element.attr("value"));
  },
  goLive: function (event) {
    event.preventDefault();
    var id = $("#selected-item").val();
    if (typeof id !== "number") {
      id = "\"" + id + "\"";
    }
    var text = "{\"request\": {\"id\": " + id + "}}";
    $.getJSON(
      "/api/" + $("#search-plugin").val() + "/live",
      {"data": text}
    );
    $.mobile.changePage("#slide-controller");
  },
  addToService: function (event) {
    event.preventDefault();
    var id = $("#selected-item").val();
    if (typeof id !== "number") {
        id = "\"" + id + "\"";
    }
    var text = "{\"request\": {\"id\": " + id + "}}";
    $.getJSON(
      "/api/" + $("#search-plugin").val() + "/add",
      {"data": text},
      function () {
        $("#options").dialog("close");
      }
    );
  },
  addAndGoToService: function (event) {
    event.preventDefault();
    var id = $("#selected-item").val();
    if (typeof id !== "number") {
        id = "\"" + id + "\"";
    }
    var text = "{\"request\": {\"id\": " + id + "}}";
    $.getJSON(
      "/api/" + $("#search-plugin").val() + "/add",
      {"data": text},
      function () {
        //$("#options").dialog("close");
        $.mobile.changePage("#service-manager");
      }
    );
  },
  addChapterToService: function (event) {
    event.preventDefault();
    var id = $("#complete-ref").val();
    if (typeof id !== "number") {
        id = "\"" + id + "\"";
    }
    var text = "{\"request\": {\"id\": " + id + "}}";
    $.getJSON(
      "/api/bibles/add",
      {"data": text}
    );
  },
  addChapterAndGoToService: function (event) {
    event.preventDefault();
    var id = $("#complete-ref").val();
    if (typeof id !== "number") {
        id = "\"" + id + "\"";
    }
    var text = "{\"request\": {\"id\": " + id + "}}";
    $.getJSON(
      "/api/bibles/add",
      {"data": text},
      function () {
        $.mobile.changePage("#service-manager");
      }
    );
  },
  escapeString: function (string) {
    return string.replace(/\\/g, "\\\\").replace(/"/g, "\\\"")
  },
  setupBooks: function() {
    for (var i=0; i<book_data.length; i++){
      book = book_data[i];
      $("#book-grid").append('<div class="book ' + book[1] + ' ui-block-e"><input data-chap="' + book[2] + '" type="radio" name="book-radio" id="book-' + i + '" value="' + book[3] + '" /><label for="book-' + i + '">' + book[0] + '</label></div>').trigger('create');
    }
    $("#book-0").prop("checked", true).checkboxradio("refresh");
    book_chosen = $("#book-0").val();
  },
  setupVersions: function(){
    $.getJSON(
      "/api/bible_versions",
      function (data, status) {
        version_data = data.results
        for (var i=0; i<version_data.length; i++){
          $("#version-grid").append('<div class="version ui-block-e"><input type="radio" name="version-radio" id="version-' + i + '" value="' + version_data[i] + '" /><label for="version-' + i + '">' + version_data[i] + '</label></div>').trigger('create');
        }
        $("#version-0").prop("checked", true).checkboxradio("refresh");
        version_chosen = $("#version-0").val();

        $("#version-chooser label").on("click", function() {
          version_chosen = $(this).prev().val();
          OpenLP.updateRef();
        });
      }
    );
  },
  setupChapters: function () {
    for(var i=0; i<30; i++){
      $("#chapter-grid").append('<div class="chapter ui-block-e"><input type="radio" name="chap-radio" id="chap-' + (5*i+1) + '" value="' + (5*i + 1) + '" /><label for="chap-' + (5*i + 1)+ '">' + (5*i+1) + '</label></div>').trigger('create');
      $("#chapter-grid").append('<div class="chapter ui-block-e"><input type="radio" name="chap-radio" id="chap-' + (5*i+2) + '" value="' + (5*i + 2) + '" /><label for="chap-' + (5*i + 2)+ '">' + (5*i+2) + '</label></div>').trigger('create');
      $("#chapter-grid").append('<div class="chapter ui-block-e"><input type="radio" name="chap-radio" id="chap-' + (5*i+3) + '" value="' + (5*i + 3) + '" /><label for="chap-' + (5*i + 3)+ '">' + (5*i+3) + '</label></div>').trigger('create');
      $("#chapter-grid").append('<div class="chapter ui-block-e"><input type="radio" name="chap-radio" id="chap-' + (5*i+4) + '" value="' + (5*i + 4) + '" /><label for="chap-' + (5*i + 4)+ '">' + (5*i+4) + '</label></div>').trigger('create');
      $("#chapter-grid").append('<div class="chapter ui-block-e"><input type="radio" name="chap-radio" id="chap-' + (5*i+5) + '" value="' + (5*i + 5) + '" /><label for="chap-' + (5*i + 5)+ '">' + (5*i+5) + '</label></div>').trigger('create');
    }
    $("#chapter-grid div").hide();
    for(var i=0; i<book_data[0][2]; i++){
      $("#chapter-grid div:nth-child(" + (i+1) + ")").show();
    }
    $("#chap-1").prop("checked", true).checkboxradio("refresh");
    chapters_shown = parseInt($("#book-0").data("chap"));
    chapter_chosen = 1;
  },
  updateRef: function() {
    $("#complete-ref").val(book_chosen + " " + chapter_chosen + " (" + version_chosen + ")");
  }
}
// Initial jQueryMobile options
$(document).bind("mobileinit", function(){
  $.mobile.defaultDialogTransition = "none";
  $.mobile.defaultPageTransition = "none";
});
// Service Manager
$("#service-manager").live("pagebeforeshow", OpenLP.loadService);
$("#service-refresh").live("click", OpenLP.loadService);
$("#service-next").live("click", OpenLP.nextItem);
$("#service-previous").live("click", OpenLP.previousItem);
$("#service-blank").live("click", OpenLP.blankDisplay);
$("#service-theme").live("click", OpenLP.themeDisplay);
$("#service-desktop").live("click", OpenLP.desktopDisplay);
$("#service-show").live("click", OpenLP.showDisplay);
// Slide Controller
$("#slide-controller").live("pagebeforeshow", OpenLP.loadController);
$("#controller-refresh").live("click", OpenLP.loadController);
$("#controller-next").live("click", OpenLP.nextSlide);
$("#controller-previous").live("click", OpenLP.previousSlide);
$("#controller-blank").live("click", OpenLP.blankDisplay);
$("#controller-theme").live("click", OpenLP.themeDisplay);
$("#controller-desktop").live("click", OpenLP.desktopDisplay);
$("#controller-show").live("click", OpenLP.showDisplay);
// Alerts
$("#alert-submit").live("click", OpenLP.showAlert);
// Search
$("#search-submit").live("click", OpenLP.search);
$("#search-text").live("keypress", function(event) {
    if (event.which == 13)
    {
        OpenLP.search(event);
    }
});
$("#go-live").live("click", OpenLP.goLive);
$("#add-to-service").live("click", OpenLP.addToService);
$("#add-and-go-to-service").live("click", OpenLP.addAndGoToService);
// Bible Chapter search
$("#add-chapter-to-service").live("click", OpenLP.addChapterToService);
$("#add-chapter-and-go-to-service").live("click", OpenLP.addChapterAndGoToService);
// Poll the server twice a second to get any updates.
$.ajaxSetup({cache: false});
$("#search").live("pageinit", function (event) {
  OpenLP.getSearchablePlugins();
});

$(document).ready(function(){
  version_chosen = ""
  OpenLP.setupBooks();
  OpenLP.setupChapters();
  OpenLP.setupVersions();

  $("#book-chooser label").on("click", function() {
    chapters = parseInt($(this).prev().data("chap"));
    book_chosen = $(this).prev().val();
    if (chapters > chapters_shown){
      for(var i=chapters_shown; i<chapters; i++){
        $("#chapter-grid div:nth-child(" + (i+1) + ")").show();
      }
    }
    else if (chapters < chapters_shown){
      for(var i=chapters; i<chapters_shown; i++){
        $("#chapter-grid div:nth-child(" + (i+1) + ")").hide();
      }
    }
    chapters_shown = chapters;
    chapter_chosen = 1;
    $("#chapter-grid input").prop("checked", false).checkboxradio("refresh");
    $("#chap-1").prop("checked", true).checkboxradio("refresh");
    $("#book-chooser").trigger('collapse');
    $("#chapter-chooser").trigger('expand');
    OpenLP.updateRef();
  });

  $("#chapter-chooser label").on("click", function() {
    chapter_chosen = $(this).prev().val();
    OpenLP.updateRef();
    $("#book-chooser").trigger('collapse');
    $("#chapter-chooser").trigger('collapse');
    $("#version-chooser").trigger('expand');
  });

  $("#book-chooser").trigger('collapse');
  $("#chapter-chooser").trigger('collapse');
  $("#version-chooser").trigger('collapse');
});

setInterval("OpenLP.pollServer();", 500);
OpenLP.pollServer();
