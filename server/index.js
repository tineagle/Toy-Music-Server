function getList(rows, cb) {
    var list = document.createElement("ul");
    rows.forEach(row => {
        var elem = document.createElement("li");
        elem.appendChild(cb(row));
        list.appendChild(elem);
    });
    return list;
}

function replaceWithArtists() {
    $.getJSON("music.json?q=artist", actualReplaceWithArtists);
}

function actualReplaceWithArtists(rows) {
    var list = getList(rows, function(row) {
        var link = document.createElement('a');
        link.innerText = row['artist'];
        link.href = '#';
        link.onclick = function() {
            replaceWithAlbums(row['artist']);
        };
        return link;
    })
    var elem = document.getElementById('content');
    if(elem.firstChild) {
        elem.replaceChild(list, elem.firstChild);
    } else {
        elem.appendChild(list);
    }
}

function replaceWithAlbums(artist) {
    $.getJSON(`music.json?q[]=album&q[]=artist&artist=${artist}`, function(rows) {
        actualReplaceWithAlbums(rows, artist);
    });
}

function actualReplaceWithAlbums(rows, artist) {
    var list = getList(rows, function(row) {
        var link = document.createElement('a');
        link.innerText = row['album'];
        link.href = '#';
        link.onclick = function() {
            replaceWithSongs(row['artist'], row['album']);
        };
        return link;
    })
    var elem = document.getElementById('content');
    if(elem.firstChild) {
        elem.replaceChild(list, elem.firstChild);
    } else {
        elem.appendChild(list);
    }
}

function replaceWithSongs(artist, album) {
    $.getJSON(`localhost/music.json?artist=${artist}&album=${album}`, function(rows) {
        actualReplaceWithSongs(rows, artist, album);
    });
}

function actualReplaceWithSongs(rows, artist, album) {
    var list = getList(rows, function(row) {
        var link = document.createElement('a');
        link.innerText = row['title'];
        link.href = `Music/${row['path']}`;
        link.download = row['title'];
        return link;
    })
    var elem = document.getElementById('content');
    if(elem.firstChild) {
        elem.replaceChild(list, elem.firstChild);
    } else {
        elem.appendChild(list);
    }
}

function replaceWithNothing() {
    var elem = document.getElementById('content');
    while(elem.firstChild) {
        elem.removeChild(elem.firstChild);
    }
}