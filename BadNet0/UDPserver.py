import socket
import threading
import select
from sys import argv
from random import randint


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

    # Wait for client to send additional packets
    data, addr = temp_sock.recvfrom(PACKET_SIZE)
    
    # Write them into the file
    f.write(data)
    
    while True:
        
        # Useful for indicating whether there is some data being transmitted to the socket
        ready = select.select([temp_sock], [], [], TIMEOUT)
        
        if ready[0]:
            data, addr = temp_sock.recvfrom(PACKET_SIZE)
            f.write(data)

        else:
            print(f"Finished receiving {file_name.decode(FORMAT)} from [{addr}]")
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
        data, addr = server.recvfrom(PACKET_SIZE)
        
        # Handle each client in a separate thread
        thread = threading.Thread(target=handle_client, args=(data, addr))
        thread.start()


start()