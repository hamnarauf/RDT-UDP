import socket
from sys import argv, exit
import time
from Badnet import BadNet2 as badnet
from Utility import utilFunctions as util



# Accepting valid command line arguments
if len(argv) < 3:
    print("Usage: python UDPclient.py {PORT} {FILENAME}")
    exit()

# Initializing constants
PORT = int(argv[1])
SERVER_IP = socket.gethostbyname(socket.gethostname())
PACKET_SIZE = 1024
DATA_SIZE = 800
ADDR = (SERVER_IP, PORT)
FORMAT = 'utf-8'
FILE_NAME = argv[2]


# Socket for client
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sending file name
print(f"Sending file {FILE_NAME}...")
data = FILE_NAME.encode(FORMAT)
packet = util.makePkt(util.genChecksum(data), data )
badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)

# Wait for ack from server
rcvPkt, ADDR = client.recvfrom(PACKET_SIZE)
while(util.iscorrupt(rcvPkt) or not util.isAck(rcvPkt)):
    badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)
    rcvPkt, ADDR = client.recvfrom(PACKET_SIZE)


# Wait for server to send new temporary port
data, ADDR = client.recvfrom(PACKET_SIZE)

# Re-assign new values
SERVER_IP = ADDR[0]
PORT = ADDR[1]

# Open the local file in 'read-byte' mode
f = open(FILE_NAME, 'rb')

# Read chunks of file
data = f.read(DATA_SIZE)

# File transfer over the new port.
while data:
    # sending data
    packet = util.makePkt(util.genChecksum(data), data)
    badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)
    
    # wait for ack from server
    rcvPkt, ADDR = client.recvfrom(PACKET_SIZE)
    while(util.iscorrupt(rcvPkt) or not util.isAck(rcvPkt)):
        print("Retransmission")

        badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)
        rcvPkt, ADDR = client.recvfrom(PACKET_SIZE)
    
    data = f.read(DATA_SIZE)

# Closing the socket and the file
client.close()
f.close()