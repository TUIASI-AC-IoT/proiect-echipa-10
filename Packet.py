import socket
import random
import struct

# pentru a putea afisa mai usor tipul mesajelor
TIP_MESAJ = ("", "DHCPDISCOVER",
             "DHCPOFFER",
             "DHCPREQUEST",
             "DHCPDECLINE",
             "DHCPACK",
             "DHCPNAK",
             "DHCPRELEASE",
             "DHCPINFORM")


def generate_mac():
    mac = "".join(random.choice("abcdef0123456789") for _ in range(0, 12))
    return mac


def mac_to_bytes(mac):
    while len(mac) < 12:
        mac = '0' + mac
    macB = b''
    for i in range(0, 12, 2):
        m = int(mac[i:i + 2], 16)
        macB += m.to_bytes(1, 'big')
    return macB


class BOOTPHeader(object):
    REQUEST = b'\x01'
    REPLY = b'\x02'

    def __init__(self, opcode, mac):
        # initializare parametri pachet

        self.opcode = opcode
        self.hardware_type = b'\x01'
        self.hardware_address_length = b'\x06'
        self.hops = b'\x00'
        self.xid = self.gen_xid()
        self.seconds = b'\x00\x00'
        self.flags = b'\x80\x00'
        self.client_ip = b'\x00\x00\x00\x00'
        self.your_ip = b'\x00\x00\x00\x00'
        self.server_ip = b'\x00\x00\x00\x00'
        self.gateway_ip = b'\x00\x00\x00\x00'
        self.client_hardware_address = mac + b'\x00' * 10  # 10 octeti padding
        self.server_host_name = b'\x00' * 64
        self.boot_filename = b'\x00' * 128  # boot filename
        self.options = ''  # acest camp se va actualiza in functie de optiunile alese de client din interfata

    def gen_xid(self):
        return random.getrandbits(32).to_bytes(4, 'big')

    def pack(self):
        return (self.opcode + self.hardware_type + self.hardware_address_length +
                self.hops + self.xid + self.seconds + self.flags + self.client_ip + self.your_ip +
                self.server_ip + self.gateway_ip + self.client_hardware_address + self.server_host_name +
                self.boot_filename + self.options)


class Packet(BOOTPHeader):
    # tipurile de mesaj
    DHCPDISCOVER = b'\x01'
    DHCPOFFER = b'\x02'
    DHCPREQUEST = b'\x03'
    DHCPDECLINE = b'\x04'
    DHCPACK = b'\x05'
    DHCPNAK = b'\x06'
    DHCPRELEASE = b'\x07'
    DHCPINFORM = b'\x08'

    # optiunile disponibile
    SUBNET_MASK_OPTION = b'\x01'
    ROUTER_OPTION = b'\x03'
    DOMAIN_NAME_SERVER_OPTION = b'\x06'
    REQUESTED_IP_ADDRESS_OPTION = b'\x32'
    IP_ADDRESS_LEASE_TIME_ADDRESS_OPTION = b'\x33'
    DHCP_MESSAGE_TYPE_OPTION = b'\x35'
    SERVER_IDENTIFIER_OPTION = b'\x36'
    PARAMETER_REQUESTED_LIST_OPTION = b'\x37'
    RENEWAL_TIME_VALUE_OPTION = b'\x3a'
    REBINDING_TIME_VALUE_OPTION = b'\x3b'
    END_OPTION = b'\xff'

    def __init__(self):

        self.message_type = self.DHCPDISCOVER
        self.mac = mac_to_bytes(generate_mac())

        # dam valoare parametrului opcode

        if (self.message_type == self.DHCPOFFER or self.message_type == self.DHCPACK or self.message_type == self.DHCPNAK):
            opcode = BOOTPHeader.REPLY
        else:
            opcode = BOOTPHeader.REQUEST

        super(Packet, self).__init__(opcode, self.mac)
        self.option_list = []

        self.add_option(self.DHCP_MESSAGE_TYPE_OPTION, self.message_type)

    def add_option(self, option, *args):
        value = b''
        length = 0
        for i in args:
            length += len(i)
            value += i
        if length > 0:
            length = bytes([length])
        else:
            length = b''
        self.option_list.append(option + length + value)

    def pack(self):
        self.add_option
        self.options = b'\x63\x82\x53\x63'  # Magic cookie
        print(self.options)

        self.options += b''.join(self.option_list)
        print(self.options)

        # Adauga la sfarsit optiunea END

        self.options += Packet.END_OPTION
        print(self.options)
        return super(Packet, self).pack()

    def unpack(self, data):
        self.opcode, self.hardware_type, self.hardware_address_length, \
        self.hops, self.xid, self.seconds, self.flags, self.client_ip, \
        self.your_ip, self.server_ip, self.gateway_ip, self.client_hardware_address, \
        self.server_host_name, self.boot_filename, self.options \
            = struct.unpack('cccc4s2s2s4s4s4s4s16s64s128s' + str(len(data) - 236) + 's', data)

        self.opt_dict = {}
        idx = 4

        while True:
            try:
                op_code = self.options[idx]
                if op_code == 255:
                    self.opt_dict[op_code] = ''
                    break
                op_len = self.options[idx + 1]
                op_data = self.options[idx + 2:idx + 2 + op_len]
                idx = idx + 2 + op_len
                self.opt_dict[op_code] = op_data
            except IndexError:
                break

    #function for DHCPOFFER
    def create_offer_packet(self, offered_ip, server_ip, xid, mac, lease_time,options):
        self.opcode = Packet.DHCPOFFER
        self.xid = xid
        self.client_ip = b'\x00\x00\x00\x00'
        self.your_ip = bytes(offered_ip,'utf-8')
        self.server_ip = bytes(server_ip,'utf-8')
        self.client_hardware_address = mac + b'\x00' * 10

        self.options = Packet.DHCP_MESSAGE_TYPE_OPTION + b'\x01' + Packet.DHCPOFFER

        self.options += Packet.SERVER_IDENTIFIER_OPTION + b'\x04' + bytes(server_ip,'utf-8')

        self.options += Packet.IP_ADDRESS_LEASE_TIME_ADDRESS_OPTION + b'\x04' + lease_time.to_bytes(4, 'big')

        self.options += options

        self.options += b'\xff'

        return self.pack()

    #function for client to request a specific address
    def request_specific_address(self, requested_ip: str) -> None:

        requested_ip_bytes = socket.inet_aton(requested_ip)
        self.options += Packet.REQUESTED_IP_ADDRESS_OPTION + b'\x04' + requested_ip_bytes

    # for print to interface
    def to_string(self):

        str = ""
        int_op = int.from_bytes(self.opcode, "big")
        str += f"Opcode={int_op}" + "\n"

        int_htype = int.from_bytes(self.hardware_type, "big")
        str += f"Hardware type={int_htype}" + "\n"

        int_hlen = int.from_bytes(self.hardware_address_length, "big")
        str += f"Hardware address length{int_hlen}" + "\n"

        int_hops = int.from_bytes(self.hops, "big")
        str += f"Hops={int_hops}" + "\n"

        int_xid = int.from_bytes(self.xid, "big")
        str += f"Xid={int_xid}" + "\n"

        int_secs = int.from_bytes(self.seconds, "big")
        str += f"Xid={int_secs}" + "\n"

        str += f"Flags={self.flags}" + "\n"

        str += f"Ciaddr={socket.inet_ntoa(self.client_ip)}" + "\n"
        str += f"Yiaddr={socket.inet_ntoa(self.your_ip)}" + "\n"
        str += f"Siaddr={socket.inet_ntoa(self.server_ip)}" + "\n"
        str += f"Giaddr={socket.inet_ntoa(self.gateway_ip)}" + "\n"

        chaddr = self.client_hardware_address.hex(":")
        str += f"Chaddr={chaddr}" + "\n"

        # aceste doua campuri sunt provizorii pana vom adauga date
        int_sname = int.from_bytes(self.server_host_name, "big")
        # print(f"Sname={int_sname}")
        int_file = int.from_bytes(self.boot_filename, "big")
        # print(f"File={int_file}")

        # sname=self.server_host_name.decode("ascii")
        # print(f"Sname={sname}")
        # file=self.boot_filename.decode("ascii")
        # print(f"File={file}")

        return str
