from queue import Queue
import typing, threading, abc
from Nebworking import objects as objects
from Nebworking import packets as packets
from Nebworking.nebworking import serverTCP

class ClientLogicTemplate(abc.ABC):
    '''Function "main" must exist as the entrypoint for client logic handling.'''
    def __init__(self, clientObject: objects.clientObject, awaitQueueHook: typing.Callable, serverHook=serverTCP) -> None:
        super().__init__()
        self.clientObject = clientObject
        self.awaitQueue = awaitQueueHook
        self.serverHook = serverHook
        
    @abc.abstractmethod
    def main(self):
        pass

class FrozenClient():
    def __init__(self, clientObject: objects.clientObject, clientLogic: type[ClientLogicTemplate], serverObject: serverTCP) -> None:
        self.clientObject = clientObject
        self.queue = Queue()
        
        self.clientLogic = clientLogic(clientObject=clientObject, awaitQueueHook=self.awaitQueue, serverHook=serverObject)
        threading.Thread(target=lambda:self.clientLogic.main()).start()
        
    def awaitQueue(self) -> typing.Any:
        return self.queue.get()
    
class FrozenClientStorage():
    frozenClients: typing.List[FrozenClient] = []
    def addFrozenClient(self, clientObject: objects.clientObject, clientLogic: type[ClientLogicTemplate], serverObject: serverTCP):
        self.frozenClients.append(FrozenClient(clientObject, clientLogic, serverObject))
        
    def removeFrozenClient(self, clientObject: objects.clientObject):
        for frozenClient in self.frozenClients.copy():
            if frozenClient.clientObject == clientObject:
                self.frozenClients.remove(frozenClient)
                
    def getFrozenClient(self, clientObject: objects.clientObject):
        for frozenClient in self.frozenClients.copy():
            if frozenClient.clientObject == clientObject:
                return frozenClient
            
    def routeNotification(self, notification: typing.Tuple[packets.packetObject, packets.packetObject]):
        header, content = notification
        for frozenClient in self.frozenClients:
            if frozenClient.clientObject.ADDRESS == header.data['sourceAddress']: #Test with packets marked for ALL or OTHERS, not sure rn, very tired
                frozenClient.queue.put(notification)