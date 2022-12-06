import socket
import sys
import random
import select
import threading

import DHCP_Message
from GUI_client import GuiClient


def gen_xid():
    return random.randint(1, 0xffffffff)


# o functie pentru random MAC address?


class Client:

    def __init__(self, gui: GuiClient, source_port=68, destination_port=67, destination_ip='127.0.0.1'):
        self.gui = gui
        self.destination_port = destination_port
        self.destination_ip = destination_ip
        # Creare socket UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.bind(('0.0.0.0', int(source_port)))
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
            r, _, _ = select.select([self.socket], [], [], 1)
            if not r:
                contor = contor + 1
            else:
                data, address = self.socket.recvfrom(1024)
                #
                self.gui.write_to_terminal("S-a receptionat " + str(data) + " de la " + address)
                self.gui.write_to_terminal("Contor= " + contor)

    def send_discover(self):
        self.socket.sendto(DHCP_Message.getBasicDISCOVER(gen_xid(), 0xf34a93dc2116),
                           (self.destination_ip, int(self.destination_port)))
