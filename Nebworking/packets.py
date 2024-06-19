import typing, enum, pickle, math
from . import objects




class PacketType(str, enum.Enum):
    HEADER = 'header' #Sent before every packet sent through datastream. TERMINATE and CONNECTION typically not sent through datastream, they're just informational mostly.
    TERMINATE = 'terminate' #Sent to server NOTIFICATIONS when a connection was terminated
    PAYLOAD = 'payload' #Normal data packet.
    CONNECTION = 'connection' #Sent to server NOTIFICATIONS when a connection is established between client and server
    RELAY = 'relay' #When the server receives a packet with a destinationAddress that corresponds to another client on the network, a relay packet is sent to server NOTIFICATIONS and then the original packet is forwarded to the intended client
    #Note: RELAY not implemented.
    #Note: serverTCP forwarding for header sourceAddresses not implemented yet


class packetObject():
    def __init__(self, packetType: PacketType, data: bytes = None) -> None:
        self.packetType: PacketType = packetType
        self.data: object = data
        
        
    @property
    def raw(self) -> typing.Dict[str, object]:
        return {'packetType': self.packetType, 'data': self.data}
    
    
    
class construct():
    @staticmethod
    def header(sourceAddress: typing.Tuple[str, int], destinationAddress: typing.Tuple[str, int], length: int, pickled: bool = True) -> typing.Union[packetObject, bytes]: #Remember to pickle output
        data = {'sourceAddress': sourceAddress, 'destinationAddress': destinationAddress, 'length': length}
        packet = packetObject(packetType=PacketType.HEADER, data=data)
        if pickled:
            return pickle.dumps(packet)
        return packet
    
    
    @staticmethod
    def terminate(client: objects.clientObjectSerializable=None, pickled: bool = True) -> typing.Union[packetObject, bytes]:
        client = objects.getSerializableClientObject(client)
        data = {'clientObject': client}
        packet = packetObject(packetType=PacketType.TERMINATE, data=data)
        if pickled:
            return pickle.dumps(packet)
        return packet
    
    
    @staticmethod
    def payload(payload: bytes, pickled: bool = True) -> typing.Union[packetObject, bytes]:
        data = {'payload': payload}
        packet = packetObject(packetType=PacketType.PAYLOAD, data=data)
        if pickled:
            return pickle.dumps(packet)
        return packet
        
    
    @staticmethod
    def connection(client: objects.clientObjectSerializable, pickled: bool = True) -> typing.Union[packetObject, bytes]:
        client = objects.getSerializableClientObject(client)
        data = {'clientObject': client}
        packet = packetObject(packetType=PacketType.CONNECTION, data = data)
        if pickled:
            return pickle.dumps(packet)
        return packet


def createHeader(packet: typing.Union[packetObject, bytes], sourceAddress: typing.Tuple[str, int], destinationAddress: typing.Tuple[str, int], pickled: bool = True) -> typing.Union[packetObject, bytes]:
    if type(packet) is packetObject: #Packle has not been pickled, but is a packetObject
        return (construct.header(sourceAddress=sourceAddress, destinationAddress=destinationAddress, length=len(pickle.dumps(packet)), pickled=pickled))
    if type(packet) is bytes: #Packet has been pickled
        return (construct.header(sourceAddress=sourceAddress, destinationAddress=destinationAddress, length=len(packet), pickled=pickled))
    
    
def createValidSizePackets(packet: bytes, length: int) -> typing.List[bytes]:
    packetList = []
    for sectionIndex in range(math.ceil(len(packet) / length)):
        packetChunk = (packet[(sectionIndex * length):((sectionIndex+1) * length)])
        if len(packetChunk) < length:
            packetList.append(b"".join([packetChunk] + [b" " for _padding in range(length - len(packetChunk))]))
        else:
            packetList.append(packetChunk)
    return packetList