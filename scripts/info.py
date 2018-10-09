#! /usr/bin/python

import argparse

import os
import subprocess
import json

import getpass
import mysql.connector

def move_file(src, dst):
    # Use unix commands for file handling
    dstPath, _ = os.path.split(dst)
    subprocess.run(['mkdir', '-p', dstPath])
    subprocess.run(['mv', src, dst])

def build_path(song):
    # Use Unsorted as directory for artist/album if unspecified
    return os.path.join(
        '.',
        song.get('artist') or 'Unsorted',
        song.get('album') or 'Unsorted',
        song['title'] + song['ext']
    )

def to_song(path):
    # Check file extension
    _, ext = os.path.splitext(path)
    if ext not in ['.mp3', '.m4a']:
        return None

    # Query ffprobe for json data
    command = ['ffprobe', '-i', str(path), '-v', 'quiet', '-print_format', 'json', '-show_format']
    output = subprocess.run(command, stdout=subprocess.PIPE).stdout
    data = json.loads(output)

    fmt = data['format']
    tags = fmt['tags']

    # Check for ID3 tags
    if tags is None or tags['title'] is None:
        return None

    # Form song as dict
    song = {}
    song['title'] = tags['title']
    song['artist'] = tags.get('artist')
    song['album'] = tags.get('album')
    song['track'] = tags.get('track')
    song['duration'] = float(fmt['duration'])
    song['ext'] = ext
    song['path'] = build_path(song)

    return song

def get_songs(dir):
    # Walk through directory, collecting files that parse correctly
    songs = []
    for root, _, files in os.walk(dir):
        for file in files:
            path = os.path.join(root, file)
            song = to_song(path)
            if song is not None:
                songs.append((path, song))
    return songs

class SQLHandler(object):
    def __init__(self, host, database):
        # Query for user and (hidden) password
        user = input('User:')
        pw = getpass.getpass('Password:')

        # Connect immediately
        self.connection = mysql.connector.connect(user=user, password=pw, host=host, database=database)
        self.cursor = self.connection.cursor()
    
    def __del__(self):
        # Clean up sql
        self.connection.close()

    def insert_song(self, song):
        # Insert all fields
        query = (
            "INSERT INTO music "
            "(path, title, artist, album, track, duration)"
            "VALUES"
            "(%(path)s, %(title)s, %(artist)s, %(album)s, %(track)s, %(duration)s)"
        )
        self.cursor.execute(query, song)
        # Commit (auto-commit disabled by default)
        self.connection.commit()

if __name__ == "__main__":
    # Argument handling
    # -i srcs -o dest
    parser = argparse.ArgumentParser(description='Organize files into a new directory/sql')
    parser.add_argument('-i', metavar='PATH', type=str, nargs='+',
                        required=True, dest='srcs', 
                        help='list of source directories')
    parser.add_argument('-o', metavar='PATH', type=str,
                        required=True, dest='dest', 
                        help='destination directory')
    args = parser.parse_args()

    # Make connection
    sql = SQLHandler('localhost', 'media')

    # Handle each source folder
    for src in args.srcs:
        src = os.path.abspath(src)
        # Get songs
        songs = get_songs(src)
        for path, song in get_songs(src):
            new_path = os.path.abspath(os.path.join(args.dest, song['path']))
            # Move file and insert into sql
            move_file(path, new_path)
            sql.insert_song(song)