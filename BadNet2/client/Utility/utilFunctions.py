import pickle
from hashlib import md5


def genChecksum(data):
    '''Generates 16-bit checksum using sha256 hash function'''
    checksum = bin(int.from_bytes(md5(data).digest(), 'little'))

    # Least significant 16-bit
    return checksum[-16:]


def iscorrupt(pkt):
    '''Returns true if packet is corrupt'''

    try:
        # deserializing packet
        pkt = pickle.loads(pkt)
        return not(genChecksum(pkt[-1]) == pkt[0])
    except:
        return True


def makePkt(checksum, data):
    '''Make Packet, Format: checksum, data'''

    pkt = []
  
    pkt.append(checksum)
    pkt.append(data)

    pkt = pickle.dumps(pkt)
    return pkt


def extractData(pkt):
    '''Deserialize packet and returns data'''
    return pickle.loads(pkt)[-1]


def isAck(pkt):
    '''Returns true if the packet was acknowledgment packet'''
    pkt = pickle.loads(pkt)
    return pkt[-1] == b"1"

