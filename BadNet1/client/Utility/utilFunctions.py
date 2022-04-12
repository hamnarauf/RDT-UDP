import pickle
from hashlib import md5

SEQ_NO = 0

def make_pkt(data=b'0', finish=False):
    '''Make Packet, Format: seq.no, ack_bit, finish_bit, checksum, data'''
    global SEQ_NO
    pkt = []
    
    # Attach sequence number of next data paccket
    pkt.append(str(bin(SEQ_NO)))
    
    # Set ack bit to 0
    pkt.append(b'0')

    # Finish bit determines whether we need to disconnect from a particular client or not.
    if finish:
        pkt.append(b'1')

    else:
        pkt.append(b'0')

    pkt.append(get_checksum(data))
    pkt.append(data)
    pkt = pickle.dumps(pkt)
    

    # Increment the sequence number.
    SEQ_NO += 1
    
    print(SEQ_NO)

    return pkt, SEQ_NO - 1


def extract_seq(pkt):
    '''Deserialize packet, convert binary string to integer and return sequence number'''
    seq = pickle.loads(pkt)[0]
    seq = int(seq, 2)
    return seq

def extract(pkt):
    '''Deserialize packet and returns sequence number'''
    return int(pickle.loads(pkt)[0], 2), pickle.loads(pkt)[-1]

def is_ack(pkt):
    ack_bit = pickle.loads(pkt)[1]
    return ack_bit == b'1'

def is_finish(pkt):
    finish_bit = pickle.loads(pkt)[2]
    return finish_bit == b'1'

def get_checksum(data):
    '''Generates 2-byte checksum using md5 hash function'''
    checksum = md5(data).digest()[-2:]

    return checksum

def make_ack(seq):
    ack = []

    data = b'0'

    # Attach seq no. of received packet
    ack.append(str(bin(seq)))
    
    # Ack bit set to 1
    ack.append(b'1')

    # Finish bit set to 0
    ack.append(b'0')

    # Attach checksum
    ack.append(get_checksum(data))
    
    ack.append(data)
    ack = pickle.dumps(ack)

    return ack


def make_fin():
    '''Make Packet, Format: seq.no, ack_bit, finish_bit, checksum, data'''
    finish = []
    seq = -1

    data = b'0'
    # Attach sequence number of next data paccket
    finish.append(str(bin(seq)))
    
    # Set ack bit to 0
    finish.append(b'0')

    # Finish bit determines whether we need to disconnect from a particular client or not.
    finish.append(b'1')


    finish.append(get_checksum(data))
    finish.append(data)
    finish = pickle.dumps(finish)
    
    return finish, seq


def iscorrupt(pkt):
    '''Returns true if packet is corrupt'''

    try:
        # deserializing packet
        pkt = pickle.loads(pkt)
        return not(get_checksum(pkt[-1]) == pkt[-2])
    
    except:
        return True