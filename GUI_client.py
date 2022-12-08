import tkinter as tk
from tkinter import *

import client


class GuiClient:

    def __init__(self, gui_client):
        super().__init__()
        # initializare backend
        self.backend = client.Client(self)

        # initializare fereastra
        gui_client.title("DHCP Client")
        gui_client.geometry("900x600")
        gui_client.resizable(False, False)

        self.opt_frame = Frame(gui_client)
        self.right_frame = Frame(gui_client)

        # initializam variabilele pentru checkbox uri
        self.SUBNET_MASK = IntVar()
        self.ROUTER = IntVar()
        self.DNS = IntVar()
        self.REQUESTED_IP_ADDRESS = IntVar()
        self.LEASE_TIME = IntVar()
        self.MESSAGE_TYPE = IntVar()
        self.SERVER_IDENTIFIER = IntVar()
        self.PARAMETER_REQUESTED_LIST = IntVar()
        self.RENEWAL_TIME = IntVar()
        self.REBINDING_TIME = IntVar()
        self.END = IntVar()

        # cand o sa fie gata clasa client,aceast buton va avea command=self.discover
        self.button_start = Button(self.opt_frame, command=self.backend.send_discover, height=2, width=10,
                                   text="Start")
        self.ip_entry = Entry(self.opt_frame)
        self.lease_entry = Entry(self.opt_frame)

        self.text = Text(self.right_frame, state='disabled', width=45, height=16)
        self.text_terminal = Text(self.right_frame, state='disabled', width=45, height=16)

    def disable_entry(self):
        if self.REQUESTED_IP_ADDRESS.get() == 1:
            self.ip_entry.config(state=NORMAL)
        elif self.REQUESTED_IP_ADDRESS.get() == 0:
            self.ip_entry.config(state=DISABLED)

    def disable_entry_lease(self):
        if self.LEASE_TIME.get() == 1:
            self.lease_entry.config(state=NORMAL)
        elif self.LEASE_TIME.get() == 0:
            self.lease_entry.config(state=DISABLED)

    def run(self):
        self.opt_frame.grid(row=0, column=0)
        self.right_frame.grid(row=0, column=1, padx=60)

        opt_label = Label(self.opt_frame, text="DHCP Options")
        opt_label.grid(row=1, column=1, padx=50, pady=20)

        par_label = Label(self.right_frame, text="Current Parameters")
        par_label.grid(row=0, column=0)
        self.text.grid(row=1, column=0)

        terminal_label = Label(self.right_frame, text="Operations")
        terminal_label.grid(row=2, column=0)
        self.text_terminal.grid(row=3, column=0)

        opt1_label = Label(self.opt_frame, text="Option 1: Subnet Mask")
        opt2_label = Label(self.opt_frame, text="Option 3: Router")
        opt3_label = Label(self.opt_frame, text="Option 6: Domain Name Server")
        opt4_label = Label(self.opt_frame, text="Option 50: Requested IP Address")
        opt5_label = Label(self.opt_frame, text="Option 51: IP Address lease time")
        opt6_label = Label(self.opt_frame, text="Option 53: DHCP Message Type")
        opt7_label = Label(self.opt_frame, text="Option 54: Server Identifier")
        opt8_label = Label(self.opt_frame, text="Option 55: Parameter Requested List")
        opt9_label = Label(self.opt_frame, text="Option 58: Renewal Time Value")
        opt10_label = Label(self.opt_frame, text="Option 59: Rebinding Time Value")
        opt11_label = Label(self.opt_frame, text="Option 255: End")

        opt1_ck = Checkbutton(self.opt_frame, variable=self.SUBNET_MASK, height=2, width=4)
        opt2_ck = Checkbutton(self.opt_frame, variable=self.ROUTER, height=2, width=4)
        opt3_ck = Checkbutton(self.opt_frame, variable=self.DNS, height=2, width=4)
        opt4_ck = Checkbutton(self.opt_frame, variable=self.REQUESTED_IP_ADDRESS, height=2, width=4,
                              command=self.disable_entry)
        opt5_ck = Checkbutton(self.opt_frame, variable=self.LEASE_TIME, height=2, width=4,
                              command=self.disable_entry_lease)
        opt6_ck = Checkbutton(self.opt_frame, variable=self.MESSAGE_TYPE, height=2, width=4)
        opt7_ck = Checkbutton(self.opt_frame, variable=self.SERVER_IDENTIFIER, height=2, width=4)
        opt8_ck = Checkbutton(self.opt_frame, variable=self.PARAMETER_REQUESTED_LIST, height=2, width=4)
        opt9_ck = Checkbutton(self.opt_frame, variable=self.RENEWAL_TIME, height=2, width=4)
        opt10_ck = Checkbutton(self.opt_frame, variable=self.REBINDING_TIME, height=2, width=4)
        opt11_ck = Checkbutton(self.opt_frame, variable=self.END, height=2, width=4)

        opt1_label.grid(row=2, column=1, sticky='w')
        opt2_label.grid(row=3, column=1, sticky='w')
        opt3_label.grid(row=4, column=1, sticky='w')
        opt4_label.grid(row=5, column=1, sticky='w')
        self.ip_entry.config(state="disabled")
        self.ip_entry.grid(row=5, column=2)
        opt5_label.grid(row=6, column=1, sticky='w')
        self.lease_entry.config(state="disabled")
        self.lease_entry.grid(row=6, column=2)
        opt6_label.grid(row=7, column=1, sticky='w')
        opt7_label.grid(row=8, column=1, sticky='w')
        opt8_label.grid(row=9, column=1, sticky='w')
        opt9_label.grid(row=10, column=1, sticky='w')
        opt10_label.grid(row=11, column=1, sticky='w')
        opt11_label.grid(row=12, column=1, sticky='w')

        opt1_ck.grid(row=2, column=0)
        opt2_ck.grid(row=3, column=0)
        opt3_ck.grid(row=4, column=0)
        opt4_ck.grid(row=5, column=0)
        opt5_ck.grid(row=6, column=0)
        opt6_ck.grid(row=7, column=0)
        opt7_ck.grid(row=8, column=0)
        opt8_ck.grid(row=9, column=0)
        opt9_ck.grid(row=10, column=0)
        opt10_ck.grid(row=11, column=0)
        opt11_ck.grid(row=12, column=0)

        self.button_start.grid(row=15, column=0, padx=20, pady=20)

    def write_text(self, information):
        self.text.insert(END, str(information))

    def delete_text(self):
        self.text.delete(0, END)

    def write_to_terminal(self, msg):
        self.text_terminal['state'] = 'normal'
        self.text_terminal.insert('end', msg)
        self.text_terminal['state'] = 'disabled'

    def cleanup(self):
        self.backend.cleanup()


if __name__ == "__main__":
    window = tk.Tk()
    gui_client = GuiClient(window)
    gui_client.run()
    window.mainloop()
    gui_client.cleanup()
