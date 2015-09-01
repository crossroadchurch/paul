# paul
A fork of OpenLP church projection software

## changelog
* Added a mandatory slide break tool for editing songs - either put [br] tag into song lyrics manually or use UI button to insert at current cursor position

* Changed data directory to openlp-paul so that Paul can run alongside OpenLP 2.0

* Songs now have a key and transpose amount, which the user can edit.

* Song key, transpose amount supported for import from and export to OpenLyrics format (openlyrics.info for full XML description), as well as import from OpenLP format (.sqlite database)

* Chords can now be added to songs.  Chord lines must be added on the line immediately preceding the corresponding lyrics and must end with a @.  The # symbol can be used to pad lyric lines so that they fit the chords.  Chords are stored in a separate database field to the lyrics to avoid interfering with other OpenLP functionality.  If chords are used in a song then the key must also be specified to allow the song to save.

## limitations
* The song lyric editor currently only allows you to edit the entire song, rather than being able to add/edit/delete individual verses.

* Chords are currently not exported to or imported from the OpenLyrics format.
