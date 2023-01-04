import socket
import struct
import sys
import select
import threading
from Packet import Packet

from GUI_server import GUIServer

class Server:

    def __init__(self, gui: GUIServer, source_port=67, destination_port=68, destination_ip='127.0.0.1'):
        self.gui = gui
        self.destination_port = destination_port
        self.destination_ip = destination_ip
        # Creare socket UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Activare optiune transmitere pachete de difuzie
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        #activare optiune refolosire port
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', 67))

        self.socket.setblocking(False)
        self.running = True

        self.p_server = Packet(Packet.DHCPOFFER, b'')

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
                #
                self.gui.write_to_terminal(
                    "S-a receptionat mesaj DISCOVER de la " + str(address))
                #self.gui.write_to_terminal("Contor= " + str(contor))
                self.gui.write_to_terminal("Se trimite mesajul OFFER")
                self.socket.sendto(self.p_server.pack(),address)

    def cleanup(self):
        self.running = False
        print("Waiting for the thread to close...")
        self.receive_thread.join()
        print("Closing socket...")
        self.socket.close()
        print("Cleanup done!")
