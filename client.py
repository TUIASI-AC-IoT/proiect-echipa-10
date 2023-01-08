import socket
import struct
import sys
import random
import time

import select
import threading
from GUI_client import GuiClient
from Packet import Packet

# max number of retransmission DHCPDISCOVER
MAX_COUNT = 5


# codul e facut doar pentru un client si server. Ai putea face sa fie valabil pentru mai multi?

class Client:

    def __init__(self, gui: GuiClient, source_port=68, destination_port=67, destination_ip='127.0.0.1'):
        self.gui = gui
        self.destination_port = destination_port
        self.destination_ip = destination_ip

        # variable for case that dhcpdiscover it's not send
        self.initial_discover_timeout = 1
        self.discover_timeout = 1
        self.max_discover_timeout = 30

        # variable for client
        self.xid = b''
        self.mac = b''
        self.your_ip = b''
        self.server_identifier = b''

        # Creare socket UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Activare optiune transmitere pachete prin difuzie
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Activare reutilizare adresa
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # daca am mai multi clienti
        # cand se trimite raspunsul de la server il va primi tot primul client initiat, ma gandesc ca ar fi de la faptul ca e acelasi port,idk
        self.socket.bind(("", 68))
        self.running = True
        # am cateva erori cand folosesc thread-urile,ai putea sa le rezolvi tu?
        # cand le folosesc mi se blocheaza clientul si nu inteleg de ce
        # si la clasa GUI_client e comentat in main:)
        '''try:
            self.receive_thread = threading.Thread(target=self.receive_fct)
            self.receive_thread.start()
        except:
            print("Eroare la pornirea thread‐ului")
            sys.exit()
'''

    '''def receive_fct(self):
        contor = 0
        while self.running:
            # Apelam la functia sistem IO -select- pentru a verifica daca socket-ul are date in bufferul de receptie
            # Stabilim un timeout de 1 secunda
            r, _, _ = select.select([self.socket], [], [], 10)
            if not r:
                contor = contor + 1
            else:
                # se asteapta mesajul offer de la server
                self.gui.write_to_terminal("[CLIENT] Wainting DHCPOFFER")
                try:
                    data, address = self.socket.recvfrom(1024)
                except:
                    print("Eroare la primirea mesajului de offer")
                    sys.exit()

                # punem intr-un pachet ce s-a primit
                pack_offer_receive = Packet()
                pack_offer_receive.unpack(data)
                self.gui.write_text(pack_offer_receive.to_string())
                if pack_offer_receive.opcode == Packet.DHCPOFFER:
                    self.gui.write_to_terminal("[CLIENT] Received DHCPOFFER")'''

    def cleanup(self):
        self.running = False
        print("Waiting for the thread to close...")
        self.receive_thread.join()
        print("Closing socket...")
        self.socket.close()
        print("Cleanup done!")

    def discover(self):
        # try to implement binary exponential backoff algorithm
        counter = 0
        pack_discover = Packet()
        self.xid = pack_discover.xid
        self.mac = pack_discover.client_hardware_address
        print('discover inainte')
        print(self.xid)
        print(self.mac)
        while counter < MAX_COUNT:
            self.socket.sendto(pack_discover.pack(), ("<broadcast>", 67))
            self.xid = pack_discover.xid
            self.mac = pack_discover.client_hardware_address
            print('dicover dupa')
            print(self.xid)
            print(self.mac)
            self.gui.write_to_terminal("[CLIENT] Send DHCPDISCOVER")
            # wait for DHCPOFFER response
            r, _, _ = select.select([self.socket], [], [], 10)
            if r:
                self.gui.write_to_terminal("[CLIENT] Waiting DHCPOFFER")
                data, address = self.socket.recvfrom(1024)
                pack_offer_receive = Packet()
                pack_offer_receive.unpack(data)
                print('offer')
                print(pack_offer_receive.xid)
                print(pack_offer_receive.client_hardware_address)
                # check if received message is a valid DHCPOFFER response
                if pack_offer_receive.opcode == Packet.DHCPOFFER:
                    # process offer and break out of loop
                    self.gui.write_to_terminal("[CLIENT] Receive DHCPOFFER")
                    self.gui.write_text(pack_offer_receive.to_string())
                    self.process_offer(pack_offer_receive)
                    break
                else:
                    counter += 1
                    time.sleep(2 ** counter)

        if counter == MAX_COUNT:
            self.handle_discovery_failure()

    def process_offer(self, receive_pack):

        # reset discover timeout
        self.discover_timeout = self.initial_discover_timeout

        #am rezolvat problema cu mac ul :)) de retinut - trebuie lucrat cu self.client_hardware_address, nu self.mac:))
        if receive_pack.client_hardware_address != self.mac:
            print('iesit la mac')
            return False
        # check if offer is valid
        if receive_pack.xid != self.xid:
            print('iesit la xid')
            return False

        # OFFER message transmit to client your_ip and server_ip
        self.your_ip = receive_pack.your_ip
        self.server_identifier = receive_pack.server_ip

        self.send_request(receive_pack)

    def handle_discovery_failure(self):

        self.discover_timeout = min(self.discover_timeout * 2, self.max_discover_timeout)

        # sleep before send another discover message
        time.sleep(self.discover_timeout)

        # send another message
        self.discover()


    def send_request(self, packet_offer_receive):

        self.gui.write_to_terminal('[CLIENT] Send REQUEST')
        packet_request = Packet()
        packet_request.message_type = Packet.REQUEST
        packet_request.mac = packet_offer_receive.mac
        packet_request.xid = packet_offer_receive.xid
        #here we need to considerate that case when client want the address chosen by him
        packet_request.client_ip = packet_offer_receive.your_ip
        packet_request.your_ip = packet_offer_receive.your_ip
        packet_request.server_ip = packet_offer_receive.server_ip
        packet_request.options = b'\x35\x01\x03' + b'\x36\x04' + packet_offer_receive.server_ip

        self.socket.sendto(packet_request.pack(),("<broadcast>", 67))


