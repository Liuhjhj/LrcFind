# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  Liuhjhj
@File           :  get_song_lrc.py
"""
import json
import requests


class Lyric_api(object):    # 根据歌曲id查找歌词

    def get_lyric(self, song_list, index):
        id = song_list[index]['id']
        web = 'http://music.163.com/api/song/lyric?id=' + str(id) + '&lv=1'
        head = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }
        timeout = 30
        try:
            page = requests.session().get(web, headers=head, timeout=timeout)
            page.encoding = 'UTF-8'
            a = page.text
            b = json.loads(a)   # str转dic
            return b['lrc']['lyric']
        except Exception as e:
            print(e)
            return 'Error'
