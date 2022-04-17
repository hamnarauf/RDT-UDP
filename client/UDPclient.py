import socket
from sys import argv, exit
from Badnet import BadNet5 as badnet
import select
import time
from Utility import utilFunctions as util
import multiprocessing as mp
from os.path import exists as file_exists


# Global variables
TIMEOUT = 0.005
PACKET_SIZE = 1024
PORT = int(argv[1])
SERVER_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER_IP, PORT)



def retransmit(client, packets):
    '''
    Function to retransmit packets in case of loss/error
    Parameters:
    client(socket): Client socket
    packets(dictionary): Buffer of all unacknowledged packets
      
    '''
    keys = packets.keys()
    print(keys)
    if len(keys) > 0:
        
        for key in keys:
            print(f"The key is {key}")
            
            # Dequeue oldest unacknowledged packet
            o_unack = key
            packet = packets.pop(o_unack, None)

            if packet:  
                
                # Transmit packet
                badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)

                # Re-insert into dictionary
                packets[o_unack] = packet  

def check_for_acks(client, packets):

    '''
    Function to check for ack messages and let the sender know not to re-transmit correctly received packets.

    Parameters:
    client(Socket): Client socket
    packets(Dictionary): Buffer of all unacknowledged packets
    
    '''
    ready = select.select([client], [], [], TIMEOUT)

    if ready[0]:
        recv_pkt, addr = client.recvfrom(PACKET_SIZE)

        print(f"Received {util.extract_seq(recv_pkt)}")
        
        # If ack is correctly received, pop packet of this sequence number
        if not util.iscorrupt(recv_pkt):
            seq_no = util.extract_seq(recv_pkt)
            packets.pop(seq_no, None)

    # Ack is not received and timer expires. 
    else:
        print("RETRANSMISSION DUE TO LOSS")
        retransmit(client, packets)

    return

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
    # across each process    
    manager = mp.Manager() 
    packets = manager.dict() 
    
    # Sending file name to server
    print(f"Sending file {FILE_NAME}...")
    data = FILE_NAME.encode(FORMAT)
    packet, seq_no = util.make_pkt(data)
    badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)
    packets[seq_no] = packet

    # Open the local file in 'read-byte' mode
    f = open(FILE_NAME, 'rb')

    # Read chunks of size equal to the DATA_SIZE
    data = f.read(DATA_SIZE)

    # File transfer over the server port.
    while data:
   
        # Make a new packet from the file and transmit to server
        packet, seq_no = util.make_pkt(data)
        
        # Sender keeps a buffer of sent but unacknowledged packets
        packets[seq_no] = packet
        
        
        badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)

        # Check for any received ack messages
        check_for_acks(client, packets)
        print(packets.keys())
        print(f"Length: {len(packets)}")
        
        data = f.read(DATA_SIZE)

    # Closing the file
    f.close()

    
    print(len(packets))
    
    # Hold off client from sending finish packet until all prev packets have been correctly acknowledged
    while len(packets) > 0:
        check_for_acks(client, packets)
        print(packets.keys())
        print(f"Length: {len(packets)}")
    

    # Make finish packet
    finish, finish_seq = util.make_pkt(finish=True)

    # Insert into dictionary
    packets[finish_seq] = finish

    badnet.BadNet.transmit(client, finish, SERVER_IP, PORT)

    # Hold off client from terminating until finish packet has been correctly acknowledged.
    while len(packets) > 0:
        check_for_acks(client, packets)

    # Closing the socket
    client.close()
    
    end = time.perf_counter()
    print(f"Finished in {round(end-start, 2)} second(s)")