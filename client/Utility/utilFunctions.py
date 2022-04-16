from hashlib import md5

SEQ_NO = 0

def make_pkt(data=b'0', finish=False):
    '''
    Make Packet
    Format: checksum(2B), seq.no(2B), ack_bit(1B), finish_bit(1B), data(1018B)
    Total: 1024 Bytes

    Parameters:
    data(byte): Data to be inserted in packet, default is b'0'
    finish(boolean): finish is True for finish packet, default is 'False'

    Returns:
    bytes: Packet of size 1024 Bytes
    int: Sequence number of packet

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
    
    return pkt, SEQ_NO - 1


def extract_seq(pkt):
    '''
    Extract sequence number, convert it to integer
    
    Parameter:
    pkt(bytes): Packet from which sequence number is to be extracted

    Returns:
    int: sequence number
    
    '''
    seq_bit = pkt[2:4]
    return int.from_bytes(seq_bit, "big")


def extract(pkt):
    '''
    Returns sequence number and data
    
    Parameter:
    pkt(bytes): Packet from which sequence number and data is to be extracted

    Returns:
    int: Sequence number of packet 
    bytes: Data of packet
    
    '''
    return extract_seq(pkt), pkt[6:]


def is_ack(pkt):
    '''
    Checks if pkt is an acknowlegment packet

    Parameter:
    pkt(bytes): Packet

    Returns:
    boolean: True if pkt is an acknowlegement packet
    
    '''
    ack_bit = pkt[4:5]
    return ack_bit == b'1'


def is_finish(pkt):
    '''
    Checks if pkt is a finish packet

    Parameter:
    pkt(bytes): Packet

    Returns:
    boolean: True if pkt is a finish packet
    
    '''

    finish_bit = pkt[5:6]
    return finish_bit == b'1'


def get_checksum(data):
    '''
    Generates 2-byte checksum using md5 hash function
    
    Parameter:
    data(bytes): data to be sent

    Returns:
    bytes: checksum

    '''
    checksum = md5(data).digest()[-2:]

    return checksum

def make_ack(seq):
    '''  
    Make acknowlegement Packet,
    Format: checksum(2Bytes), seq.no(2B), ack_bit(1B), finish_bit(1B), data(1018B)

    Parameter:
    seq(int): Sequence number of packet whose ack is to be sent

    Returns:
    bytes: Acknowlegement packet of size 1024 Bytes

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
    '''
    Checks if pkt is corrupt

    Parameter:
    pkt(bytes): Packet

    Returns:
    boolean: True if pkt is corrupt
    '''

    recv_checksum = pkt[0:2]
    return not(get_checksum(pkt[2:]) == recv_checksum)
