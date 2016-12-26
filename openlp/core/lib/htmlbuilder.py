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
This module is responsible for generating the HTML for :class:`~openlp.core.ui.maindisplay`. The ``build_html`` function
is the function which has to be called from outside. The generated and returned HTML will look similar to this::

        <!DOCTYPE html>
        <html>
        <head>
        <title>OpenLP Display</title>
        <style>
        *{
            margin: 0;
            padding: 0;
            border: 0;
            overflow: hidden;
            -webkit-user-select: none;
        }
        body {
            background-color: #000000;
        }
        .size {
            position: absolute;
            left: 0px;
            top: 0px;
            width: 100%;
            height: 100%;
        }
        #black {
            z-index: 8;
            background-color: black;
            display: none;
        }
        #bgimage {
            z-index: 1;
        }
        #image {
            z-index: 2;
        }

        #videobackboard {
            z-index:3;
            background-color: #000000;
        }
        #video {
            background-color: #000000;
            z-index:4;
        }

        #flash {
            z-index:5;
        }

            #alert {
                position: absolute;
                left: 0px;
                top: 0px;
                z-index: 10;
                width: 100%;
                vertical-align: bottom;
                font-family: DejaVu Sans;
                font-size: 40pt;
                color: #ffffff;
                background-color: #660000;
                word-wrap: break-word;
            }

        #footerarea {
            display: none;
            position: absolute;
            z-index: 6;

            left: 10px;
            bottom: 0px;
            width: 1580px;
            font-family: Nimbus Sans L;
            font-size: 12pt;
            color: #FFFFFF;
            text-align: left;
            white-space: nowrap;
        }

        #verseorder ul {
          list-style-type: none;
          padding: 0;
          font-size: 1.5rem;
        }

        #verseorder ul li {
          display: inline;
          padding: 0px 5px;
        }

        .current-verse {
          background-color: green;
        }

        /* lyric css */

        .lyricstable {
            z-index: 5;
            position: absolute;
            display: table;
            left: 10px; top: 0px;
        }
        .lyricscell {
            display: table-cell;
            word-wrap: break-word;
            -webkit-transition: opacity 0.4s ease;
            white-space:pre-wrap; word-wrap: break-word; text-align: left; vertical-align: top; font-family: Nimbus
            Sans L; font-size: 40pt; color: #FFFFFF; line-height: 100%; margin: 0;padding: 0; padding-bottom: 0;
            padding-left: 4px; width: 1580px; height: 810px;
        }
        .lyricsmain {
             -webkit-text-stroke: 0.125em #000000; -webkit-text-fill-color: #FFFFFF;  text-shadow: #000000 5px 5px;
        }

        sup {
            font-size: 0.6em;
            vertical-align: top;
            position: relative;
            top: -0.3em;
        }
        </style>
        <script>
            var timer = null;
            var transition = false;

            function show_video(state, path, volume, loop, variable_value){
                // Sometimes  video.currentTime stops slightly short of video.duration and video.ended is intermittent!

                var video = document.getElementById('video');
                if(volume != null){
                    video.volume = volume;
                }
                switch(state){
                    case 'load':
                        video.src = 'file:///' + path;
                        if(loop == true) {
                            video.loop = true;
                        }
                        video.load();
                        break;
                    case 'play':
                        video.play();
                        break;
                    case 'pause':
                        video.pause();
                        break;
                    case 'stop':
                        show_video('pause');
                        video.currentTime = 0;
                        break;
                    case 'close':
                        show_video('stop');
                        video.src = '';
                        break;
                    case 'length':
                        return video.duration;
                    case 'current_time':
                        return video.currentTime;
                    case 'seek':
                        video.currentTime = variable_value;
                        break;
                    case 'isEnded':
                        return video.ended;
                    case 'setVisible':
                        video.style.visibility = variable_value;
                        break;
                    case 'setBackBoard':
                        var back = document.getElementById('videobackboard');
                        back.style.visibility = variable_value;
                        break;
               }
            }

            function getFlashMovieObject(movieName)
            {
                if (window.document[movieName]){
                    return window.document[movieName];
                }
                if (document.embeds && document.embeds[movieName]){
                    return document.embeds[movieName];
                }
            }

            function show_flash(state, path, volume, variable_value){
                var text = document.getElementById('flash');
                var flashMovie = getFlashMovieObject("OpenLPFlashMovie");
                var src = "src = 'file:///" + path + "'";
                var view_parm = " wmode='opaque'" + " width='100%%'" + " height='100%%'";
                var swf_parm = " name='OpenLPFlashMovie'" + " autostart='true' loop='false' play='true'" +
                    " hidden='false' swliveconnect='true' allowscriptaccess='always'" + " volume='" + volume + "'";

                switch(state){
                    case 'load':
                        text.innerHTML = "<embed " + src + view_parm + swf_parm + "/>";
                        flashMovie = getFlashMovieObject("OpenLPFlashMovie");
                        flashMovie.Play();
                        break;
                    case 'play':
                        flashMovie.Play();
                        break;
                    case 'pause':
                        flashMovie.StopPlay();
                        break;
                    case 'stop':
                        flashMovie.StopPlay();
                        tempHtml = text.innerHTML;
                        text.innerHTML = '';
                        text.innerHTML = tempHtml;
                        break;
                    case 'close':
                        flashMovie.StopPlay();
                        text.innerHTML = '';
                        break;
                    case 'length':
                        return flashMovie.TotalFrames();
                    case 'current_time':
                        return flashMovie.CurrentFrame();
                    case 'seek':
        //                flashMovie.GotoFrame(variable_value);
                        break;
                    case 'isEnded':
                        //TODO check flash end
                        return false;
                    case 'setVisible':
                        text.style.visibility = variable_value;
                        break;
                }
            }

            function show_alert(alerttext, position){
                var text = document.getElementById('alert');
                text.innerHTML = alerttext;
                if(alerttext == '') {
                    text.style.visibility = 'hidden';
                    return 0;
                }
                if(position == ''){
                    position = getComputedStyle(text, '').verticalAlign;
                }
                switch(position)
                {
                    case 'top':
                        text.style.top = '0px';
                        break;
                    case 'middle':
                        text.style.top = ((window.innerHeight - text.clientHeight) / 2)
                            + 'px';
                        break;
                    case 'bottom':
                        text.style.top = (window.innerHeight - text.clientHeight)
                            + 'px';
                        break;
                }
                text.style.visibility = 'visible';
                return text.clientHeight;
            }

            function update_css(align, font, size, color, bgcolor){
                var text = document.getElementById('alert');
                text.style.fontSize = size + "pt";
                text.style.fontFamily = font;
                text.style.color = color;
                text.style.backgroundColor = bgcolor;
                switch(align)
                {
                    case 'top':
                        text.style.top = '0px';
                        break;
                    case 'middle':
                        text.style.top = ((window.innerHeight - text.clientHeight) / 2)
                            + 'px';
                        break;
                    case 'bottom':
                        text.style.top = (window.innerHeight - text.clientHeight)
                            + 'px';
                        break;
                }
            }


            function show_image(src){
                var img = document.getElementById('image');
                img.src = src;
                if(src == '')
                    img.style.display = 'none';
                else
                    img.style.display = 'block';
            }

            function show_blank(state){
                var black = 'none';
                var lyrics = '';
                switch(state){
                    case 'theme':
                        lyrics = 'hidden';
                        break;
                    case 'black':
                        black = 'block';
                        break;
                    case 'desktop':
                        break;
                }
                document.getElementById('black').style.display = black;
                document.getElementById('lyricsmain').style.visibility = lyrics;
                document.getElementById('image').style.visibility = lyrics;
                document.getElementById('footer').style.visibility = lyrics;
            }

            function show_footer(footertext){
                document.getElementById('footer').innerHTML = footertext;
            }

            function show_verseorder(text){
                document.getElementById('verseorder').innerHTML = text;
            }

            function show_text(new_text){
                var match = /-webkit-text-fill-color:[^;"]+/gi;
                if(timer != null)
                    clearTimeout(timer);
                /*
                QtWebkit bug with outlines and justify causing outline alignment
                problems. (Bug 859950) Surround each word with a <span> to workaround,
                but only in this scenario.
                */
                var txt = document.getElementById('lyricsmain');
                if(window.getComputedStyle(txt).textAlign == 'justify'){
                    if(window.getComputedStyle(txt).webkitTextStrokeWidth != '0px'){
                        new_text = new_text.replace(/(\s|&nbsp;)+(?![^<]*>)/g,
                            function(match) {
                                return '</span>' + match + '<span>';
                            });
                        new_text = '<span>' + new_text + '</span>';
                    }
                }
                text_fade('lyricsmain', new_text);
            }

            function text_fade(id, new_text){
                /*
                Show the text.
                */
                var text = document.getElementById(id);
                if(text == null) return;
                if(!transition){
                    text.innerHTML = new_text;
                    return;
                }
                // Fade text out. 0.1 to minimize the time "nothing" is shown on the screen.
                text.style.opacity = '0.1';
                // Fade new text in after the old text has finished fading out.
                timer = window.setTimeout(function(){_show_text(text, new_text)}, 400);
            }

            function _show_text(text, new_text) {
                /*
                Helper function to show the new_text delayed.
                */
                text.innerHTML = new_text;
                text.style.opacity = '1';
                // Wait until the text is completely visible. We want to save the timer id, to be able to call
                // clearTimeout(timer) when the text has changed before finishing fading.
                timer = window.setTimeout(function(){timer = null;}, 400);
            }

            function show_text_completed(){
                return (timer == null);
            }
        </script>
        </head>
        <body>
        <img id="bgimage" class="size" style="display:none;" />
        <img id="image" class="size" style="display:none;" />

        <div id="videobackboard" class="size" style="visibility:hidden"></div>
        <video id="video" class="size" style="visibility:hidden" autobuffer preload></video>

        <div id="flash" class="size" style="visibility:hidden"></div>

            <div id="alert" style="visibility:hidden"></div>

        <div class="lyricstable"><div id="lyricsmain" style="opacity:1" class="lyricscell lyricsmain"></div></div>
        <div id="footerarea">
            <div id="footer" class="footer"></div>
            <div id="verseorder"></div>
        </div>
        <div id="black" class="size"></div>
        </body>
        </html>
"""
import logging

from PyQt4 import QtWebKit

from openlp.core.common import Settings
from openlp.core.lib.theme import BackgroundType, BackgroundGradientType, VerticalType, HorizontalType

log = logging.getLogger(__name__)

HTMLSRC = """
<!DOCTYPE html>
<html>
<head>
<title>OpenLP Display</title>
<style>
*{
    margin: 0;
    padding: 0;
    border: 0;
    overflow: hidden;
    -webkit-user-select: none;
}
body {
    %s;
}
.size {
    position: absolute;
    left: 0px;
    top: 0px;
    width: 100%%;
    height: 100%%;
}
#black {
    z-index: 8;
    background-color: black;
    display: none;
}
#bgimage {
    z-index: 1;
}
#image {
    z-index: 2;
}
%s
#footerarea {
    position: absolute;
    z-index: 6;
    %s
}
#verseorder ul {
  list-style-type: none;
  padding: 0;
  /*font-size: 1.5rem;*/
  font-size: 150%%;
}

#verseorder ul li {
  display: inline;
  padding: 5px 5px;
  font-weight: bold;
}

.current-verse {
  background-color: green;
}
/* lyric css */
%s
sup {
    font-size: 0.6em;
    vertical-align: top;
    position: relative;
    top: -0.3em;
}
</style>
<script>
    var timer = null;
    var transition = %s;
    %s

    function show_image(src){
        var img = document.getElementById('image');
        img.src = src;
        if(src == '')
            img.style.display = 'none';
        else
            img.style.display = 'block';
    }

    function show_blank(state){
        var black = 'none';
        var lyrics = '';
        switch(state){
            case 'theme':
                lyrics = 'hidden';
                break;
            case 'black':
                black = 'block';
                break;
            case 'desktop':
                break;
        }
        document.getElementById('black').style.display = black;
        document.getElementById('lyricsmain').style.visibility = lyrics;
        document.getElementById('image').style.visibility = lyrics;
        document.getElementById('footer').style.visibility = lyrics;
    }

    function show_footer(footertext){
        document.getElementById('footer').innerHTML = footertext;
    }

    function show_verseorder(text){
      document.getElementById('verseorder').innerHTML = text;
    }

    function show_text(new_text){
        var match = /-webkit-text-fill-color:[^;\"]+/gi;
        if(timer != null)
            clearTimeout(timer);
        /*
        QtWebkit bug with outlines and justify causing outline alignment
        problems. (Bug 859950) Surround each word with a <span> to workaround,
        but only in this scenario.
        */
        var txt = document.getElementById('lyricsmain');
        if(window.getComputedStyle(txt).textAlign == 'justify'){
            if(window.getComputedStyle(txt).webkitTextStrokeWidth != '0px'){
                new_text = new_text.replace(/(\s|&nbsp;)+(?![^<]*>)/g,
                    function(match) {
                        return '</span>' + match + '<span>';
                    });
                new_text = '<span>' + new_text + '</span>';
            }
        }
        text_fade('lyricsmain', new_text);
    }

    function text_fade(id, new_text){
        /*
        Show the text.
        */
        var text = document.getElementById(id);
        if(text == null) return;
        if(!transition){
            text.innerHTML = new_text;
            return;
        }
        // Fade text out. 0.1 to minimize the time "nothing" is shown on the screen.
        text.style.opacity = '0.1';
        // Fade new text in after the old text has finished fading out.
        timer = window.setTimeout(function(){_show_text(text, new_text)}, 400);
    }

    function _show_text(text, new_text) {
        /*
        Helper function to show the new_text delayed.
        */
        text.innerHTML = new_text;
        text.style.opacity = '1';
        // Wait until the text is completely visible. We want to save the timer id, to be able to call
        // clearTimeout(timer) when the text has changed before finishing fading.
        timer = window.setTimeout(function(){timer = null;}, 400);
    }

    function show_text_completed(){
        return (timer == null);
    }
</script>
</head>
<body>
<img id="bgimage" class="size" %s />
<img id="image" class="size" %s />
%s
<div class="lyricstable"><div id="lyricsmain" style="opacity:1" class="lyricscell lyricsmain"></div></div>
<div id="footerarea">
  <div id="footer" class="footer"></div>
  <div id="verseorder"></div>
</div>
<div id="black" class="size"></div>
</body>
</html>
"""


def build_html(item, screen, is_live, background, image=None, plugins=None):
    """
    Build the full web paged structure for display

    :param item: Service Item to be displayed
    :param screen: Current display information
    :param is_live: Item is going live, rather than preview/theme building
    :param background:  Theme background image - bytes
    :param image: Image media item - bytes
    :param plugins: The List of available plugins
    """
    width = screen['size'].width()
    height = screen['size'].height()
    theme_data = item.theme_data
    # Image generated and poked in
    if background:
        bgimage_src = 'src="data:image/png;base64,%s"' % background
    elif item.bg_image_bytes:
        bgimage_src = 'src="data:image/png;base64,%s"' % item.bg_image_bytes
    else:
        bgimage_src = 'style="display:none;"'
    if image:
        image_src = 'src="data:image/png;base64,%s"' % image
    else:
        image_src = 'style="display:none;"'
    css_additions = ''
    js_additions = ''
    html_additions = ''
    if plugins:
        for plugin in plugins:
            css_additions += plugin.get_display_css()
            js_additions += plugin.get_display_javascript()
            html_additions += plugin.get_display_html()
    html = HTMLSRC % (
        build_background_css(item, width),
        css_additions,
        build_footer_css(item, height),
        build_lyrics_css(item),
        'true' if theme_data and theme_data.display_slide_transition and is_live else 'false',
        js_additions,
        bgimage_src,
        image_src,
        html_additions
    )
    return html


def webkit_version():
    """
    Return the Webkit version in use. Note method added relatively recently, so return 0 if prior to this
    """
    try:
        webkit_ver = float(QtWebKit.qWebKitVersion())
        log.debug('Webkit version = %s' % webkit_ver)
    except AttributeError:
        webkit_ver = 0
    return webkit_ver


def build_background_css(item, width):
    """
    Build the background css

    :param item: Service Item containing theme and location information
    :param width:
    """
    width = int(width) // 2
    theme = item.theme_data
    background = 'background-color: black'
    if theme:
        if theme.background_type == BackgroundType.to_string(BackgroundType.Transparent):
            background = ''
        elif theme.background_type == BackgroundType.to_string(BackgroundType.Solid):
            background = 'background-color: %s' % theme.background_color
        else:
            if theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.Horizontal):
                background = 'background: -webkit-gradient(linear, left top, left bottom, from(%s), to(%s)) fixed' \
                    % (theme.background_start_color, theme.background_end_color)
            elif theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.LeftTop):
                background = 'background: -webkit-gradient(linear, left top, right bottom, from(%s), to(%s)) fixed' \
                    % (theme.background_start_color, theme.background_end_color)
            elif theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.LeftBottom):
                background = 'background: -webkit-gradient(linear, left bottom, right top, from(%s), to(%s)) fixed' \
                    % (theme.background_start_color, theme.background_end_color)
            elif theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.Vertical):
                background = 'background: -webkit-gradient(linear, left top, right top, from(%s), to(%s)) fixed' % \
                    (theme.background_start_color, theme.background_end_color)
            else:
                background = 'background: -webkit-gradient(radial, %s 50%%, 100, %s 50%%, %s, from(%s), to(%s)) fixed'\
                    % (width, width, width, theme.background_start_color, theme.background_end_color)
    return background


def build_lyrics_css(item):
    """
    Build the lyrics display css

    :param item: Service Item containing theme and location information
    """
    style = """
.lyricstable {
    z-index: 5;
    position: absolute;
    display: table;
    %s
}
.lyricscell {
    display: table-cell;
    word-wrap: break-word;
    -webkit-transition: opacity 0.4s ease;
    %s
}
.lyricsmain {
    %s
}
"""
    theme_data = item.theme_data
    lyricstable = ''
    lyrics = ''
    lyricsmain = ''
    if theme_data and item.main:
        lyricstable = 'left: %spx; top: %spx;' % (item.main.x(), item.main.y())
        lyrics = build_lyrics_format_css(theme_data, item.main.width(), item.main.height())
        lyricsmain += build_lyrics_outline_css(theme_data)
        if theme_data.font_main_shadow:
            lyricsmain += ' text-shadow: %s %spx %spx;' % \
                (theme_data.font_main_shadow_color, theme_data.font_main_shadow_size, theme_data.font_main_shadow_size)
    lyrics_css = style % (lyricstable, lyrics, lyricsmain)
    return lyrics_css


def build_lyrics_outline_css(theme_data):
    """
    Build the css which controls the theme outline. Also used by renderer for splitting verses

    :param theme_data: Object containing theme information
    """
    if theme_data.font_main_outline:
        size = float(theme_data.font_main_outline_size) / 16
        fill_color = theme_data.font_main_color
        outline_color = theme_data.font_main_outline_color
        return ' -webkit-text-stroke: %sem %s; -webkit-text-fill-color: %s; ' % (size, outline_color, fill_color)
    return ''


def build_lyrics_format_css(theme_data, width, height):
    """
    Build the css which controls the theme format. Also used by renderer for splitting verses

    :param theme_data: Object containing theme information
    :param width: Width of the lyrics block
    :param height: Height of the lyrics block
    """
    align = HorizontalType.Names[theme_data.display_horizontal_align]
    valign = VerticalType.Names[theme_data.display_vertical_align]
    if theme_data.font_main_outline:
        left_margin = int(theme_data.font_main_outline_size) * 2
    else:
        left_margin = 0
    justify = 'white-space:pre-wrap;'
    # fix tag incompatibilities
    if theme_data.display_horizontal_align == HorizontalType.Justify:
        justify = ''
    if theme_data.display_vertical_align == VerticalType.Bottom:
        padding_bottom = '0.5em'
    else:
        padding_bottom = '0'
    lyrics = '%s word-wrap: break-word; ' \
             'text-align: %s; vertical-align: %s; font-family: %s; ' \
             'font-size: %spt; color: %s; line-height: %d%%; margin: 0;' \
             'padding: 0; padding-bottom: %s; padding-left: %spx; width: %spx; height: %spx; ' % \
        (justify, align, valign, theme_data.font_main_name, theme_data.font_main_size,
         theme_data.font_main_color, 100 + int(theme_data.font_main_line_adjustment), padding_bottom,
         left_margin, width, height)
    if theme_data.font_main_italics:
        lyrics += 'font-style:italic; '
    if theme_data.font_main_bold:
        lyrics += 'font-weight:bold; '
    return lyrics


def build_footer_css(item, height):
    """
    Build the display of the item footer

    :param item: Service Item to be processed.
    :param height:
    """
    style = """
    left: %spx;
    bottom: %spx;
    width: %spx;
    font-family: %s;
    font-size: %spt;
    color: %s;
    text-align: left;
    white-space: %s;
    """
    theme = item.theme_data
    if not theme or not item.footer:
        return ''
    bottom = height - int(item.footer.y()) - int(item.footer.height())
    whitespace = 'normal' if Settings().value('themes/wrap footer') else 'nowrap'
    lyrics_html = style % (item.footer.x(), bottom, item.footer.width(),
                           theme.font_footer_name, theme.font_footer_size, theme.font_footer_color, whitespace)
    return lyrics_html
