import pickle

SEQ_NO = 0

def make_pkt(data):
    '''Make Packet, Format: seq.no, data'''
    global SEQ_NO
    pkt = []
    
    pkt.append(str(bin(SEQ_NO)))
    pkt.append(data)
    pkt = pickle.dumps(pkt)
    
    SEQ_NO += 1
    
    return pkt

def extract_data(pkt):
    '''Deserialize packet and returns data'''
    return pickle.loads(pkt)[-1]

def extract_seq(pkt):
    '''Deserialize packet, convert binary string to integer and return sequence number'''
    seq = pickle.loads(pkt)[0]
    seq = int(seq, 2)
    return seq

def extract(pkt):
    '''Deserialize packet and returns sequence number'''
    return int(pickle.loads(pkt)[0], 2), pickle.loads(pkt)[1]


def make_ack(packet):
    '''Format: Packet seq.no, Ack'''
    
    ack = []
    seq_no = pickle.loads(packet)[0]

    ack.append(seq_no)
    ack.append(b'1')

    ack = pickle.dumps(ack)
    return ack