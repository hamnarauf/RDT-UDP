import socket
from sys import argv, exit
from client.Badnet import BadNet5 as badnet
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
FILE_SIZE = 2061
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

    if not util.iscorrupt(packet):
        
        # Extract contents of packet
        seq_no, data = util.extract(packet)

        print(f"Received {seq_no}")
        
        # If the sent packet is a finish request
        if util.is_finish(packet):
            ack = util.make_ack(seq_no)
            print(f'Sending ack of FINISH1 packet {util.extract_seq(ack)}')
            badnet.BadNet.transmit(server, ack, client_IP, client_port)
            return

        # Send ack
        ack = util.make_ack(seq_no)

        badnet.BadNet.transmit(server, ack, client_IP, client_port)
        print(f'Sending ack of packet {util.extract_seq(ack)}')

        DATA_BUFF[seq_no] = data
        length += 1


    while True:

        recv_pkt, addr = server.recvfrom(PACKET_SIZE)

        if not util.iscorrupt(recv_pkt):
            seq_no, data = util.extract(recv_pkt)

            print(f"Received {seq_no}")

            if util.is_finish(recv_pkt):

                ack = util.make_ack(seq_no)
                badnet.BadNet.transmit(server, ack, client_IP, client_port)
                print(f'Sending ack of FINISH2 packet {util.extract_seq(ack)}')
                print(f"Disconnecting from client [{addr}]")
                break
            
            else:
                # If the packet is not a duplicate
                if DATA_BUFF[seq_no] == 0:
                    
                    # Insert into data buffer
                    DATA_BUFF[seq_no] = data
                    length += 1
    
                # Discard duplicate packet
                else:
                    pass

                # Send ack
                ack = util.make_ack(seq_no)
                badnet.BadNet.transmit(server, ack, client_IP, client_port)
                print(f'Sending ack of packet {util.extract_seq(ack)}')
    
    write_file()
    length = 0    

def write_file():
    
    global DATA_BUFF

    name = DATA_BUFF[0]
    print(f"Writing file: {name.decode(FORMAT)}")
    file_name = name.strip()
    
    # Open the file in 'write-byte' mode
    with open(file_name, 'wb') as f:

        for index in range(1, length):
            
            if DATA_BUFF[index] != 0:
                f.write(DATA_BUFF[index])

    print(f"Finished writing file {file_name}")
    DATA_BUFF = [0] * FILE_SIZE

def start():

    
    while True:
        print(f"[{SERVER_IP}]: Server is listening on PORT {PORT}")
        try:
            # Blocking UDP Code (waiting for client to send packets)
            rcv_packet, addr = server.recvfrom(PACKET_SIZE)

            # Handle client requests
            handle_client(rcv_packet, addr)
        except:
            print("CONNECTION ERRORRR")
            pass

start()