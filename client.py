import queue
import sys
import threading
import time

import select

from GUI_client import GuiClient
from Packet import *

# max number of retransmission DHCPDISCOVER
MAX_COUNT = 2


class Client:

    def __init__(self, gui: GuiClient, source_port=68, destination_port=67, destination_ip='127.0.0.1'):
        self.gui = gui
        self.destination_port = destination_port
        self.destination_ip = destination_ip

        # evenimente client
        self.received_offer_event = threading.Event()
        self.renew_timer = None
        self.rebind_timer = None

        # variabila pentru a stoca pachetele primite
        self.storage = queue.Queue(16)

        # variabila pentru a stoca optiunile pentru DISCOVER
        self.prepared_discover = None

        # variable for case that dhcpdiscover it's not send
        self.initial_discover_timeout = 1
        self.discover_timeout = 1
        self.max_discover_timeout = 30

        # variable for client
        self.xid = b''
        self.mac = b''
        self.your_ip = b''
        self.server_identifier = b''
        self.lease_time = int()
        self.t1 = int()
        self.t2 = int()

        # Creare socket UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Activare optiune transmitere pachete prin difuzie
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Activare reutilizare adresa
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind(("", 68))
        self.running = True

        try:
            self.receive_thread = threading.Thread(target=self.receive_fct)
            self.receive_thread.start()
        except:
            print("Eroare la pornirea thread‐ului")
            sys.exit()

    def cleanup(self):
        self.running = False
        print("Waiting for the thread to close...")
        self.receive_thread.join()
        print("Closing socket...")
        self.socket.close()
        print("Cleanup done!")

    def receive_fct(self):
        contor = 0
        while self.running:
            # Apelam la functia sistem IO -select- pentru a verifica daca socket-ul are date in bufferul de receptie
            # Stabilim un timeout de 10 secunde (relativ mare)
            # ar putea fi scazut catre 2-3 secunde
            r, _, _ = select.select([self.socket], [], [], 1)
            if not r:
                contor = contor + 1
            else:
                # se asteapta mesajul offer de la server
                self.gui.write_to_terminal("[CLIENT] Receive thread listening...")
                try:
                    data, address = self.socket.recvfrom(1024)
                except:
                    print("Eroare la citirea din socket")
                    sys.exit()

                # punem intr-un pachet ce s-a primit
                received_packet = Packet()
                received_packet.unpack(data)
                self.gui.write_text(received_packet.to_string())
                if received_packet.message_type == Packet.DHCPDISCOVER:
                    self.gui.write_to_terminal("[CLIENT] Received DISCOVER???")
                    print("[CLIENT] Received DISCOVER???")
                elif received_packet.message_type == Packet.DHCPOFFER:
                    self.gui.write_to_terminal("[CLIENT] Received DHCPOFFER")
                    print("[CLIENT] Received DHCPOFFER")
                    self.received_offer_event.set()
                    # trebuie citit continutul offer-ului si folosit
                    try:
                        self.storage.put(received_packet)
                    except TimeoutError:
                        print("Fatal error: Storage is full!")  # Nu ar trebui sa se intample, dar 'just in case'
                    threading.Thread(target=self.process_offer).start()
                elif received_packet.message_type == Packet.DHCPACK:
                    self.gui.write_to_terminal("[CLIENT] Received DHCPACK")
                    print("[CLIENT] Received DHCPACK")
                    threading.Thread(target=self.process_ack, args=[received_packet]).start()

    def prepare_discover(self, discover: Packet):
        self.prepared_discover = discover

    def discover(self):
        # try to implement binary exponential backoff algorithm
        # renunt la backoff pentru ca face probleme cu threading
        # mai exact, threadul principal are prioritate peste cel de receive, asa ca back-off-ul merge la infinit
        # counter = 0
        if self.prepared_discover is None:
            pack_discover = get_discover()
        else:
            pack_discover = self.prepared_discover
        self.xid = pack_discover.xid
        self.mac = pack_discover.client_hardware_address
        self.received_offer_event.clear()
        # print('discover inainte')
        # print(self.xid)
        # print(self.mac)
        # while counter < MAX_COUNT and not self.received_offer_event.isSet():
        #     self.socket.sendto(pack_discover.pack(), ("<broadcast>", self.destination_port))
        #     # self.xid = pack_discover.xid
        #     # self.mac = pack_discover.client_hardware_address
        #     # print('discover dupa')
        #     # print(self.xid)
        #     # print(self.mac)
        #     self.gui.write_to_terminal("[CLIENT] Sent DHCPDISCOVER, waiting for DHCPOFFER")
        #
        #     # time.sleep nu putea fi intrerupt; daca se ajungea la valori mai mari in counter, se statea mult degeaba
        #     counter += 1
        #     self.received_offer_event.wait((2 << counter) + random.randint(-1, 1))
        #
        # if counter == MAX_COUNT:
        #     self.gui.write_to_terminal("Tried 5 times!")
        #     # self.handle_discovery_failure()
        # else:
        #     self.received_offer_event.clear()
        #     # self.process_offer()

        self.socket.sendto(pack_discover.pack(), ("<broadcast>", self.destination_port))
        # self.received_offer_event.wait(10)
        # self.received_offer_event.clear()
        # self.process_offer()

    def handle_discovery_failure(self):

        self.discover_timeout = min(self.discover_timeout * 2, self.max_discover_timeout)

        # testing purposes
        if self.discover_timeout == self.max_discover_timeout:
            self.discover_timeout = self.initial_discover_timeout
            raise TimeoutError
        # sleep before send another discover message
        time.sleep(self.discover_timeout)

        # send another message
        self.discover()

    def process_offer(self):

        received_pack = self.storage.get()

        # reset discover timeout
        self.discover_timeout = self.initial_discover_timeout

        # am rezolvat problema cu mac ul :)) de retinut - trebuie lucrat cu self.client_hardware_address, nu self.mac:))
        if received_pack.client_hardware_address != self.mac:
            print('iesit la mac')
            return False
        # check if offer is valid
        if received_pack.xid != self.xid:
            print('iesit la xid')
            return False

        # OFFER message transmit to client your_ip and server_ip
        # your_ip nu e folosit decat de server
        # self.your_ip = received_pack.your_ip
        self.server_identifier = received_pack.server_ip

        self.send_request(received_pack)

    def send_request(self, packet_offer_receive):

        packet_request = get_request()
        packet_request.client_hardware_address = packet_offer_receive.client_hardware_address
        packet_request.xid = packet_offer_receive.xid
        # here we need to considerate that case when client want the address chosen by him
        # packet_request.client_ip = packet_offer_receive.your_ip
        # packet_request.your_ip = packet_offer_receive.your_ip
        packet_request.server_ip = packet_offer_receive.server_ip
        packet_request.add_option(Packet.REQUESTED_IP_ADDRESS_OPTION, packet_offer_receive.your_ip)
        packet_request.add_option(Packet.SERVER_IDENTIFIER_OPTION, packet_offer_receive.server_ip)

        self.socket.sendto(packet_request.pack(), ("<broadcast>", 67))
        self.gui.write_to_terminal('[CLIENT] Sent REQUEST')

    def process_ack(self, received_ack: Packet):

        assert int.from_bytes(Packet.IP_ADDRESS_LEASE_TIME_ADDRESS_OPTION, 'big') in received_ack.opt_dict
        self.lease_time = received_ack.opt_dict[int.from_bytes(Packet.IP_ADDRESS_LEASE_TIME_ADDRESS_OPTION, 'big')]
        if int.from_bytes(Packet.RENEWAL_TIME_VALUE_OPTION, 'big') in received_ack.opt_dict:
            self.t1 = received_ack.opt_dict[int.from_bytes(Packet.RENEWAL_TIME_VALUE_OPTION, 'big')]
        else:
            self.t1 = int(self.lease_time / 2)
        if int.from_bytes(Packet.REBINDING_TIME_VALUE_OPTION, 'big') in received_ack.opt_dict:
            self.t2 = received_ack.opt_dict[int.from_bytes(Packet.REBINDING_TIME_VALUE_OPTION, 'big')]
        else:
            self.t2 = int(self.lease_time * 7 / 8)
        # teoretic ar trebui salvate/folosite si celelalte optiuni

        # planificare renew si rebind
        if self.renew_timer is not None:
            self.renew_timer.cancel()
        if self.rebind_timer is not None:
            self.rebind_timer.cancel()
        self.renew_timer = threading.Timer(self.t1, self.send_renew, args=socket.inet_ntoa(received_ack.server_ip)).start()
        self.rebind_timer = threading.Timer(self.t2, self.send_rebind, args=socket.inet_ntoa(received_ack.server_ip)).start()

    def send_renew(self, address):
        request = get_request()
        request.client_hardware_address = self.mac
        request.client_ip = self.your_ip
        request.add_option(Packet.REQUESTED_IP_ADDRESS_OPTION, self.your_ip)

        self.socket.sendto(request.pack(), address)

    def send_rebind(self):
        request = get_request()
        request.client_hardware_address = self.mac
        request.client_ip = self.your_ip
        request.add_option(Packet.REQUESTED_IP_ADDRESS_OPTION, self.your_ip)

        self.socket.sendto(request.pack(), ("<broadcast>", 67))
