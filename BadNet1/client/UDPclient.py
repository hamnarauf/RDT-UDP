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
TIMEOUT = 0.001
packets = {}

def check_for_acks():
    
    # Useful for indicating whether there is some data being transmitted to the socket
    ready = select.select([client], [], [], TIMEOUT)

    if ready[0]:
        recv_pkt, addr = client.recvfrom(PACKET_SIZE)
        seq_no = util.extract_seq(recv_pkt)

        packets.pop(seq_no, None)
        

# Socket for client
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"Sending file {FILE_NAME}...")
data = FILE_NAME.encode(FORMAT)

packet, seq_no = util.make_pkt(data)

badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)

packets[seq_no] = packet

# Open the local file in 'read-byte' mode
f = open(FILE_NAME, 'rb')

# Read chunks of size equal to the size of the buffer, in this case the packet size.
data = f.read(DATA_SIZE)

# File transfer over the server port.
while data:
    
    # Pop packets for dictionary if ack has been received
    check_for_acks()

    # Make a new packet from the file
    packet, seq_no = util.make_pkt(data)

    badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)

    # Sender keeps a buffer of sent but unacknowledged packets
    packets[seq_no] = packet

    data = f.read(DATA_SIZE)
    # time.sleep(0.01)

# Check for acks again after making all the packets from file
check_for_acks()

# Keep sending unacknowledged packets until the dictionary is not empty.
while len(packets) != 0: 
    tuple_ = packets.popitem()
    seq_no = tuple_[0]
    packet = tuple_[1]
    packets[seq_no] = packet
    badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)
    check_for_acks()

# Make finish packet
finish, seq_no = util.make_pkt(finish=True)

# Insert into dictionary
packets[seq_no] = finish

# Keep sending finish packets until its ack is received.
while len(packets) != 0: 
    badnet.BadNet.transmit(client, finish, SERVER_IP, PORT)
    check_for_acks()
    # time.sleep(0.05)

# Closing the socket and the file
client.close()
f.close()


