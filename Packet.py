import random
import socket
#constantele utilizate pentru a realiza pachetul
#op
REQUEST=b'\x01'
REPLY=b'\x02'

#htype=1 hardware type-ethernet
HTYPE=b'\x01'

#hlen=6 hardware address length
HLEN=b'\x06'

#magic cookie care va aparea in fata campului de optiuni daca acestea exista
MAGIC_COOKIE=b'\x63\x82\x53\x63'

#pentru posibilitatea de a avea optiunea 53
DHCPDISCOVER=1
DHCPOFFER=2
DHCPREQUEST=3
DHCPDECLINE=4
DHCPACK=5
DHCPNAK=6
DHCPRELEASE=7
DHCPINFORM=8

#pentru a putea afisa mai usor tipul mesajelor
TIP_MESAJ=("","DHCPDISCOVER",
           "DHCPOFFER",
           "DHCPREQUEST",
           "DHCPDECLINE",
           "DHCPACK",
           "DHCPNAK",
           "DHCPRELEASE",
           "DHCPINFORM")



class Packet(object):

    def __init__(self,MESSAGE_TYPE,XID,CHADDR,YIADDR,SIADDR,CIADDR,GIADDR):

        bxid = bytes.fromhex(hex(XID)[2:].zfill(8))
        bchaddr = bytes.fromhex(hex(CHADDR)[2:].zfill(12))

        self.broadcast=0
        self.HOPS=b'\x00'   #hops initializat cu 0
        self.XID = bxid     #xid initializat cu un numar random
        self.SECS=b'\x00\x00'

        #cele 4 adrese sunt initializate cu 0
        self.CIADDR = b'\x00\x00\x00\x00'
        self.YIADDR = b'\x00\x00\x00\x00'
        self.SIADDR = b'\x00\x00\x00\x00'
        self.GIADDR = b'\x00\x00\x00\x00'

        self.CHADDR=bchaddr
        self.SNAME=b'\x00'*64 #server name
        self.FILE=b'\x00'*128 #boot filename
        self.MESSAGE=None #acest camp se va actualiza in functie de optiunile alese de client din interfata

        self.modificari(MESSAGE_TYPE,YIADDR,SIADDR,CIADDR,GIADDR)
        self.pack=self.impachetare()
        self.desp=self.despachetare(self.pack)
        self.to_string(MESSAGE_TYPE)



    def impachetare(self)->list[bytes]:
        packet = [self.OP,
                  HTYPE,
                  HLEN,
                  self.HOPS,
                  self.XID,
                  self.SECS,
                  self.FLAGS,
                  self.CIADDR,
                  self.YIADDR,
                  self.SIADDR,
                  self.GIADDR,
                  self.CHADDR,
                  self.SNAME,
                  self.FILE,
                  MAGIC_COOKIE]
        print(packet)
        return packet

    def despachetare(self,packet:bytes)->dict[str:bytes]:

        packet_despachetat={'OP':packet[0:1],
                            'HTYPE':packet[1:2],
                            'HLEN':packet[2:3],
                            'HOPS':packet[3:4],
                            'XID':packet[4:5],
                            'SECS':packet[5:6],
                            'FLAGS':packet[6:7],
                            'CIADDR':packet[7:8],
                            'YIADDR':packet[8:9],
                            'SIADDR':packet[9:10],
                            'GIADDR':packet[10:11],
                            'CHADDR':packet[11:12],
                            'SNAME':packet[12:13],
                            'FILE':packet[13:14],
                            'COOKIE':packet[14:15]}
        print(packet_despachetat)
        return packet_despachetat

    def modificari(self,message_type,yiaddr_address,siaddr_address,ciaddr_address,giaddr_address):

        yiaddr=socket.inet_aton(yiaddr_address)
        siaddr=socket.inet_aton(siaddr_address)
        ciaddr=socket.inet_aton(ciaddr_address)
        giaddr=socket.inet_aton(giaddr_address)

        if (message_type == DHCPDISCOVER or message_type == DHCPREQUEST):
            self.broadcast = 1

        if (self.broadcast):
            self.FLAGS = b'\x80\x00'
        else:
            self.FLAGS = b'\x00\x00'

        # dam valoare parametrului opcode

        if (message_type == DHCPDISCOVER or + \
                message_type == DHCPREQUEST or + \
                message_type == DHCPDECLINE or + \
                message_type == DHCPRELEASE or + \
                message_type == DHCPINFORM):
            self.OP = REQUEST
        elif (message_type == DHCPOFFER or + \
                message_type == DHCPACK or + \
                message_type == DHCPNAK):
            self.OP = REPLY
        else:
            raise Exception("Mesaj DHCP necunoscut!!")

        if(message_type==DHCPINFORM):
            self.CIADDR=ciaddr
        elif(message_type==DHCPOFFER):
            self.YIADDR=yiaddr
            #self.SIADDR=siaddr  #acesta va veni prin optiune
        #elif(message_type==DHCPREQUEST):
        #    self.SIADDR=siaddr
        #    self.GIADDR=giaddr
        elif(message_type==DHCPACK):
            #self.CIADDR=ciaddr
            self.YIADDR=yiaddr
            #self.SIADDR=siaddr
        elif(message_type==DHCPNAK):
            self.GIADDR=giaddr
        elif(message_type==DHCPRELEASE):
            self.CIADDR=ciaddr



    #pentru afisarea pe interfata clientului
    def to_string(self,MESSAGE_TYPE):

        print(f"Tipul mesajului este {MESSAGE_TYPE}-{TIP_MESAJ[MESSAGE_TYPE]}")
        int_op=int.from_bytes(self.OP,"big")
        print(f"Opcode={int_op}")
        int_htype = int.from_bytes(HTYPE, "big")
        print(f"Htype={int_htype}")
        int_hlen = int.from_bytes(HLEN, "big")
        print(f"Hlen={int_hlen}")
        int_hops = int.from_bytes(self.HOPS, "big")
        print(f"Hops={int_hops}")
        int_xid=int.from_bytes(self.XID,"big")
        print(f"Xid={int_xid}")
        int_secs = int.from_bytes(self.SECS, "big")
        print(f"Xid={int_secs}")
        print(f"Flags={self.FLAGS}")
        print(f"Ciaddr={socket.inet_ntoa(self.CIADDR)}")
        print(f"Yiaddr={socket.inet_ntoa(self.YIADDR)}")
        print(f"Siaddr={socket.inet_ntoa(self.SIADDR)}")
        print(f"Giaddr={socket.inet_ntoa(self.GIADDR)}")
        chaddr=self.CHADDR.hex(":")
        print(f"Chaddr={chaddr}")
        #aceste doua campuri sunt provizorii pana vom adauga date
        int_sname=int.from_bytes(self.SNAME,"big")
        print(f"Sname={int_sname}")
        int_file=int.from_bytes(self.FILE,"big")
        print(f"File={int_file}")
        #cand vom adauga date
        #sname=self.SNAME.decode("ascii")
        #print(f"Sname={sname}")
        #file=self.FILE.decode("ascii")
        #print(f"File={file}")
        print(f"Magic cookie={socket.inet_ntoa(MAGIC_COOKIE)}")





def gen_xid():
    return random.randint(1, 0xffffffff)

if __name__=="__main__":
    packet1=Packet(DHCPOFFER,gen_xid(),0xf34a93dc2116,'168.162.30.1','30.20.12.12','15.16.62.12','150.162.13.25')




