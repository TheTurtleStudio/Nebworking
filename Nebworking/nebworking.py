import socket, typing, ipaddress, threading, pickle, queue #Public libraries
from math import ceil
from . import packets #Local libraries
from . import objects




class settings():
    PACKETSIZE: int = 1024



class serverTCP():
    def __init__(self, IP: str, PORT: int, ENCODING: str = 'UTF-8', DEBUG: bool = False) -> None:
        self.IP: str = IP
        self.PORT: int = PORT
        self.SOCKET: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ENCODING: str = ENCODING
        self.DEBUG: bool = DEBUG
        self.PACKETSIZE: int = settings.PACKETSIZE #Size of portion of packet taken from network stack at a time
        self.CLIENTS: typing.Dict[threading.Thread, objects.clientObject] = {}
        self.THREADLOCK: threading.Lock = threading.Lock()
        self.NOTIFICATIONS: queue.Queue = queue.Queue() #Used to send packets to library user
        self.MESSAGES: queue.Queue = queue.Queue() #Used to receive packets from library user
        
        
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
            handleClient.join()
            
            
    def sendThread(self) -> None:
        pass
         
            
    def addressToThreadInstance(self, address: typing.Tuple[str, int]) -> threading.Thread: #Used for tracing a client address to the thread object handling the connection, useful for indexing self.CLIENTS
        for thread in self.CLIENTS.keys():
            if self.CLIENTS[thread].ADDRESS == address:
                return thread
        return None
    
    
    def clientObjFromAddress(self, address: typing.Tuple[str, int]) -> objects.clientObject:
        return self.CLIENTS[self.addressToThreadInstance(address=address)]
        
    def handleClient(self, connection: socket.socket, clientAddress: typing.Tuple[str, int]) -> None:
        client = objects.clientObject(connection=connection, address=clientAddress, thread=threading.current_thread())
        self.queueNotification(packets.construct.connection(client=client, pickled=False))
        self.debug(f'[CONNECTION]: {clientAddress} connected')
        self.THREADLOCK.acquire()
        ### BEGIN THREADLOCK ###
        self.CLIENTS[str(threading.current_thread())] = client
        ### END THREADLOCK ###
        self.THREADLOCK.release()
        try:
            while not client.FLAG_TERMINATE:
                header = connection.recv(self.PACKETSIZE)
                if not header:
                    client.FLAG_TERMINATE = True
                if len(header) == 0:
                    continue
                packetAsObject: packets.packetObject = pickle.loads(header)
                packet: dict = packetAsObject.raw
                messageLength = int(packet['data']['length'])
                del packetAsObject, packet
                if messageLength > 0:
                    
                    packetBytes = bytes()
                    for _chunks in range(ceil(messageLength / self.PACKETSIZE)):
                        packetBytes += client.CONNECTION.recv(self.PACKETSIZE)
                    packet: packets.packetObject = pickle.loads(packetBytes)
                    self.queueNotification(packet) #Queue notification of packet
                    
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
                
        
    @property
    def CLIENTCOUNT(self) -> int: #Used for property self.CLIENTCOUNT as a get method
        return len(self.CLIENTS)
        
        
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
        self.PACKETSIZE: int = settings.PACKETSIZE #Size of portion of packet taken from network stack at a time
        self.NOTIFICATIONS: queue.Queue = queue.Queue() #Used to send packets to library user
        self.MESSAGES: queue.Queue = queue.Queue() #Used to receive packets from library user
        
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
            header = self.SOCKET.recv(self.PACKETSIZE).decode(self.ENCODING).encode()
            if not header:
                self.FLAG_TERMINATE = True
            if len(header) == 0:
                continue
            packetAsObject: packets.packetObject = pickle.loads(header)
            packet: dict = packetAsObject.raw
            messageLength = int(packet['data']['length'])
            del packetAsObject, packet
            
            if messageLength > 0:
                packetBytes = str()
                for _chunks in range(ceil(messageLength / self.PACKETSIZE)):
                    packetBytes += self.SOCKET.recv(self.PACKETSIZE).decode(self.ENCODING)
                packet: packets.packetObject = pickle.loads(packetBytes)
                self.queueNotification(packet) #Queue notification of packet
        
        
    def queueNotification(self, packet: packets.packetObject) -> None:
        self.NOTIFICATIONS.put(packet)
        
        
    def queueMessage(self, packet: packets.packetObject) -> None:
        self.MESSAGES.put(packet)
        
        
    def sendData(self, data: bytes, sourceAddress: typing.Tuple[str, int] = None, destinationAddress: typing.Tuple[str, int] = None) -> None:
        if sourceAddress is None:
            sourceAddress: typing.Tuple[str, int] = self.SOCKET.getsockname()
        if destinationAddress is None:
            destinationAddress = (self.SERVERIP, self.SERVERPORT)
            
        payloadPacket = packets.construct.payload(data)
        
        header = packets.createHeader(packet=payloadPacket, sourceAddress=sourceAddress, destinationAddress=destinationAddress)
        self.sendPacket(header)
        self.sendPacket(payloadPacket)
        
    
    def sendPacket(self, packet: bytes) -> None: #When using, note that you will need to manually send a header packet. Use sendData for payload packets
        packet = packets.createValidSizePackets(packet=packet, length=self.PACKETSIZE)
        for packetChunk in packet:
            self.SOCKET.sendall(packetChunk)
     
     
    def debug(self, message: str) -> None:
        if self.DEBUG:
            print(message)