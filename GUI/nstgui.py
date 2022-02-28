#! /usr/bin/env python
import os
import subprocess
import tkinter as tk
from naver_trends.service.gsheetsservice import GSheetsService
from GUI.common.constant import *

class NSTApp():
    def __init__(self):
        self.window = tk.Tk()
        self.window.title(TITLE)
        self.window.geometry(DEFAULT_WINDOW_SIZE)
        self.gsheets = GSheetsService()
        self.total_listbox = None

    def run(self):
        # elements in listboxes
        client_list     = [client['name'] for client in self.gsheets.get_all_files_info()]
        client_list_var = tk.StringVar(value=client_list)

        radio_var = tk.StringVar(None, 'basic')

        basic_radio_btn = tk.Radiobutton(
            self.window,
            variable=radio_var,
            text='기본 추출',
            value='basic'
        )
        gender_radio_btn = tk.Radiobutton(
            self.window,
            variable=radio_var,
            text='성별 추출',
            value='gender'
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
            text='Refresh',
            command=self.refresh_total_listbox,
            width=10
        )
        select_all_btn = tk.Button(
            self.window,
            text='Select all',
            command=self.select_all,
            width=10
        )
        exe_btn = tk.Button(
            self.window,
            text='Execute',
            command=lambda: self.get_current_selection_items(radio_var),
            width=10
        )

        basic_radio_btn.pack()
        gender_radio_btn.pack()

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
        command_list = []
        selected_var = radio_var.get()
        
        if selected_var == 'basic':
            command_list.append(f'{os.getcwd()}/../naver_trends/basic_main.py')
        elif selected_var == 'gender':
            command_list.append(f'{os.getcwd()}/../naver_trends/gender_main.py')
        else:
            return

        for idx in self.total_listbox.curselection():
            command_list.append(self.total_listbox.get(idx))

        subprocess.call(command_list)


if __name__ == '__main__':
    NSTApp().run()