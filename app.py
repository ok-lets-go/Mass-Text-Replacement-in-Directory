"Directory Find and Replace App"
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as notice
from tkinter import filedialog as file
from pathlib import Path


class Window(tk.Tk):
    """Replace all instances of a given string within the file names in a given directory"""

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Folder Find and Replace")

        self.target_dir = None
        self.display_list = None
        self.replace_list = None
        self.build_window()

    def build_window(self):
        "Places all relevant objects into the window frame"
        self.home_frame = tk.Frame(self)
        self.home_frame.pack()

        # Items for target folder selection
        target_dir_label = tk.Label(self.home_frame, text="Target Folder")
        self.target_dir_entry = tk.Entry(
            self.home_frame, width=100, borderwidth=4)
        browse_button = tk.Button(self.home_frame, text="Browse",
                                  command=self.browse)

        # items for target text selection
        target_label = tk.Label(self.home_frame, text="Find What: ")
        self.target_entry = tk.Entry(self.home_frame, width=100, borderwidth=4)

        # items for replacement text selection
        replacement_label = tk.Label(
            self.home_frame, text="Replace With: ")
        self.replacement_entry = tk.Entry(
            self.home_frame, width=100, borderwidth=4)

        target_dir_label.grid(row=0, column=0, pady=(20, 20), padx=10)
        self.target_dir_entry.grid(row=0, column=1, columnspan=3,
                                   pady=(20, 20), padx=10)
        browse_button.grid(row=0, column=4, pady=(20, 20), padx=(5, 10))

        target_label.grid(row=1, column=0, pady=(20, 20), padx=10)
        replacement_label.grid(row=2, column=0, pady=(20, 20), padx=10)

        self.target_entry.grid(row=1, column=1, columnspan=3,
                               pady=(20, 20), padx=10)
        self.replacement_entry.grid(row=2, column=1, columnspan=3,
                                    pady=(20, 20), padx=10)

        # bottom buttons
        cancel_btn = tk.Button(self.home_frame, text="Exit", command=self.quit)
        find_btn = tk.Button(self.home_frame, text="Find",
                             command=lambda: (self.find_items(), self.display_items()))
        replace_btn = tk.Button(self.home_frame, text="Replace",
                                command=self.replace_items)
        replaceall_btn = tk.Button(self.home_frame, text="Replace All",
                                   command=self.replace_all)

        cancel_btn.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        find_btn.grid(row=3, column=3, padx=5, pady=5, sticky=tk.E)
        replace_btn.grid(row=3, column=4, padx=5, pady=5)
        replaceall_btn.grid(row=3, column=5, padx=5, pady=5)
        # File List
        self.table_frame = tk.Frame(self.home_frame)
        self.item_display = ttk.Treeview(
            self.table_frame, selectmode="extended",  height=10, show='tree')
        self.item_display['columns'] = ("Items", )
        self.item_display.column("#0", width=0, stretch=tk.NO)
        self.item_display.column("Items", width=750,  minwidth=120)

        # scroll bar for file list
        scrollbar = tk.Scrollbar(self.table_frame)
        scrollbar.pack(side="right", fill="y")
        scrollbar.config(command=self.item_display.yview)

    def browse(self):
        "Open browser to select target folder"
        filename = file.askdirectory()

        self.target_dir_entry.delete(0, tk.END)
        self.target_dir_entry.insert(0, filename)

    def find_items(self):
        "Display all files in the folder with the given string"
        target_dir = Path(self.target_dir_entry.get())
        target_text = self.target_entry.get()
        self.display_list = []
        self.replace_list = []
        if target_dir.is_dir():
            for item in target_dir.iterdir():

                if target_text in str(item.stem):
                    solo_tuple = (str(item.stem), )
                    self.display_list.append(solo_tuple)
                    self.replace_list.append(item)

        elif not target_dir.is_dir():
            notice.showerror(message="Invalid folder path given")

    def replace_items(self):
        "Replace given string in selected files with replacement string"
        counter = 0
        fail_count = 0
        fail_text = ""
        for index in self.item_display.selection():
            item = self.replace_list[int(index)]
            fail_val, file = self.replace(item)
            fail_count += fail_val
            if fail_val: 
                fail_text += '\u2022 ' + file + '\n'
            if file == 'invalid': 
                fail_text = 'invalid'
            counter += 1
        self.table_frame.grid_forget()

        if fail_count: 
            response = notice.askretrycancel(title="Error",  message=
                            f"""{counter} files renamed\n 
{fail_count} file(s) not accessible:
{fail_text}                             
            """)
            if response:
                self.replace_items()
        elif 'invalid' not in fail_text:
            notice.showerror(title = "Error", message = 'Invalid replacement text selected, cannot contain \\/:*|<>"')
        else: 
            notice.showinfo(title="Success", message=f"{counter} file(s) renamed")


    def replace_all(self):
        "Replace given string in all files with replacement string"
        self.find_items()
        counter = 0
        fail_count = 0
        fail_text = ""
        for item in self.replace_list:
            fail_val, file = self.replace(item)
            fail_count += fail_val
            if fail_val: 
                fail_text += '\u2022 ' + file + '\n'
            if file == 'invalid': 
                fail_text = 'invalid'
            counter += 1
        self.table_frame.grid_forget()
        if fail_count: 
            response = notice.askretrycancel(title="Error",  message=
                            f"""{counter} files renamed\n 
{fail_count} file(s) not accessible:
{fail_text}                             
            """)
            if response:
                self.replace_items()
        elif 'invalid' in fail_text:
            notice.showerror(title = "Error", message = 'Invalid replacement text selected, cannot contain \\/:*|<>"')
        else: 
            notice.showinfo(title="Success", message=f"{counter} file(s) renamed")

    def replace(self, item):
        """Actual replacement command"""
        try: 
            item.rename(f"{item.parent}\\{str(item.stem).replace(
                    self.target_entry.get(), self.replacement_entry.get())}{item.suffix}")
            return 0, None
            
        except PermissionError: 
            return 1, f'{item.stem}.{item.suffix}'
        
        except FileNotFoundError: 
            return 0, 'invalid'
        except OSError:
            return 0, 'invalid'

    def display_items(self):
        "Display found items in window"
        for i in self.item_display.get_children():
            self.item_display.delete(i)
        self.update()
        for index, item in enumerate(self.display_list):
            self.item_display.insert(
                parent='', index="end", iid=index, text="Item", values=item)
        self.table_frame.grid(
            row=4, column=0, columnspan=5, sticky=tk.EW, pady=5)
        self.item_display.pack()


def launch_app():
    """allows app to be called by a separate module"""
    app = Window()
    app.mainloop()

if __name__ == "__main__":
    launch_app()
