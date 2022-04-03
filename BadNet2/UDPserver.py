import socket
import threading
import select
from sys import argv
from random import randint
from client.Utility import utilFunctions as util
from client.Badnet import BadNet2 as badnet


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
TIMEOUT = 0.1


# Handle every client request in a separate thread. Dynamically create new sockets bound to new ports.
def handle_client(data, addr):

    # Generate a new random port
    port = randint(10000, 15000)

    # Create a new socket
    temp_addr = (SERVER_IP, port)
    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_sock.bind(temp_addr)
    byte_port = str(port).encode(FORMAT)

    # Send new port to client
    temp_sock.sendto(byte_port, (addr))

    print(f"Receiving file: {data.decode(FORMAT)}")
    file_name = data.strip()

    # Open the file in 'write-byte' mode
    f = open(file_name, 'wb')

    while True:

        # Useful for indicating whether there is some data being transmitted to the socket
        ready = select.select([temp_sock], [], [], TIMEOUT)

        if ready[0]:
            rcvPacket, (client_IP, client_port) = temp_sock.recvfrom(PACKET_SIZE)

            # Corrupted data, i.e flipped bits or duplication
            while (util.iscorrupt(rcvPacket)):

                # send negative acknowlegment to client
                nak = util.makePkt(util.genChecksum(b'0'), b'0')
                badnet.BadNet.transmit(temp_sock, nak, client_IP, client_port)
                rcvPacket, (client_IP, client_port) = temp_sock.recvfrom(PACKET_SIZE)

            # No bits were flipped, sending positive acknowledgment to client
            ack = util.makePkt(util.genChecksum(b"1"), b'1')
            badnet.BadNet.transmit(temp_sock, ack, client_IP, client_port)

            # Writing to file
            data = util.extractData(rcvPacket)
            f.write(data)

        else:
            print(f"Finished receiving {file_name} from [{addr}]")
            f.close()
            temp_sock.close()
            break


def start():

    # Socket for server
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(ADDR)

    print(f"[{SERVER_IP}]: Server is listening on PORT {PORT}")

    while True:
        # Blocking UDP Code (waiting for client to send packets)
        rcvPacket, (client_IP, client_port) = server.recvfrom(PACKET_SIZE)

        # Bits were flipped
        while (util.iscorrupt(rcvPacket)):

            # Send negative acknowlegment to client
            nak = util.makePkt(util.genChecksum(b'0'), b'0')
            badnet.BadNet.transmit(server, nak, client_IP, client_port)
            rcvPacket, (client_IP, client_port) = server.recvfrom(PACKET_SIZE)

        # No bits were flipped, sending positive acknowledgment to client
        ack = util.makePkt(util.genChecksum(b'1'), b'1')
        badnet.BadNet.transmit(server, ack, client_IP, client_port)

        data = util.extractData(rcvPacket)

        # Handle each client in a separate thread
        thread = threading.Thread(target=handle_client, args=(data, (client_IP, client_port)))
        thread.start()


start()
