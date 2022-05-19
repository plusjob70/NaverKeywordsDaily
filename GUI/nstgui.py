#! /usr/bin/python
import os
import subprocess
import tkinter as tk
from naver_trends.service.gsheetsservice import GSheetsService
from GUI.common.constant import *


class NSTApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title(TITLE)
        self.window.geometry(DEFAULT_WINDOW_SIZE)
        self.gsheets = GSheetsService()
        self.total_listbox = None

    def run(self):
        # elements in listboxes
        client_list = [client['name'] for client in self.gsheets.get_all_files_info()]
        client_list_var = tk.StringVar(value=client_list)

        radio_var = tk.StringVar(None, 'device')

        basic_radio_btn = tk.Radiobutton(
            self.window,
            variable=radio_var,
            text='디바이스 추출',
            value='device'
        )
        gender_radio_btn = tk.Radiobutton(
            self.window,
            variable=radio_var,
            text='성별 추출',
            value='gender'
        )
        age_radio_btn = tk.Radiobutton(
            self.window,
            variable=radio_var,
            text='나이 추출',
            value='age'
        )

        self.total_listbox = tk.Listbox(
            self.window,
            listvariable=client_list_var,
            selectmode='extended',
            activestyle='none',
            width=57,
            height=20
        )

        refresh_btn = tk.Button(
            self.window,
            text='새로고침',
            command=self.refresh_total_listbox,
            width=10
        )
        select_all_btn = tk.Button(
            self.window,
            text='전체선택',
            command=self.select_all,
            width=10
        )
        exe_btn = tk.Button(
            self.window,
            text='실행하기',
            command=lambda: self.get_current_selection_items(radio_var),
            width=10
        )

        basic_radio_btn.pack()
        gender_radio_btn.pack()
        age_radio_btn.pack()

        self.total_listbox.pack()
        refresh_btn.pack()
        select_all_btn.pack()
        exe_btn.pack()

        self.window.mainloop()

    def select_all(self):
        self.total_listbox.select_set(0, self.total_listbox.size())

    def refresh_total_listbox(self):
        self.total_listbox.delete(0, self.total_listbox.size())
        for idx, client in enumerate(self.gsheets.get_all_files_info()):
            self.total_listbox.insert(idx, client['name'])

    def get_current_selection_items(self, radio_var):

        selected_var = radio_var.get()
        command_list = [f'{os.getcwd()}/../naver_trends/main.py', selected_var]

        for idx in self.total_listbox.curselection():
            command_list.append(self.total_listbox.get(idx))

        if len(command_list) <= 2:
            print('Select at least one')
            return
        else:
            subprocess.call(command_list)


if __name__ == '__main__':
    NSTApp().run()
