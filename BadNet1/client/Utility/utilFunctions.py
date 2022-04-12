from hashlib import md5

SEQ_NO = 0

def make_pkt(data=b'0', finish=False):
    '''
    Make Packet,
    Format: checksum(2B), seq.no(2B), ack_bit(1B), finish_bit(1B), data(1018B)
    Total: 1024 Bytes
    '''
    
    global SEQ_NO
    
    # Attach sequence number of next data packet
    seq_bit = SEQ_NO.to_bytes(2, "big")
    
    # Set ack bit to 0
    ack_bit = b'0'

    # Finish bit determines whether we need to disconnect from a particular client or not.
    if finish:
        finish_bit = b'1'

    else:
        finish_bit = b'0'

    pkt = seq_bit + ack_bit + finish_bit + data

    # Attach checksum
    checksum = get_checksum(pkt)
    pkt = checksum + pkt

    # Increment the sequence number.
    SEQ_NO += 1
    
    print(SEQ_NO)

    return pkt, SEQ_NO - 1


def extract_seq(pkt):
    '''Extract sequence number, convert it to integer'''
    seq_bit = pkt[2:4]
    return int.from_bytes(seq_bit, "big")

def extract(pkt):
    '''Returns sequence number, data'''
    return extract_seq(pkt), pkt[6:]

def is_ack(pkt):
    ack_bit = pkt[4:5]
    return ack_bit == b'1'

def is_finish(pkt):
    finish_bit = pkt[5:6]
    return finish_bit == b'1'

def get_checksum(data):
    '''Generates 2-byte checksum using md5 hash function'''
    checksum = md5(data).digest()[-2:]

    return checksum

def make_ack(seq):
    '''  
    Make Ack Packet,
    Format: checksum(2Bytes), seq.no(2B), ack_bit(1B), finish_bit(1B), data(1018B)
    '''

    # Attach seq no. of received packet
    seq_bit = seq.to_bytes(2, "big")
    
    # Ack bit set to 1
    ack_bit = b'1'

    # Finish bit set to 0
    finish_bit  = b'0'
    
    # No data transmitted 
    data = b'0'

    ack = seq_bit + ack_bit + finish_bit + data

    # attach checksum
    checksum = get_checksum(ack) 
    ack = checksum + ack

    return ack

def iscorrupt(pkt):
    '''Returns true if packet is corrupt'''
    recv_checksum = pkt[0:2]
    
    return not(get_checksum(pkt[2:]) == recv_checksum)
