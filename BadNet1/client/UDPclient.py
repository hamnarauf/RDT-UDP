import socket
from sys import argv, exit
from Badnet import BadNet5 as badnet
import time
import select
from Utility import utilFunctions as util

# Accepting valid command line arguments
if len(argv) < 3:
    print("Usage: python UDPclient.py {PORT} {FILENAME}")
    exit()

# Initializing constants
PORT = int(argv[1])
SERVER_IP = socket.gethostbyname(socket.gethostname())
PACKET_SIZE = 1024
DATA_SIZE = 1018
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
     
        if not util.iscorrupt(recv_pkt):
            seq_no = util.extract_seq(recv_pkt)
            print(f"Received packet {seq_no}")
            pop = packets.pop(seq_no, None)
            if pop == None:
                print(f"Popped NONE")
            else:
                print(f"Popping packet {seq_no}")
            return True
        else:
            print("CORRUPTED PACKET")

# Open the local file in 'read-byte' mode
f = open(FILE_NAME, 'rb')

# Socket for client
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"Sending file {FILE_NAME}...")
data = FILE_NAME.encode(FORMAT)

packet, seq_no = util.make_pkt(data)

badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)

packets[seq_no] = packet


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

# Closing the file
f.close()
# Check for acks again after making all the packets from file
check_for_acks()

print("\n\n\n\nGOING INTO 2nd WHILE LOOP NOW\n\n\n\n\n")

# Keep sending unacknowledged packets until the dictionary is not empty.
while len(packets) != 0: 

    for packet in list(packets.values()):
        badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)
        print('\n\n\n')
        print(f"Sending packet {util.extract_seq(packet)}")
        check_for_acks()


print("\n\n\n\n\n")
print("SENDING FINISH PACKET NOW")
print(packets)

# Make finish packet
finish, finish_seq = util.make_pkt(finish=True)

# Insert into dictionary
packets[finish_seq] = finish

print(f'Sequence number of finish packet is {util.extract_seq(finish)}')
print(packets)
print("\n\n\n\n\n")

# Keep sending finish packets until its ack is received.
while len(packets) != 0: 
    print(f'Sending finish packet {util.extract_seq(finish)}')
    badnet.BadNet.transmit(client, finish, SERVER_IP, PORT)
    if check_for_acks():
        break

# Closing the socket
client.close()