import typing, enum, pickle, math
from socket import socket
import Nebworking.objects as objects




class PacketType(str, enum.Enum):
    HEADER = 'header' #Sent before every packet sent through datastream. TERMINATE and CONNECTION typically not sent through datastream, they're just informational mostly.
    TERMINATE = 'terminate' #Sent to server NOTIFICATIONS when a connection was terminated
    PAYLOAD = 'payload' #Normal data packet.
    CONNECTION = 'connection' #Sent to server NOTIFICATIONS when a connection is established between client and server
    RELAY = 'relay' #When the server receives a packet with a destinationAddress that corresponds to another client on the network, a relay packet is sent to server NOTIFICATIONS and then the original packet is forwarded to the intended client
    STATUS = 'status' #Sent to the client when a packet is handled. Returned status via ResponseStatus
    
    
class ResponseStatus(str, enum.Enum): #Based off HTTP response status codes
    C200 = "OK" #Everything succeeded. Very good.
    C202 = "Accepted" #Request has been received
    C400 = "Bad Request" #Can't/won't process request due to sender error
    C403 = "Forbidden" #Sender does not have access to the content requested
    C405 = "Method Not Allowed" #Request method is known but sender does not have access to make the request
    C418 = "Nebnotworking" #Little easter egg :)
    C500 = "Internal Server Error" #Cannot serve client due to a server error
    
    
class AddressType():
    
    @staticmethod
    def ALL() -> typing.Tuple[str, int]:
        return ('all', 'all')
    
    
    @staticmethod
    def OTHERS() -> typing.Tuple[str, int]:
        return ('others', 'others')


    @staticmethod
    def SINGLE(address: str, port: int) -> typing.Tuple[str, int]:
        return (address, port)



class packetObject():
    def __init__(self, packetType: PacketType, data: bytes = None) -> None:
        self.packetType: PacketType = packetType
        self.data: typing.Any = data
        
        
    @property
    def raw(self) -> typing.Dict[str, typing.Any]:
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
        client = objects.getSerializableClientObject(client) if client is not None else None
        data = {'clientObject': client}
        packet = packetObject(packetType=PacketType.CONNECTION, data=data)
        if pickled:
            return pickle.dumps(packet)
        return packet
    
    
    @staticmethod
    def relay(sourceAddress: typing.Tuple[str, int], destinationAddress: typing.Tuple[str, int], relayedPacket: packetObject, success=True, pickled: bool = True) -> typing.Union[packetObject, bytes]:
        data = {'success': success, 'sourceAddress': sourceAddress, 'destinationAddress': destinationAddress, 'relayedPacket': relayedPacket}
        packet = packetObject(packetType=PacketType.RELAY, data=data)
        if pickled:
            return pickle.dumps(packet)
        return packet
    
    
    @staticmethod
    def status(status: ResponseStatus, pickled: bool = True) -> typing.Union[packetObject, bytes]:
        data = {'status': status.name, 'description': status.value}
        packet = packetObject(packetType=PacketType.STATUS, data=data)
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


def constructFullPacketContent(socketConnection: socket, packetSize: int, length: int) -> packetObject:
    packetBytes = bytes()
    for _chunks in range(math.ceil(length / packetSize)):
        packetBytes += socketConnection.recv(packetSize)
    packet: packetObject = pickle.loads(packetBytes)
    return packet


def serializePacketObject(nonSerializedPacketObject: packetObject) -> bytes:
    return pickle.dumps(nonSerializedPacketObject)


def unSerializePacketObject(serializedPacketObject: bytes) -> packetObject:
    return pickle.loads(serializedPacketObject)


def getFullPacketBytes(header: typing.Union[packetObject, bytes], packet: typing.Union[packetObject, bytes]) -> bytes:
    if type(header) is packetObject:
        header = serializePacketObject(header)
    if type(packet) is packetObject:
        packet = serializePacketObject(packet)
    return header + packet