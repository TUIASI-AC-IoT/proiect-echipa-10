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
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Activare optiune refolosire port
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', 67))

        self.socket.setblocking(False)

        # provizoriu - pool de adrese se va lua din interfata
        self.address_pool = ['12.30.0.1', '12.30.0.2', '12.30.0.3']
        self.client_address_mapping = {}

        self.lease_time = 300

        self.running = True

        try:
            self.receive_thread = threading.Thread(target=self.receive_fct)
            self.receive_thread.start()
        except:
            print("Eroare la pornirea thread‐ului")
            sys.exit()

    # problema la server - cand primeste mesaj de REQUEST il trateaza ca cel de DISCOVER
    # aceasta functie cred ca o sa se mai modifice ca am facut o prea incarcata
    def receive_fct(self):
        contor = 0
        while self.running:
            # Apelam la functia sistem IO -select- pentru a verifca daca socket-ul are date in bufferul de receptie
            # Stabilim un timeout de 1 secunda
            r, _, _ = select.select([self.socket], [], [], 10)
            if not r:
                contor = contor + 1
            else:
                self.gui.write_to_terminal("[SERVER] Waiting meesage from client")
                data, address = self.socket.recvfrom(1024)
                packet_receive = Packet()
                packet_receive.unpack(data)
                if packet_receive.message_type == Packet.DHCPDISCOVER:
                    self.gui.write_to_terminal("[SERVER]Received DHCPDISCOVER message")
                    offer_packet = Packet()
                    print("mac")
                    print(packet_receive.client_hardware_address)
                    print("\n\n")
                    # OFFER PACKET cu adrese random - pentru client adresa trebuie luata dintr-un pool de adrese,lease time-ul se va lua
                    # din interfata,trebuie modificata si adresa serverului
                    offer_packet.create_offer_packet(self.choose_address(), (self.socket.getsockname())[0],
                                                     packet_receive.xid, packet_receive.client_hardware_address,
                                                     self.lease_time,
                                                     packet_receive.options)
                    self.socket.sendto(offer_packet.pack(), address)
                    self.gui.write_to_terminal("[SERVER]Send DHCPOFFER message")
                elif packet_receive.message_type == Packet.REQUEST:
                    self.gui.write_to_terminal("[SERVER] Receive REQUEST")
                    self.process_request(packet_receive, address)

    def cleanup(self):
        self.running = False
        print("Waiting for the thread to close...")
        self.receive_thread.join()
        print("Closing socket...")
        self.socket.close()
        print("Cleanup done!")

    def process_request(self, packet_receive, address):

        self.gui.write_to_terminal('[SERVER] Process REQUEST')
        requested_ip = packet_receive.client_ip
        client_mac = packet_receive.mac
        if self.is_address_available(requested_ip):
            self.assign_address(client_mac, requested_ip)
            self.send_ack(packet_receive, address)
        else:
            self.send_nak(packet_receive, address)

    def send_nak(self, packet_receive, address):

        nak_packet = Packet()
        nak_packet.message_type = Packet.DHCPNAK
        nak_packet.xid = packet_receive.xid
        nak_packet.server_ip = packet_receive.server_ip
        nak_packet.client_ip = b'\x00\x00\x00\x00'
        nak_packet.client_hardware_address = packet_receive.client_hardware_address
        nak_packet.options = b'\x35\x01\x06'  # DHCP Message Type Option: NAK
        self.socket.sendto(nak_packet.pack(), address)

    def send_ack(self, packet_receive, address):

        ack_packet = Packet()
        ack_packet.message_type = Packet.DHCPACK
        ack_packet.xid = packet_receive.xid
        ack_packet.client_hardware_address = packet_receive.client_hardware_address
        ack_packet.server_ip = packet_receive.server_ip
        ack_packet.your_ip = packet_receive.client_ip
        ack_packet.options = (Packet.DHCP_MESSAGE_TYPE_OPTION + b'\x01\x05' +
                              Packet.IP_ADDRESS_LEASE_TIME_ADDRESS_OPTION + struct.pack('!I', self.lease_time) +
                              Packet.SERVER_IDENTIFIER_OPTION + packet_receive.server_ip +
                              Packet.END_OPTION
                              )
        self.socket.sendto(ack_packet.pack(), address)

    # choose address from addresss pool - maybe need another way to choose?:))
    def choose_address(self):
        return self.address_pool[0]

    # verificari adresa - daca e disponibila
    def is_address_available(self, address):
        if address in self.address_pool:
            return True
        else:
            return False

    # asignare adresa
    def assign_address(self, mac, address):
        if self.is_address_available(address):
            # scoatem adresa din pool
            self.address_pool.remove(address)
            self.client_address_mapping[mac] = address

            return address
        return None

    # eliberare adresa
    def release_address(self, mac):
        if mac in self.client_address_mapping:
            address = self.client_address_mapping[mac]
            self.address_pool.append(address)

            del self.client_address_mapping[mac]
