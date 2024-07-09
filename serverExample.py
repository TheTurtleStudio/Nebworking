import Nebworking.nebworking as nebworking
import Nebworking.packets as packets
from Nebworking.eventTypes import Events
import Nebworking.objects as objects
import typing

print("I'm the server")
HOST = "192.168.0.58"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

class Callbacks():
    @staticmethod
    def newNotification(notification: typing.Tuple[packets.packetObject, packets.packetObject]):
        print(f"Received header: {notification[0].raw}")
        print(f"Received packet: {notification[1].raw}")
        
    @staticmethod
    def newConnection(clientObject: objects.clientObject):
        print(f"New connection: {clientObject.ADDRESS}")
        
    @staticmethod
    def clientTerminated(clientObject: objects.clientObject):
        print(f"Connection terminated: {clientObject.ADDRESS}")


server = nebworking.serverTCP(IP=HOST, PORT=PORT, DEBUG=False)
server.addEventCallback(event=Events.NOTIFICATION, callback=Callbacks.newNotification)
server.addEventCallback(event=Events.CONNECTION, callback=Callbacks.newConnection)
server.addEventCallback(event=Events.TERMINATION, callback=Callbacks.clientTerminated)
server.start()