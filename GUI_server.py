import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
import re

import server


# am facut functiile de verificare putin mai generale
# probabil o sa le mut intr-un modul separat
def validate_lease_time(lease_time) -> bool:
    if len(lease_time) == 0:
        messagebox.showerror("Lease time error", "Lease time can't be empty")
        return False
    elif any(ch.isalpha() for ch in lease_time):
        messagebox.showerror("Lease time error", "Lease time can't contain letters")
        return False
    return True


def validate_ip_address(ip_address) -> bool:
    if len(ip_address) == 0:
        messagebox.showerror("IP Address error", "Ip Address can't be empty")
        return False
    elif not re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", ip_address):
        messagebox.showerror("IP Address error", "Ip Address format error")
        return False
    else:
        for ip_byte in ip_address.split("."):
            if int(ip_byte) < 0 or int(ip_byte) > 255 or any(i.isalpha() for i in ip_byte):
                messagebox.showerror("IP Address error", "Ip Address format error")
                return False
    return True


def validate_name(name) -> bool:
    if len(name) == 0:
        messagebox.showerror("Name error", "Name can't be empty")
        return False
    return True


def validate_mask(mask) -> bool:
    if len(mask) == 0:
        messagebox.showerror("Mask error", "Mask can't be empty")
        return False
    elif any(ch.isalpha() for ch in mask):
        messagebox.showerror("Mask error", "Mask can't contain letters")
        return False
    elif int(mask) < 1 or int(mask) > 32:
        messagebox.showerror("Mask error", "Mask can be between 1 and 32")
        return False
    return True


class GUIServerConfig:
    def __init__(self, window_context):
        super().__init__()
        # initializare fereastra
        self.window_context = window_context
        self.window_context.title("Configuration of server parameters")
        self.window_context.geometry("800x500")
        self.window_context.resizable(False, False)

        # adaugat un panou principal pentru a facilita trecerea dintre ferestre
        self.main_panel = ttk.Frame(self.window_context, padding=(5, 5, 12, 0))
        self.main_panel.grid(column=0, row=0, sticky="nsew")
        self.window_context.grid_columnconfigure('all', weight=1)
        self.window_context.grid_rowconfigure('all', weight=1)

        # self.message = ""
        self.lease_entry = Entry(self.main_panel, font=("Arial", 13))
        self.name_entry = Entry(self.main_panel, font=("Arial", 13))
        self.ip_address_entry = Entry(self.main_panel, font=("Arial", 13))
        self.mask_entry = Entry(self.main_panel, font=("Arial", 13))

        self.button_start = Button(height=2, width=15, text="Start server", command=self.start_server)

    def start_server(self):
        if not validate_mask(self.mask_entry.get()):
            self.mask_entry.delete(0, END)
            raise ValueError
        if not validate_name(self.name_entry.get()):
            raise ValueError
        if not validate_lease_time(self.lease_entry.get()):
            self.lease_entry.delete(0, END)
            raise ValueError
        if not validate_ip_address(self.ip_address_entry.get()):
            self.ip_address_entry.delete(0, END)
            raise ValueError

        gui_server = GUIServer(self.window_context, lease_time=self.lease_entry.get(),
                               ip_address=self.ip_address_entry.get(), name=self.name_entry.get(),
                               mask_size=self.mask_entry.get())
        self.main_panel.destroy()

        gui_server.run()

    def run(self):

        label1 = Label(self.main_panel, text="Lease time", font=("Arial", 13))
        label2 = Label(self.main_panel, text="Name", font=("Arial", 13))
        label3 = Label(self.main_panel, text="IP Address", font=("Arial", 13))
        label4 = Label(self.main_panel, text="Mask", font=("Arial", 13))

        label1.grid(row=1, column=1, padx=50, pady=40, sticky='w')
        label2.grid(row=3, column=1, padx=50, pady=40, sticky='w')
        label3.grid(row=5, column=1, padx=50, pady=40, sticky='w')
        label4.grid(row=7, column=1, padx=50, pady=40, sticky='w')

        self.lease_entry.grid(row=1, column=2)
        self.name_entry.grid(row=3, column=2)
        self.ip_address_entry.grid(row=5, column=2)
        self.mask_entry.grid(row=7, column=2)

        self.button_start.grid(row=8, column=4, padx=50)

        # default values for ease of testing
        self.lease_entry.insert(0, "86400")
        self.name_entry.insert(0, "Server.dhcp")
        self.ip_address_entry.insert(0, "127.0.0.1")
        self.mask_entry.insert(0, "24")


class GUIServer:
    def __init__(self, window_context, lease_time, name, ip_address, mask_size):
        super().__init__()

        # initializare fereastra
        self.window_context = window_context
        self.window_context.title("Server Main page")
        self.window_context.geometry("900x600")
        self.window_context.resizable(False, False)

        # initializare backend
        self.backend = server.Server(self, lease_time=int(lease_time), name=name, ip_address=ip_address,
                                     mask_size=int(mask_size))

        # adaugat un panou principal pentru a facilita trecerea dintre ferestre
        self.main_panel = ttk.Frame(self.window_context, padding=(5, 5, 12, 0))
        self.main_panel.grid(column=0, row=0, sticky="nsew")
        self.window_context.grid_columnconfigure('all', weight=1)
        self.window_context.grid_rowconfigure('all', weight=1)

        self.view_frame = Frame(self.main_panel)
        self.middle_frame = Frame(self.main_panel)
        self.bottom_frame = Frame(self.main_panel)

        # self.view_text = Text(self.view_frame, state="disabled", width=65, height=10)
        self.info_server = Text(self.view_frame, width=30, height=10)
        # self.progress = Text(self.middle_frame, state="disabled", width=105, height=10)

        self.view_text = scrolledtext.ScrolledText(self.view_frame, state="disabled", height=10, width=70)
        self.progress = scrolledtext.ScrolledText(self.middle_frame, state="disabled", height=10, width=100)

        self.release_ip_entry = Entry(self.bottom_frame)
        self.button_ip = Button(self.bottom_frame, height=1, width=10, text="Release",
                                command=self.validate_ip_address)
        # poate o comanda care redeschide view-ul de configurare?
        # self.button_stop = Button(self.bottom_frame, height=1, width=10, text="Stop Server")
        self.button_close = Button(self.bottom_frame, height=1, width=10, text="Close Server",
                                   command=self.return_to_config)
        # self.button_config = Button(self.bottom_frame, height=1, width=10, text="Config")

    def return_to_config(self):

        self.main_panel.destroy()

        gui = GUIServerConfig(self.window_context)
        gui.run()

        self.cleanup()

    def validate_ip_address(self):
        validate_ip_address(self.release_ip_entry.get())

    def run(self):

        self.view_frame.grid(row=0, column=0)
        self.middle_frame.grid(row=1, column=0)
        self.bottom_frame.grid(row=2, column=0)

        view_label = Label(self.view_frame, text="View")
        view_label.grid(row=1, column=0, padx=15, pady=10, sticky='w')
        self.view_text.grid(row=2, column=0, padx=15)

        # self.write_text(message)

        text1_label = Label(self.bottom_frame, text="Release IP Address")
        text1_label.grid(row=2, column=0, pady=20)
        self.release_ip_entry.grid(row=2, column=1, padx=10)
        self.button_ip.grid(row=3, column=1)

        # self.button_stop.grid(row=2, column=4, padx=200)
        self.button_close.grid(row=3, column=4, padx=200)
        # self.button_config.grid(row=4, column=4, padx=200, pady=20)

        info_label = Label(self.view_frame, text="Info Server")
        info_label.grid(row=1, column=1, padx=50, sticky='w')
        self.info_server.grid(row=2, column=1, padx=20, sticky='w')

        progress_label = Label(self.view_frame, text="Progress")
        progress_label.grid(row=3, column=0, padx=15, pady=15, sticky='w')
        self.progress.grid(row=4, column=0, padx=15)

    def write_text(self, message):
        self.info_server.insert('end', message)

    def write_to_terminal(self, msg):
        self.progress['state'] = 'normal'
        # might need to insert a '\n'
        self.progress.insert('end', msg)
        self.progress.insert('end', '\n')
        self.progress['state'] = 'disabled'

    # pseudo-destructor pentru a evita thread-uri orfane
    def cleanup(self):
        self.backend.cleanup()


if __name__ == "__main__":
    window = tk.Tk()
    gui_config = GUIServerConfig(window)
    gui_config.run()
    window.mainloop()
