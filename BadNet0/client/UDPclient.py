import socket
from sys import argv, exit
from Badnet import BadNet0
import time

# Accepting valid command line arguments
if len(argv) < 3:
    print("Usage: python UDPclient.py {PORT} {FILENAME}")
    exit()

# Initializing constants
PORT = int(argv[1])
SERVER_IP = socket.gethostbyname(socket.gethostname())
PACKET_SIZE = 1024
ADDR = (SERVER_IP, PORT)
FORMAT = 'utf-8'
FILE_NAME = argv[2]

# Socket for client
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
BadNet0.BadNet.transmit(client, FILE_NAME.encode(FORMAT), SERVER_IP, PORT)
print(f"Sending file {FILE_NAME}...")

# Wait for server to send new temporary port
data, ADDR = client.recvfrom(PACKET_SIZE)

# Re-assign new values
SERVER_IP = ADDR[0]
PORT = ADDR[1]

# Open the local file in 'read-byte' mode
f = open(FILE_NAME, 'rb')

# Read chunks of size equal to the size of the buffer, in this case the packet size.
data = f.read(PACKET_SIZE)

# File transfer over the new port.
while data:
    BadNet0.BadNet.transmit(client, data, SERVER_IP, PORT)
    data = f.read(PACKET_SIZE)
    # time.sleep(0.1)

# Closing the socket and the file
client.close()
f.close()