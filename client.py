import socket
import struct
import sys
import random
import time

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

def mac_to_bytes(mac):
    while len(mac) < 12:
        mac = '0' + mac
    macB = b''
    for i in range(0, 12, 2):
        m = int(mac[i:i + 2], 16)
        macB += struct.pack('!B', m)
    return macB


class Client:

    def __init__(self, gui: GuiClient, source_port=68, destination_port=67, destination_ip='127.0.0.1'):
        self.gui = gui
        self.destination_port = destination_port
        self.destination_ip = destination_ip
        self.discover_time=0

        # Creare socket UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        #Activare optiune transmitere pachete prin difuzie
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        #Activare reutilizare adresa
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #cand se trimite raspunsul de la server il va primi tot primul client initiat
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
                #se asteapta mesajul offer de la server
                self.gui.write_to_terminal("[CLIENT] Wainting DHCPOFFER")
                try:
                    data, address = self.socket.recvfrom(1024)
                except:
                    print("Eroare la primirea mesajului de offer")
                    sys.exit()

                #punem intr-un pachet ce s-a primit
                pack_offer_receive=Packet()
                pack_offer_receive.unpack(data)
                self.gui.write_text(pack_offer_receive.to_string())
                if pack_offer_receive.opcode==Packet.DHCPOFFER:
                    self.gui.write_to_terminal("[CLIENT] Received DHCPOFFER")


    def cleanup(self):
        self.running = False
        print("Waiting for the thread to close...")
        self.receive_thread.join()
        print("Closing socket...")
        self.socket.close()
        print("Cleanup done!")

    def discover(self):
        pack_discover=Packet()
        self.socket.sendto(pack_discover.pack(),("<broadcast>",67))
        self.gui.write_to_terminal("[CLIENT] Send DISCOVER")
        #self.discover_time=int(time.time())
        #print(self.discover_time)
        #trebuie inceput un thread pentru timer - daca clientul nu primeste raspuns dupa un
        #anumit timp sa retrimita
        self.gui.write_text(pack_discover.to_string())
