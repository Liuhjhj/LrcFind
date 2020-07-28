# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  Liuhjhj
@File           :  Window.py
"""
from PyQt5.QtGui import QTextCursor, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QHBoxLayout, \
    QVBoxLayout, QDesktopWidget
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import get_song_list

## 获取歌曲的搜索结果
class get_song_infor_thread(QThread):
    song = pyqtSignal(list)
    song_list = pyqtSignal(list)
    data_signal = pyqtSignal(dict)

    def __init__(self, name):
        super().__init__()
        self.name = name

    def run(self):
        import get_song_infor
        song_infor = get_song_list.Music_api()
        song_list = song_infor.get_music_list(self.name)
        data = song_infor.get_data(self.name)
        self.data_signal.emit(data)
        self.song_list.emit(song_list)
        information = get_song_infor.Informaton()
        song_infor = information.get_song_information(song_list)
        self.song.emit(song_infor)

## 获取歌曲的歌词
class get_song_lrc_thread(QThread):
    song_lrc_signal = pyqtSignal(str)

    def __init__(self, song_list, index):
        super().__init__()
        self.index = index
        self.song_list = song_list

    def run(self):
        import get_song_lrc
        song_lrc = get_song_lrc.Lyric_api().get_lyric(self.song_list, self.index)
        self.song_lrc_signal.emit(song_lrc)

## 获取歌曲的热门评论
class get_song_hot_comments_thread(QThread):
    song_hot_comments_signal = pyqtSignal(list)

    def  __init__(self, song_list, index, data):
        super().__init__()
        self.index = index
        self.song_list = song_list
        self.data = data

    def run(self):
        import get_song_hot_comments
        if self.data is not None:
            song_hot_comments = get_song_hot_comments.comments_api()\
                .get_hot_comments(self.song_list, self.index, self.data)
            self.song_hot_comments_signal.emit(song_hot_comments)

class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.label = QLabel('歌曲名')
        self.song_name = QLineEdit()
        self.btn = QPushButton('开始查询')
        self.btn2 = QPushButton('歌词')
        self.btn3 = QPushButton('热门评论')
        self.combobox = QComboBox()
        self.lrc = QTextEdit()
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.label)
        self.h_layout.addWidget(self.song_name)
        self.h_layout.addWidget(self.btn)
        self.h_layout2 = QHBoxLayout()
        self.h_layout2.addWidget(self.btn2)
        self.h_layout2.addWidget(self.btn3)
        self.v_layout = QVBoxLayout()
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(self.combobox)
        self.v_layout.addLayout(self.h_layout2)
        self.v_layout.addWidget(self.lrc)
        self.setLayout(self.v_layout)
        self.setWindowTitle('歌词查询')
        self.btn.clicked.connect(self.get_song_data)
        self.combobox.currentIndexChanged.connect(self.get_song_lrc)
        self.btn3.clicked.connect(self.get_song_hot_comments)
        self.btn2.clicked.connect(lambda: self.update_lrc(self.lyric))
        self.btn2.setEnabled(False)
        self.btn3.setEnabled(False)
        self.resize(600, 500)
        self.center()

    ## 界面居中
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    ## 开始获取搜索歌曲结果的线程
    def get_song_data(self):
        if self.song_name.text() == "":
            self.lrc.setText("请输入歌曲名称")
            return
        self.up_box = get_song_infor_thread(self.song_name.text())
        self.up_box.song.connect(self.update_combobox)
        self.up_box.data_signal.connect(self.get_data)
        self.up_box.song_list.connect(self.save_song_list)
        self.btn2.setEnabled(True)
        self.btn3.setEnabled(True)
        self.up_box.start()
        self.combobox.clear()

    ## 开始获取歌曲评论的线程
    def get_song_hot_comments(self):
        self.up_hot_comments = get_song_hot_comments_thread(self.song_list, self.combobox.currentIndex(),self.data)
        self.up_hot_comments.song_hot_comments_signal.connect(self.update_comments)
        self.up_hot_comments.start()


    ## 槽函数：把爬到的结果放到combobox
    def update_combobox(self, list):
        for lis in list:
            self.combobox.addItem(lis)

    ## 点击函数：开始获取歌词的线程
    def get_song_lrc(self):
        if self.combobox.currentIndex() == 0 \
                and self.combobox.currentText() == '':
            return
        else:
            self.up_lrc = get_song_lrc_thread(self.song_list, self.combobox.currentIndex())
            self.up_lrc.song_lrc_signal.connect(self.update_lrc)
            self.up_lrc.start()
            self.lrc.clear()

    ## 槽函数：显示歌词
    def update_lrc(self, lyric):
        self.lrc.setTextColor(QColor(0,0,0))
        self.lrc.setText('')
        self.lrc.setText(lyric)
        self.lyric = lyric

    ## 槽函数：加载全局搜索结果变量
    def save_song_list(self, list):
        self.song_list = list

    ## 槽函数：加载Params和SecretKey全局变量
    def get_data(self, data):
        self.data = data

    ## 槽函数：显示评论
    def update_comments(self, comments):
        self.lrc.setText('')
        for comment in comments:
            self.lrc.append('<font color=\"#0000FF\">'+ comment['user']['nickname'] +'</font>'+': '+comment['content'])
            self.lrc.append('\n')
        cursor = self.lrc.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.lrc.setTextCursor(cursor)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
