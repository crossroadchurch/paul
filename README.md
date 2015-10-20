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