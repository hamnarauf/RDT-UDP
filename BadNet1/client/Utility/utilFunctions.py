import pickle

SEQ_NO = 0

def make_pkt(data=b'0', ack=False, finish=False, seq=None):
    '''Make Packet, Format: seq.no, ack_bit, finish_bit, data'''
    global SEQ_NO
    pkt = []
    
    if ack and seq == None:
        raise Exception("Please provide a sequence number with acknowledgment packet")

    if ack:
        # Attach seq no. of received packet
        pkt.append(str(bin(seq)))
        
        # Ack bit set to 1
        pkt.append(b'1')

    else:
        # Attach sequence number of next data paccket
        pkt.append(str(bin(SEQ_NO)))
        
        # Set ack bit to 0
        pkt.append(b'0')
    
    # Finish bit determines whether we need to disconnect from a particular client or not.
    if finish:
        pkt.append(b'1')

    else:
        pkt.append(b'0')

    pkt.append(data)
    pkt = pickle.dumps(pkt)
    
    # Ack and finish?????? packets should not increment the sequence number.
    if not ack:
        SEQ_NO += 1
    

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