import socket
import threading
import select
from sys import argv, exit
from client.Badnet import BadNet1 as badnet
from client.Utility import utilFunctions as util

# Accepting valid command line arguments
if len(argv) < 2:
    print("Usage: python UDPserver.py {PORT}")
    exit()

# Initializing constants
PORT = int(argv[1])
SERVER_IP = socket.gethostbyname(socket.gethostname())
PACKET_SIZE = 1024
ADDR = (SERVER_IP, PORT)
FORMAT = 'utf-8'
FILE_SIZE = 2044
DATA_BUFF = [0] * FILE_SIZE
length = 0

# Socket for server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(ADDR)


def handle_client(packet, addr):
    """Handle each client requests"""
    global length
    client_IP = addr[0]
    client_port = addr[1]

    # Send ack
    ack = util.make_ack(packet)
    badnet.BadNet.transmit(server, ack, client_IP, client_port)

    seq_no, data = util.extract(packet)

    
    # DATA_BUFF[seq_no] = data
    # length += 1

    print(f"Receiving file: {data.decode(FORMAT)}")
    file_name = data.strip()

    while True:

        recv_pkt, addr = server.recvfrom(PACKET_SIZE)

        try:
            recv_pkt.decode(FORMAT) != "!DISCONNECT"

            print(f"Finished receiving {file_name} from [{addr}]")
            break
        
        except:
            seq_no, data = util.extract(recv_pkt)
            
            # If the packet is not a duplicate
            if DATA_BUFF[seq_no] == 0:
                
                # Insert into data buffer
                DATA_BUFF[seq_no] = data
                length += 1
  
            # Discard duplicate packet
            else:
                pass

            # Send ack
            ack = util.make_ack(recv_pkt)
            badnet.BadNet.transmit(server, ack, client_IP, client_port)
    
    write_file(file_name)
    
def write_file(file_name):
    
    # Open the file in 'write-byte' mode
    with open(file_name, 'wb') as f:

        for index in range(1, length):
            
            if DATA_BUFF[index] != 0:
                f.write(DATA_BUFF[index])
    


def start():

    print(f"[{SERVER_IP}]: Server is listening on PORT {PORT}")

    while True:
        
        # Blocking UDP Code (waiting for client to send packets)
        rcv_packet, addr = server.recvfrom(PACKET_SIZE)

        # Handle client requests
        handle_client(rcv_packet, addr)




start()
