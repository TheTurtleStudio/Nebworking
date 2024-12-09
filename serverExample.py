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



class Server():
    def __init__(self):
        self.server = nebworking.serverTCP(IP=HOST, PORT=PORT, DEBUG=False)
        self.server.addEventCallback(event=Events.NOTIFICATION, callback=frozenClientStorage.routeNotification)
        self.server.addEventCallback(event=Events.CONNECTION, callback=self.newConnection)
        self.server.addEventCallback(event=Events.TERMINATION, callback=self.clientTerminated)
        self.server.start()
    
    
    
    '''START CALLBACKS'''
    def routeNotification(self, notification: typing.Tuple[packets.packetObject, packets.packetObject]):
        '''I can be used to route to NOTIFICATION events to client logic systems, but right now this is being handled by the FrozenClient system.'''
        pass
        
    def newConnection(self, clientObject: objects.clientObject):
        print(f"New connection: {clientObject.ADDRESS}")
        #Create a new clientLogic instance to handle the logic for the new client.
        frozenClientStorage.addFrozenClient(clientObject=clientObject, clientLogic=clientLogicsExample.ClientLogic, serverObject=self.server)
            
    def clientTerminated(self, clientObject: objects.clientObject):
        print(f"Connection terminated: {clientObject.ADDRESS}")
        frozenClientStorage.removeFrozenClient(clientObject=clientObject)
        
server = Server()