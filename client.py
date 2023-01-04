import socket
import sys
import random
import select
import threading

import DHCP_Message
from GUI_client import GuiClient
from Packet import Packet


def gen_xid():
    return random.randint(1, 0xffffffff)

# o functie pentru random MAC address
def generate_mac():
    mac= "".join(random.choice("abcdef0123456789") for _ in range(0,12))
    return mac


class Client:

    def __init__(self, gui: GuiClient, source_port=68, destination_port=67, destination_ip='127.0.0.1'):
        self.gui = gui
        self.destination_port = destination_port
        self.destination_ip = destination_ip

        self.p = Packet(Packet.DHCPDISCOVER,b'\x9c\xb7\x0d\x69\x71\x8d')



        # Creare socket UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("", 68))
        self.running = True
        try:
            self.receive_thread = threading.Thread(target=self.receive_fct)
            self.receive_thread.start()
        except:
            print("Eroare la pornirea thread‐ului")
            sys.exit()


    def receive_fct(self):
        contor = 0
        while self.running:
            # Apelam la functia sistem IO -select- pentru a verifca daca socket-ul are date in bufferul de receptie
            # Stabilim un timeout de 1 secunda
            r, _, _ = select.select([self.socket], [], [], 10)
            if not r:
                contor = contor + 1
            else:
                data, address = self.socket.recvfrom(1024)
                self.gui.write_to_terminal("S-a receptionat mesajul OFFER de la " + str(address))
                self.gui.write_text(self.p.to_string())
                #self.gui.write_to_terminal("Contor= " + str(contor))

    def cleanup(self):
        self.running = False
        print("Waiting for the thread to close...")
        self.receive_thread.join()
        print("Closing socket...")
        self.socket.close()
        print("Cleanup done!")

    def send_discover(self):
        self.gui.write_to_terminal("S-a trimis mesajul DISCOVER ")
        self.socket.sendto(self.p.pack(),("<broadcast>", 67))