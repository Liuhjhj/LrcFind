# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  Liuhjhj
@File           :  Window.py
"""
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QHBoxLayout, \
    QVBoxLayout, QDesktopWidget
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import get_song_list


class get_song_infor_thread(QThread):
    song = pyqtSignal(list)
    song_list = pyqtSignal(list)

    def __init__(self, name):
        super().__init__()
        self.name = name

    def run(self):
        import get_song_infor
        song_list = get_song_list.Music_api().get_music_list(self.name)
        self.song_list.emit(song_list)
        information = get_song_infor.Informaton()
        song_infor = information.get_song_information(song_list)
        self.song.emit(song_infor)


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


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.label = QLabel('歌曲名')
        self.song_name = QLineEdit()
        self.btn = QPushButton('开始查询')
        self.combobox = QComboBox()
        self.lrc = QTextEdit()
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.label)
        self.h_layout.addWidget(self.song_name)
        self.h_layout.addWidget(self.btn)
        self.v_layout = QVBoxLayout()
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(self.combobox)
        self.v_layout.addWidget(self.lrc)
        self.setLayout(self.v_layout)
        self.setWindowTitle('歌词查询')
        self.btn.clicked.connect(self.get_song_data)
        self.combobox.currentIndexChanged.connect(self.get_song_lrc)
        self.resize(600, 500)
        self.center()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def get_song_data(self):
        self.up_box = get_song_infor_thread(self.song_name.text())
        self.up_box.song.connect(self.update_combobox)
        self.up_box.song_list.connect(self.save_song_list)
        self.up_box.start()
        self.combobox.clear()

    def update_combobox(self, list):
        for lis in list:
            self.combobox.addItem(lis)

    def get_song_lrc(self):
        if self.combobox.currentIndex() == 0 \
                and self.combobox.currentText() == '':
            return
        else:
            self.up_lrc = get_song_lrc_thread(self.song_list, self.combobox.currentIndex())
            self.up_lrc.song_lrc_signal.connect(self.update_text)
            self.up_lrc.start()
            self.lrc.clear()

    def update_text(self, lyric):
        self.lrc.setText(lyric)

    def save_song_list(self, list):
        self.song_list = list


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
