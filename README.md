# paul
A fork of OpenLP church projection software

## changelog
* Added a mandatory slide break tool for editing songs - either put [br] tag into song lyrics manually or use UI button to insert at current cursor position

* Changed data directory to openlp-paul so that Paul can run alongside OpenLP 2.0

* Songs now have a key and transpose amount, which the user can edit.

* Song key, transpose amount supported for import from and export to OpenLyrics format (openlyrics.info for full XML description), as well as import from OpenLP format (.sqlite database)
