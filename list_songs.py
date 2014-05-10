from __future__ import print_function
# coding:utf-8
import glob
import os
import unicodedata
import sys
import eyed3
from collections import namedtuple

fse = sys.getfilesystemencoding()
files = [x for x in glob.glob(u"songs/*.mp3")]
SongInfo = namedtuple("SongInfo", "title_artist album")
songinfo_list = []


def calc_string_width(s):
    """ return extra width generated by east-asian chars"""
    extra_width = 0
    for c in s:
        ctype = unicodedata.east_asian_width(c)
        if ctype == 'F' or ctype == 'W' or ctype == 'A':
            extra_width += 1
    return extra_width, len(s) + extra_width

with open("songs.txt", 'wt') as output:
    for f in files:
        song = eyed3.load(f)
        title = os.path.split(f)[1][:-4]  # strip .mp3
        artist = song.tag.artist
        album = song.tag.album
        try:
            # 有些信息是按latin1 decode的, 变成\xcb\xea这样, 但实际上应该是gbk decode, 即两个字节应该一起读
            # 所以要先encode回bytes再用gbk decode
            # refer to http://stackoverflow.com/questions/23521361/how-to-convert-string-to-bytes-in-python-2
            artist = artist.encode('latin1').decode('gbk')
            album = album.encode('latin1').decode('gbk')
        except UnicodeEncodeError:
            pass
        songinfo_list.append(SongInfo(title+' - '+artist, album))
        extra_t_width, t_width = calc_string_width(title)
        extra_ar_width, ar_width = calc_string_width(artist)
        extra_al_width, al_width = calc_string_width(album)
        min_sum_width = t_width + al_width + ar_width + len(title) + len(album) + len(artist)
        if al_width + max(70, t_width + ar_width + 3) > 121:
            # 121 is github README max width, 3 = len(' - ')
            # tight mode, 1 = len('-')
            spaces = 121 - al_width - 1 - t_width - ar_width
            output.write((title + '-' + artist + ' '*spaces + album + '\n').encode('utf-8'))
        else:
            format_string = u'{:%d}' % (70-extra_t_width-extra_ar_width)
            output.write(format_string.format(title + ' - ' + artist).encode('utf-8'))
            output.write(album.encode('utf-8') + '  \n')


def rewrite_readme():
    with open('README.md', 'w') as readme:
        readme_title_text = u"laike9m ACG 音樂精選  \n=======\n\n個人向ACG音樂精選\n\n"
        readme.write(readme_title_text.encode('utf-8'))
        # draw markdown table
        head = "| title - artist | album |\n"
        seperator = "|---|---|\n"
        readme.write(head + seperator)
        global songinfo_list
        songinfo_list = sorted(songinfo_list, key=lambda s: s.album)
        for songinfo in songinfo_list:
            readme.write('|' + songinfo.title_artist.encode('utf-8') + '|' +
                         songinfo.album.encode('utf-8') + '\n')

rewrite_readme()
