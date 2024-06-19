import socket, typing, threading




class clientObject(): #Not to be confused with clientTCP, this contains information about a client that has connected to a server created by a serverTCP instance
    def __init__(self, connection: socket.socket, address: typing.Tuple[str, int], thread: threading.Thread) -> None:
        self.CONNECTION: socket.socket = connection
        self.ADDRESS: typing.Tuple[str, int] = address
        self.THREAD: threading.Thread = thread
        
        self.FLAG_TERMINATE: bool = False
        
        
class clientObjectSerializable(clientObject):
    CONNECTION = None
    THREAD = None
    
    
def getSerializableClientObject(nonSerialized: clientObject):
    return clientObjectSerializable(connection=None, address=nonSerialized.ADDRESS, thread=None)