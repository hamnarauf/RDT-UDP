import socket
from sys import argv, exit
from Badnet import BadNet5 as badnet
import time
import select
from Utility import utilFunctions as util
import multiprocessing as mp

# Each process is spawned with copies of these values.
TIMEOUT = 0.001
PACKET_SIZE = 1024
PORT = int(argv[1])
SERVER_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER_IP, PORT)

# Function to retransmit packets in case of loss/error
def retransmit_pkts(client, packets):
    
    while True:
        
        # Useful for indicating whether there is some data being transmitted to the socket
        ready = select.select([client], [], [], TIMEOUT)
        
        keys = packets.keys()

        if not ready[0] and len(keys) > 0:
            o_unack = keys[0]
            packet = packets.pop(o_unack)

            print(f"\n\nGoing to send packet {util.extract_seq(packet)}")
            
            # Transmit packet
            badnet.BadNet.transmit(client, packet, SERVER_IP, PORT)

            # Re-insert into dictionary
            packets[o_unack] = packet

# Function to check for ack messages and let the sender know not to re-transmit correctly received packets.
def check_for_acks(client, packets):

    while True:

        recv_pkt, addr = client.recvfrom(PACKET_SIZE)

        if not util.iscorrupt(recv_pkt):
            seq_no = util.extract_seq(recv_pkt)
            print(f"Received packet {seq_no}")
            pop = packets.pop(seq_no, None)
            if pop == None:
                print(f"Popped NONE")
            else:
                print(f"Popping packet {seq_no}")

        else:
            print("CORRUPTED PACKET")


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
    
    # Creating a shared dictionary that every process can read/write to. Updates made in one process are reflected
    # across every process    
    manager = mp.Manager() 
    packets = manager.dict() 
    
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

    # Read chunks of size equal to the size of the buffer, in this case the packet size.
    data = f.read(DATA_SIZE)

    # File transfer over the server port.
    while data:
   
        # Make a new packet from the file
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
    
    print("\nSENDING FINISH PACKET NOW")

    # Make finish packet
    finish, finish_seq = util.make_pkt(finish=True)

    # Insert into dictionary
    packets[finish_seq] = finish

    badnet.BadNet.transmit(client, finish, SERVER_IP, PORT)
    print(f'Sequence number of finish packet is {util.extract_seq(finish)}')

    # Hold off client from terminating until finish packet has been correctly acknowledged.
    while len(packets) > 0:
        pass


    # p1.join()
    # p2.join()

    # Terminating the processes
    p1.terminate()
    p2.terminate()

    # p1.close()
    # p2.close()
    
    # Closing the socket
    client.close()
    
    end = time.perf_counter()
    print(f"Finished in {round(end-start, 2)} second(s)")