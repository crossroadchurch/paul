# paul
A fork of OpenLP church projection software

## changelog
*11 Aug 2015*
* Added a mandatory slide break tool for editing songs - either put [br] tag into song lyrics manually or use UI button to insert at current cursor position

*22 Aug 2015*
* Changed data directory to openlp-paul so that Paul can run alongside OpenLP 2.0
* Songs now have a key and transpose amount, which the user can edit.
* Song key, transpose amount supported for import from and export to OpenLyrics format (openlyrics.info for full XML description), as well as import from OpenLP format (.sqlite database)

*01 Sept 2015*
* Chords can now be added to songs.  Chord lines must be added on the line immediately preceding the corresponding lyrics and must end with a @.  The # symbol can be used to pad lyric lines so that they fit the chords.  Chords are stored in a separate database field to the lyrics to avoid interfering with other OpenLP functionality.  If chords are used in a song then the key must also be specified to allow the song to save.  Edit song dialog only supports Edit All sections.

*04 Sept 2015*
* Songs with chords can now be exported to and imported from the OpenLyrics format.
* Edit song dialog now supports Add/Edit/Delete sections again.
* Minor changes to chord sanitization routine.

*13 Sept 2015*
* New route added to httprouter (Remote plugin): /api/controller/live_chords.  This returns the chords for the current song (inline with the lyrics), with slide breaks in the same places as in the regular projector output.

*30 Sept 2015*
* Bug fix - Opening a service plan no longer crashes OpenLP.
* Bug fix - Editing a template no longer crashes OpenLP.
* Disabled OpenLP version checking thread.

*19 Oct 2015*
* /api/controller/live_chords now returns the transposed chords for the current song, if a transpose amount has been selected for the song.

*10 Nov 2015*
* In the Theme Wizard, the user can now choose between three different ways of specifying the song area dimensions (Classic, Margins, Proportional).

*08 Jan 2016*
* Removed /api/controller/live_chords route.
* Added /silas/{update_id} route.  Returns musician oriented view of the live controller.  Slide data includes (transposed) chords, where used.  The song_order indicates current position with parentheses e.g. V1 (C1) V2.  Possible JSON-encoded dicts are:
  * {"status": "inactive"} - if live controller not active, else:
  * {"status": "current"} - no updates have occurred, based on value of {update_id}, else:
  * {"status": "update", "update_id": new update_id, "current_slide": "...", "next_slide": "...", "song_order": "..."}

*17 Jan 2016*
* Update musician oriented view.  Route is now /silas/update={update_id}&capo={capo}, both arguments optional.  The status=update JSON has an additional field, played_key, indicating the key that the musician will be playing e.g. "E" or "Capo 2 (D)".
* Compacted the song order returned by /silas/

*30 Jan 2016*
* Added /music route to return a stage view with chords.  The capo can be changed from this page.

*19 Feb 2016*
* Added looped videos (played using VLC) and associated Loop manager component.

*10 Sept 2016*
* Bug fix: chords render correctly for services that have been loaded in from a save file.
* Bug fix: multiple identical lines rendered on Musician View.
* CSS and JS fixes to improve rendering of Musician View.
* Loop manager can be hidden and shown.

*08 Oct 2016*
* Base font size of Musician view can be changed by adding the size parameter to the music route: /music?size=n

*29 Nov 2016*
* Bug fix: songs with optional slide breaks can now be added to service plan without crashing OpenLP.

*Known issues*
* If a song is live whilst a theme is edited then when that song is redisplayed OpenLP will hang.  Current workaround:  Display a different song before returning to the initial song.
