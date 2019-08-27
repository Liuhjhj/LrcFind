# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  Liuhjhj
@File           :  get_song_name.py
"""


class Informaton(object):

    def get_song_information(self, song_list):
        song_infor = []
        for song in song_list:
            song = song['name'] + '-' + song['ar'][0]['name'] + '-' + song['al']['name']
            song_infor.append(song)
        return song_infor
