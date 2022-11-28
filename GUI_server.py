import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
import re

lease_v=False
name_v=False
ip_address_v=False
mask_v=False
message=""

class GUI_Server1():
    def __init__(self,gui_server1):
        super().__init__()
        #initializare fereastra
        gui_server1.title("Configuration of server parameters")
        gui_server1.geometry("800x500")
        gui_server1.resizable(False,False)

        self.lease_entry=Entry(gui_server1,font=("Arial",13))
        self.name_entry=Entry(gui_server1,font=("Arial",13))
        self.ip_address_entry=Entry(gui_server1,font=("Arial",13))
        self.mask_entry=Entry(gui_server1,font=("Arial",13))

        self.button_lease=Button(height=2,width=15,text="Set lease time",command=self.validation_lease)
        self.button_name=Button(height=2,width=15,text="Set name",command=self.validation_name)
        self.button_ip=Button(height=2,width=15,text="Set ip address",command=self.validation_ip_address)
        self.button_mask=Button(height=2,width=15,text="Set mask",command=self.validation_mask)
        self.button_start=Button(height=2,width=15,text="Start server",command=self.openNewWindow)

    def validation_lease(self):
        global lease_v
        global message
        lease=self.lease_entry.get()
        if(len(lease)==0):
            messagebox.showinfo("Lease time error","Lease can't be empty")
        else:
            if any(ch.isalpha() for ch in lease):
                self.lease_entry.delete(0, END)
                messagebox.showinfo("Lease time error", "Lease can't contain letters")
            else:
                lease_v=True
                message+="Lease time: "+lease+"\n"
    def validation_name(self):
        global name_v
        global message
        name = self.name_entry.get()
        if (len(name) == 0):
            messagebox.showinfo("Name error", "Name can't be empty")
        else:
            name_v=True
            message+='Name: '+name+"\n"
    def validation_ip_address(self):
        global ip_address_v
        global message
        ip_address=self.ip_address_entry.get()
        if(len(ip_address)==0):
            messagebox.showinfo("IP Address error", "Ip Address can't be empty")
        else:
            match=re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",ip_address)
            if (not match):
                self.ip_address_entry.delete(0,END)
                messagebox.showinfo("IP Address error", "Ip Address format error")
            else:
                bytes=ip_address.split(".")
                for ip_byte in bytes:
                    if(int(ip_byte)<0 or int(ip_byte)>255 or any(i.isalpha() for i in ip_byte)):
                        self.ip_address_entry.delete(0, END)
                        messagebox.showinfo("IP Address error", "Ip Address format error")
                    else:
                        ip_address_v=True
                message+="IP Address: "+ip_address+"\n"
    def validation_mask(self):
        global mask_v
        global message
        mask=self.mask_entry.get()
        if(len(mask)==0):
            messagebox.showinfo("Mask error", "Mask can't be empty")
        else:
            if any(ch.isalpha() for ch in mask):
                 self.mask_entry.delete(0, END)
                 messagebox.showinfo("Mask error", "Mask can't contain letters")
            else:
                if (int(mask) < 1 or int(mask) > 32):
                    self.mask_entry.delete(0, END)
                    messagebox.showinfo("Mask error", "Mask can be between 1 and 32")
                else:
                    mask_v=True
                    message+="Mask: "+mask+'\n'
    def openNewWindow(self):

        print(message)
        print("\n")
        print(lease_v)
        print(name_v)
        print(ip_address_v)
        print(mask_v)

        if(lease_v and name_v and ip_address_v and mask_v):
            gui2=tk.Tk()
            gui_server2=GUI_Server2(gui2).run()

        else:
            messagebox.showinfo("Start error", "the fields have not been filled in correctly")
    def run(self):

        label1=Label(text="Lease time",font=("Arial",13))
        label2=Label(text="Name",font=("Arial",13))
        label3=Label(text="IP Address",font=("Arial",13))
        label4=Label(text="Mask",font=("Arial",13))

        label1.grid(row=1,column=1,padx=50,pady=40,sticky='w')
        label2.grid(row=3,column=1,padx=50,pady=40,sticky='w')
        label3.grid(row=5,column=1,padx=50,pady=40,sticky='w')
        label4.grid(row=7,column=1,padx=50,pady=40,sticky='w')

        self.lease_entry.grid(row=1,column=2)
        self.name_entry.grid(row=3,column=2)
        self.ip_address_entry.grid(row=5,column=2)
        self.mask_entry.grid(row=7,column=2)

        self.button_lease.grid(row=1,column=3,padx=50)
        self.button_name.grid(row=3,column=3,padx=50)
        self.button_ip.grid(row=5,column=3,padx=50)
        self.button_mask.grid(row=7,column=3,padx=50)

        self.button_start.grid(row=8,column=4,padx=50)

class GUI_Server2():
    def __init__(self,gui_server2):
        super().__init__()
        #initializare fereastra
        gui_server2.title("Server Main page")
        gui_server2.geometry("900x600")
        gui_server2.resizable(False,False)

        self.view_frame=Frame(gui_server2)
        self.middle_frame=Frame(gui_server2)
        self.bottom_frame=Frame(gui_server2)

        self.view_text=Text(self.view_frame,width=65,height=10)
        self.info_server=Text(self.view_frame,width=30,height=10)
        self.progress=Text(self.middle_frame,width=105,height=10)

        self.write_text(message)

        self.view_text=scrolledtext.ScrolledText(self.view_frame,height=10,width=70)
        self.progress=scrolledtext.ScrolledText(self.middle_frame,height=10,width=100)

        self.release_ip_entry=Entry(self.bottom_frame)
        self.button_ip=Button(self.bottom_frame,height=1,width=10,text="Release",command=self.validation_ip_address)
        self.button_stop=Button(self.bottom_frame,height=1,width=10,text="Stop Server")
        self.button_close=Button(self.bottom_frame,height=1,width=10,text="Close Server",command=gui_server2.destroy)

    def validation_ip_address(self):
        global ip_address_v
        ip_address=self.release_ip_entry.get()
        if(len(ip_address)==0):
            messagebox.showinfo("IP Address error", "Ip Address can't be empty")
        else:
            match=re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",ip_address)
            if (not match):
                self.release_ip_entry.delete(0,END)
                messagebox.showinfo("IP Address error", "Ip Address format error")
            else:
                bytes=ip_address.split(".")
                for ip_byte in bytes:
                    if(int(ip_byte)<0 or int(ip_byte)>255 or any(i.isalpha() for i in ip_byte)):
                        self.release_ip_entry.delete(0, END)
                        messagebox.showinfo("IP Address error", "Ip Address format error")
                    else:
                        ip_address_v=True

    def run(self):

        self.view_frame.grid(row=0,column=0)
        self.middle_frame.grid(row=1,column=0)
        self.bottom_frame.grid(row=2,column=0)

        view_label=Label(self.view_frame,text="View")
        view_label.grid(row=1,column=0,padx=15,pady=10,sticky='w')
        self.view_text.grid(row=2,column=0,padx=15)

        text1_label=Label(self.bottom_frame,text="Release IP Address")
        text1_label.grid(row=2, column=0,pady=50)
        self.release_ip_entry.grid(row=2, column=1,padx=10)
        self.button_ip.grid(row=3,column=1)

        self.button_stop.grid(row=2,column=4,padx=200)
        self.button_close.grid(row=3,column=4,padx=200)


        info_label=Label(self.view_frame,text="Info Server")
        info_label.grid(row=1,column=1,padx=50,sticky='w')
        self.info_server.grid(row=2,column=1,padx=20,sticky='w')


        progress_label=Label(self.view_frame,text="Progress")
        progress_label.grid(row=3,column=0,padx=15,pady=15,sticky='w')
        self.progress.grid(row=4,column=0,padx=15)

    def write_text(self,information):
        self.info_server.insert(END,information)


if __name__=="__main__":
    gui=tk.Tk()
    gui_client=GUI_Server1(gui).run()
    gui.mainloop()