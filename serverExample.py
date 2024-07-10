import Nebworking.nebworking as nebworking
import Nebworking.packets as packets
from Nebworking.eventTypes import Events
import Nebworking.objects as objects
import typing

print("I'm the server")
HOST = "192.168.0.58"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

 
'''FrozenClient System (Built-in multiclient logic helper)'''
import Nebworking.multiclientHelper as multiclientHelper
import clientLogicsExample
frozenClientStorage = multiclientHelper.FrozenClientStorage()
'''The FrozenClient system lets us take messages delivered by clients from one large queue and have a separate thread for each clients messages to be handled'''
'''I also thought it sounded cool. Frozone vibes. There's nothing special about the system, I just want to enjoy this small victory so I'm making it sound cooler than it really is.'''


class Callbacks():
    @staticmethod
    def newNotification(notification: typing.Tuple[packets.packetObject, packets.packetObject]):
        '''I can be used as a callback for NOTIFICATION events, but right now they're being handled by the FrozenClient system.'''
        
        pass
        
    @staticmethod
    def newConnection(clientObject: objects.clientObject):
        print(f"New connection: {clientObject.ADDRESS}")
        frozenClientStorage.addFrozenClient(clientObject=clientObject, clientLogic=clientLogicsExample.ClientLogic)
        
    @staticmethod
    def clientTerminated(clientObject: objects.clientObject):
        print(f"Connection terminated: {clientObject.ADDRESS}")
        frozenClientStorage.removeFrozenClient(clientObject=clientObject)


server = nebworking.serverTCP(IP=HOST, PORT=PORT, DEBUG=False)
server.addEventCallback(event=Events.NOTIFICATION, callback=frozenClientStorage.routeNotification)
server.addEventCallback(event=Events.CONNECTION, callback=Callbacks.newConnection)
server.addEventCallback(event=Events.TERMINATION, callback=Callbacks.clientTerminated)
server.start()