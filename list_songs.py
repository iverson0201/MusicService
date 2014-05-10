from __future__ import print_function
# coding:utf-8
import glob
import os
import unicodedata
import eyed3

import sys
fse = sys.getfilesystemencoding()
files = [x for x in glob.glob(u"songs/*.mp3")]


def calc_string_width(s):
    """ return extra width generated by east-asian chars"""
    extra_width = 0
    for c in s:
        ctype = unicodedata.east_asian_width(c)
        if ctype == 'F' or ctype == 'W' or ctype == 'A':
            extra_width += 1
    return extra_width, len(s) + extra_width

with open("songs.txt", 'wt') as output, open("gen_table.txt", 'wt') as gt:
    for f in files:
        song = eyed3.load(f)
        title = os.path.split(f)[1]
        album = song.tag.album
        artist = song.tag.artist
        try:
            # 有些信息是按latin1 decode的, 变成\xcb\xea这样, 但实际上应该是gbk decode, 即两个字节应该一起读
            # 所以要先encode回bytes再用gbk decode
            # refer to http://stackoverflow.com/questions/23521361/how-to-convert-string-to-bytes-in-python-2
            artist = artist.encode('latin1').decode('gbk')
            album = album.encode('latin1').decode('gbk')
        except UnicodeEncodeError:
            pass
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
        gt.write((title + ' - ' + artist + ';' + album + '\n').encode('utf-8'))
        # paste gen_table.txt to http://www.tablesgenerator.com/markdown_tables#
        # semicolon is seperator
        # then copy/paste generated markdown table to README.md


def rewrite_readme():
    import codecs
    with codecs.open('songs.txt', 'r', 'utf-8') as songs,\
            codecs.open('README.md', 'w') as readme:
        readme_title_text = u"laike9m ACG 音樂精選  \n=======\n\n個人向ACG音樂精選\n\n"
        readme.write(readme_title_text.encode('utf-8'))
        for line in songs.readlines():
            readme.write('\t' + line.rstrip().encode('utf-8') + '\n')

# rewrite_readme()


# TODO: github页面字体宽度问题
