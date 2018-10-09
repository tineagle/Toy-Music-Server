#Music Server
This is simple toy music server made in half a week to learn/re-learn some web tools.

![](https://github.com/tineagle/Toy-Music-Server/tree/master/docs/clip.gif)

##File Info
/scripts/info.py -i srcs -o dest

* Restructures input folders into an output folder.
* Uses ffmpeg to scrape format/tag data and toss it in a MySQL (MariaDB) server.
* e.g. ./info.py -i /Your/Music/Source -o /Your/Music/Dest

/server/music.php

* Parses a GET query string to return JSON from SQL.
* Accessed as music.js via .htaccess

./server/index.js

* Requests/parses JSON to replace content without reloading the entire page.

/server/.htaccess

* Rewrites requests from music.json to music.php.

/server/index.html

* It displays. 👍

/server/index.css

* It formats. 👍