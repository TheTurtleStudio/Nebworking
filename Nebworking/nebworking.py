import socket, typing, threading, pickle, queue #Public libraries
from math import ceil
from . import packets #Local libraries
from . import objects




class _settings():
    PACKETSIZE: int = 1024



class serverTCP():
    def __init__(self, IP: str, PORT: int, ENCODING: str = 'UTF-8', DEBUG: bool = False, RELAYCALLBACK=None, ALLOWSOURCESPOOFING=True) -> None:
        self.IP: str = IP
        self.PORT: int = PORT
        self.SOCKET: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ENCODING: str = ENCODING
        self.DEBUG: bool = DEBUG
        self.PACKETSIZE: int = _settings.PACKETSIZE #Size of portion of packet taken from network stack at a time
        self.CLIENTS: typing.Dict[threading.Thread, objects.clientObject] = {}
        self.THREADLOCK: threading.Lock = threading.Lock()
        self.NOTIFICATIONS: queue.Queue = queue.Queue() #Used to send packets to library user
        self.RELAYFUNCTION: typing.Callable[[packets.packetObject, packets.packetObject], None] = self.handleRelay if RELAYCALLBACK is None else RELAYCALLBACK
        self.ALLOWSOURCESPOOFING: bool = ALLOWSOURCESPOOFING #To be implemented
        
        
    def start(self) -> None:
        mainServerThread = threading.Thread(target=self.mainServerThread)
        mainServerThread.start()
        
    
    def mainServerThread(self) -> None:
        self.SOCKET.bind((self.IP, self.PORT))
        self.SOCKET.listen(5)
        self.debug(f'[LISTENING]: Server started listening on {self.IP}:{self.PORT}')
        while True: #Start listening for clients. Create new thread to handleClient for each connected client. Keep listening for clients.
            clientAddress: typing.Tuple[str, int] = None
            connection, clientAddress = self.SOCKET.accept()
            handleClient = threading.Thread(target=self.handleClient, args=(connection, clientAddress))
            handleClient.start()
         
    
    def sendData(self, data: bytes, sourceAddress: typing.Tuple[str, int] = None, destinationAddress: typing.Tuple[str, int] = None) -> None:
        payloadPacket = packets.construct.payload(data)
        self.sendPacket(packet=payloadPacket, sourceAddress=sourceAddress, destinationAddress=destinationAddress)
        
    
    def sendPacket(self, packet: bytes, header: bytes=None, sourceAddress: typing.Tuple[str, int]=None, destinationAddress: typing.Tuple[str, int]=None) -> bool:
        if sourceAddress is None and header is None:
            sourceAddress = (self.IP, self.PORT)
        elif sourceAddress is None and header is not None:
            sourceAddress = packets.unSerializePacketObject(header).data['sourceAddress'] 
        if destinationAddress is None and header is None:
            destinationAddress = packets.AddressType.ALL() #Send to all clients
        elif destinationAddress is None and header is not None:
            destinationAddress = packets.unSerializePacketObject(header).data['destinationAddress']


        if header is None:
            header = packets.createHeader(packet=packet, sourceAddress=sourceAddress, destinationAddress=destinationAddress)
            
        recipientClientObjects: typing.List[objects.clientObject] = []
        if destinationAddress == packets.AddressType.ALL():
            recipientClientObjects = [clientObject for clientObject in self.CLIENTS.values()]
        elif destinationAddress == packets.AddressType.OTHERS():
            recipientClientObjects = [(clientObject if clientObject.ADDRESS != sourceAddress else None) for clientObject in self.CLIENTS.values()]
        else:
            recipientClientObjects = [self.addressToClientObject(destinationAddress)]
            
        for recipientClientObject in recipientClientObjects:
            if recipientClientObject:
                _common.sendPacketPair(headerPacket=header, contentPacket=packet, connection=recipientClientObject.CONNECTION)
        return True if len(recipientClientObjects) > 0 else False #Return if any packets were sent
    
    
    def addressToThreadInstance(self, address: typing.Tuple[str, int]) -> threading.Thread: #Used for tracing a client address to the thread object handling the connection, useful for indexing self.CLIENTS
        for thread in self.CLIENTS.keys():
            if self.CLIENTS[thread].ADDRESS == address:
                return thread
        return None
    
    
    def addressToClientObject(self, address: typing.Tuple[str, int]) -> objects.clientObject:
        for clientObject in self.CLIENTS.values():
            if clientObject.ADDRESS == address:
                return clientObject
        return None
    
    
    def handleRelay(self, headerPacket: packets.packetObject, contentPacket: packets.packetObject) -> None:
        destinationAddress = headerPacket.raw['data']['destinationAddress']
        sourceAddress = headerPacket.raw['data']['sourceAddress']
        success = self.sendPacket(packet=packets.serializePacketObject(contentPacket), header=packets.serializePacketObject(headerPacket))
        relayPacket = packets.construct.relay(sourceAddress=sourceAddress, destinationAddress=destinationAddress, relayedPacket=contentPacket, success=success, pickled=False)
        self.queueNotification(relayPacket)
    
        
    def handleClient(self, connection: socket.socket, clientAddress: typing.Tuple[str, int]) -> None:
        client = objects.clientObject(connection=connection, address=clientAddress, thread=threading.current_thread())
        self.queueNotification(packets.construct.connection(client=client, pickled=False))
        self.debug(f'[CONNECTION]: {clientAddress} connected')
        self.THREADLOCK.acquire()
        ### BEGIN THREADLOCK ###
        self.CLIENTS[str(threading.current_thread())] = client
        ### END THREADLOCK ###
        self.THREADLOCK.release()
        self.sendPacket(packet=packets.construct.connection(client=client), destinationAddress=client.ADDRESS)
        try:
            while not client.FLAG_TERMINATE:
                header = connection.recv(self.PACKETSIZE)
                if not header:
                    client.FLAG_TERMINATE = True
                if len(header) == 0:
                    continue
                headerAsObject: packets.packetObject = pickle.loads(header)
                headerPacketRaw: dict = headerAsObject.raw
                messageLength = int(headerPacketRaw['data']['length'])
                if messageLength > 0:
                    fullPacket = packets.constructFullPacketContent(socketConnection=client.CONNECTION, packetSize=self.PACKETSIZE, length=messageLength)
                    if headerPacketRaw['data']['destinationAddress'] == (self.IP, self.PORT):
                        self.queueNotification(fullPacket)
                    else:
                        self.RELAYFUNCTION(headerAsObject, fullPacket)
                    
                    
        except ConnectionResetError:
            client.FLAG_TERMINATE = True
            
        client.CONNECTION.close()
        self.THREADLOCK.acquire()
        ### BEGIN THREADLOCK ###
        del self.CLIENTS[str(threading.current_thread())]
        ### END THREADLOCK ###
        self.THREADLOCK.release()
        self.queueNotification(packets.construct.terminate(client=client, pickled=False))
        self.debug(f'[CONNECTION]: {clientAddress} connection closed')
    
    
    def queueNotification(self, packet: packets.packetObject) -> None:
        self.NOTIFICATIONS.put(packet)
        
        
    def getNotification(self) -> packets.packetObject:
        if self.NOTIFICATIONS.empty():
            return None
        return self.NOTIFICATIONS.get()
                
        
    @property
    def CLIENTCOUNT(self) -> int: #Used for property self.CLIENTCOUNT as a get method
        return len(self.CLIENTS)
    
    
    @property
    def CLIENTADDRESSLIST(self) -> typing.List[typing.Tuple[str, int]]:
        return [clientObject.ADDRESS for clientObject in self.CLIENTS.values()]
        
        
    def debug(self, message: str) -> None:
        if self.DEBUG:
            print(message)
            
            
            
class clientTCP():
    def __init__(self, SERVERIP: str, SERVERPORT: int, ENCODING: str = 'UTF-8', DEBUG: bool = False) -> None:
        self.SERVERIP: str = SERVERIP
        self.SERVERPORT: int = SERVERPORT
        self.SOCKET: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ENCODING: str = ENCODING
        self.DEBUG: bool = DEBUG
        self.PACKETSIZE: int = _settings.PACKETSIZE #Size of portion of packet taken from network stack at a time
        self.NOTIFICATIONS: queue.Queue = queue.Queue() #Used to send packets to library user
        
        self.FLAG_TERMINATE: bool = False
        
        
    def start(self) -> None:
        mainClientThread = threading.Thread(target=self.mainClientThread)
        mainClientThread.start()
        
        
    def mainClientThread(self) -> None:
        self.SOCKET.connect((self.SERVERIP, self.SERVERPORT))
        self.debug(f'[CONNECTED]: Client connected to {self.SERVERIP}:{self.SERVERPORT}')
        receiveThread = threading.Thread(target=self.receiveThread)
        receiveThread.start()
        receiveThread.join()
            
            
    def receiveThread(self) -> None:
        while not self.FLAG_TERMINATE:
            header = self.SOCKET.recv(self.PACKETSIZE)
            if not header:
                self.FLAG_TERMINATE = True
            if len(header) == 0:
                continue
            packetAsObject: packets.packetObject = pickle.loads(header)
            packet: dict = packetAsObject.raw
            messageLength = int(packet['data']['length'])
            del packetAsObject, packet
            
            if messageLength > 0:
                packetBytes = bytes()
                for _chunks in range(ceil(messageLength / self.PACKETSIZE)):
                    packetBytes += self.SOCKET.recv(self.PACKETSIZE)
                packet: packets.packetObject = pickle.loads(packetBytes)
                self.queueNotification(packet) #Queue notification of packet
        
        
    def queueNotification(self, packet: packets.packetObject) -> None:
        self.NOTIFICATIONS.put(packet)
        
        
    def sendData(self, data: bytes, sourceAddress: typing.Tuple[str, int] = None, destinationAddress: typing.Tuple[str, int] = None) -> None:
        payloadPacket = packets.construct.payload(data)
        self.sendPacket(packet=payloadPacket, sourceAddress=sourceAddress, destinationAddress=destinationAddress)
        
    
    def sendPacket(self, packet: bytes, sourceAddress: typing.Tuple[str, int] = None, destinationAddress: typing.Tuple[str, int] = None) -> None:
        if sourceAddress is None:
            sourceAddress: typing.Tuple[str, int] = self.SOCKET.getsockname()
        if destinationAddress is None:
            destinationAddress = packets.AddressType.SINGLE(address=self.SERVERIP, port=self.SERVERPORT)
        
        header = packets.createHeader(packet=packet, sourceAddress=sourceAddress, destinationAddress=destinationAddress)
        _common.sendPacketPair(headerPacket=header, contentPacket=packet, connection=self.SOCKET)
            
            
    def waitForConnectionPacket(self):
        while True:
            if self.NOTIFICATIONS.qsize() > 0:
                item: packets.packetObject = self.NOTIFICATIONS.get()
                self.NOTIFICATIONS.put(item)
                if item.packetType == packets.PacketType.CONNECTION:
                    break
                
                
    def getNotification(self) -> packets.packetObject:
        if self.NOTIFICATIONS.empty():
            return None
        return self.NOTIFICATIONS.get()
             
        
        
        
    def debug(self, message: str) -> None:
        if self.DEBUG:
            print(message)



class _common():
    @classmethod
    def sendPacketPair(self, headerPacket: typing.Union[packets.packetObject, bytes], contentPacket: typing.Union[packets.packetObject, bytes], connection: socket.socket):
        #Splitting the information into valid sized packets and then joining it back together might not be the most efficient but this is how I'll do it for now.
        validHeaderPackets = packets.createValidSizePackets(packet=headerPacket, length=_settings.PACKETSIZE)
        validContentPackets = packets.createValidSizePackets(packet=contentPacket, length=_settings.PACKETSIZE)
        validHeaderPacket = b"".join(validHeaderPackets)
        validContentPacket = b"".join(validContentPackets)
        fullPacketBytes = packets.getFullPacketBytes(header=validHeaderPacket, packet=validContentPacket)
        connection.sendall(fullPacketBytes)