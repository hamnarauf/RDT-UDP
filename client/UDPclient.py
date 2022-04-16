import socket
from sys import argv, exit
from Badnet import BadNet5 as badnet
import time
import select
from Utility import utilFunctions as util
import multiprocessing as mp
from os.path import exists as file_exists


# Each process is spawned with copies of these values.
TIMEOUT = 0.001
PACKET_SIZE = 1024
PORT = int(argv[1])
SERVER_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER_IP, PORT)


def retransmit_pkts(client, packets):
    '''
    Function to retransmit packets in case of loss/error

    Parameters:
    client(socket): Client socket
    packets(dictionary): Buffer of all unacknowleged packets
      
    '''
    while True:
        
        # Useful for indicating whether there is some data being transmitted to the socket
        ready = select.select([client], [], [], TIMEOUT)
        
        keys = packets.keys()

        if not ready[0] and len(keys) > 0:
            o_unack = keys[0]
            packet = packets.pop(o_unack)

            # Transmit packet
            badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)

            # Re-insert into dictionary
            packets[o_unack] = packet


def check_for_acks(client, packets):
    '''
    Function to check for ack messages and let the sender know not to re-transmit correctly received packets.

    Parameters:
    client(Socket): Client socket
    packets(Dictionary): Buffer of all unacknowleged packets
    
    '''

    while True:

        recv_pkt, addr = client.recvfrom(PACKET_SIZE)

        # If ack is received pop packet of this seqeuence number
        if not util.iscorrupt(recv_pkt):
            seq_no = util.extract_seq(recv_pkt)
            packets.pop(seq_no, None)


# Main process
if __name__ == '__main__':
    start = time.perf_counter()
    
    # Accepting valid command line arguments
    if len(argv) < 3:
        print("Usage: python UDPclient.py {PORT} {FILENAME}")
        exit()

    # Initializing constants for main process
    DATA_SIZE = 1018
    FORMAT = 'utf-8'
    FILE_NAME = argv[2]
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Accepting valid filename to transfer
    if not file_exists(FILE_NAME):
        print("File does not exist.")
        exit()

    # Creating a shared dictionary that every process can read/write to. Updates made in one process are reflected
    # across every process    
    manager = mp.Manager() 
    packets = manager.dict() 
    
    # sending file name to server
    print(f"Sending file {FILE_NAME}...")
    data = FILE_NAME.encode(FORMAT)
    packet, seq_no = util.make_pkt(data)
    badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)
    packets[seq_no] = packet

    # Spawning two processes, one for checking acks, one for re-transmitting packets if required.
    # The two processes run in parallel with the main process.
    p1 = mp.Process(target=check_for_acks, args=(client,packets))
    p1.start()

    p2 = mp.Process(target=retransmit_pkts, args=(client,packets))
    p2.start()
    
    # Open the local file in 'read-byte' mode
    f = open(FILE_NAME, 'rb')

    # Read chunks of size equal to the DATA_SIZE
    data = f.read(DATA_SIZE)

    # File transfer over the server port.
    while data:
   
        # Make a new packet from the file and transmit to server
        packet, seq_no = util.make_pkt(data)
        badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)

        # Sender keeps a buffer of sent but unacknowledged packets
        packets[seq_no] = packet

        data = f.read(DATA_SIZE)
    
    # Closing the file
    f.close()

    # Hold off client from sending finish packet until all prev packets have been correctly acknowleged
    while len(packets) > 0:
        pass
    

    # Make finish packet
    finish, finish_seq = util.make_pkt(finish=True)

    # Insert into dictionary
    packets[finish_seq] = finish

    badnet.BadNet.transmit(client, finish, SERVER_IP, PORT)

    # Hold off client from terminating until finish packet has been correctly acknowledged.
    while len(packets) > 0:
        pass


    # Terminating the processes
    p1.terminate()
    p2.terminate()
    
    # Closing the socket
    client.close()
    
    end = time.perf_counter()
    print(f"Finished in {round(end-start, 2)} second(s)")