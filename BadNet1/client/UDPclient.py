import socket
from struct import pack
from sys import argv, exit
from Badnet import BadNet1 as badnet
import time
import select
from Utility import utilFunctions as util
from queue import Queue

# Accepting valid command line arguments
if len(argv) < 3:
    print("Usage: python UDPclient.py {PORT} {FILENAME}")
    exit()

# Initializing constants
PORT = int(argv[1])
SERVER_IP = socket.gethostbyname(socket.gethostname())
PACKET_SIZE = 1024
DATA_SIZE = 980
ADDR = (SERVER_IP, PORT)
FORMAT = 'utf-8'
FILE_NAME = argv[2]
TIMEOUT = 0.01
packets = {}

def check_for_acks():
    
    # Useful for indicating whether there is some data being transmitted to the socket
    ready = select.select([client], [], [], TIMEOUT)

    if ready[0]:
        recv_pkt, addr = client.recvfrom(PACKET_SIZE)
        seq_no = util.extract_seq(recv_pkt)

        packets.pop(seq_no)
        


# Socket for client
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"Sending file {FILE_NAME}...")
data = FILE_NAME.encode(FORMAT)

packet = util.make_pkt(data)
seq_no = util.extract_seq(packet)

badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)

packets[seq_no] = packet

# Open the local file in 'read-byte' mode
f = open(FILE_NAME, 'rb')

# Read chunks of size equal to the size of the buffer, in this case the packet size.
data = f.read(DATA_SIZE)

# File transfer over the server port.
while data:
    
    check_for_acks()

    packet = util.make_pkt(data)
    seq_no = util.extract_seq(packet)
    
    badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)

    # Sender keeping a buffer of sent but unacknowledged packets
    packets[seq_no] = packet

    data = f.read(DATA_SIZE)
    # time.sleep(0.1)

check_for_acks()

while len(packets) != 0: 
    tuple_ = packets.popitem()
    seq_no = tuple_[0]
    packet = tuple_[1]
    packets[seq_no] = packet
    badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)
    check_for_acks()


# badnet.BadNet.transmit(client, "!DISCONNECT".encode(FORMAT), SERVER_IP, PORT)
client.sendto("!DISCONNECT".encode(FORMAT), (SERVER_IP, PORT))

# Closing the socket and the file
client.close()
f.close()


