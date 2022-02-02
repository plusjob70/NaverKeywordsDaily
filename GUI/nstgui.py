from cgitb import text
import tkinter as tk
from naver_trends.service.gsheetsservice import GSheetsService
from common.constant import *

class NSTApp():
    def __init__(self):
        self.window = tk.Tk()
        self.window.iconbitmap('common/resources/enzinex_logo.ico')
        self.window.title(TITLE)
        self.window.geometry(DEFAULT_WINDOW_SIZE)
        #self.window.resizable(False, False)

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
        age_radio_btn = tk.Radiobutton(
            self.window,
            variable=radio_var,
            text='연령 추출',
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
            command=self.get_current_selection_items,
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

    def get_current_selection_items(self):
        for idx in self.total_listbox.curselection():
            print(self.total_listbox.get(idx))


if __name__ == '__main__':
    NSTApp().run()