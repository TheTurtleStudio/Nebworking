import Nebworking.nebworking as nebworking
import Nebworking.packets as packets
from Nebworking.eventTypes import Events
import typing
from socket import socket

print("I'm the client")
HOST = "192.168.0.58"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

class Callbacks():
    @staticmethod
    def newNotification(notification: typing.Tuple[packets.packetObject, packets.packetObject]):
        print(f"Received header: {notification[0].raw}")
        print(f"Received packet: {notification[1].raw}")
        
    @staticmethod
    def newConnection(connection: socket):
        print(f"Connected to: {connection.getpeername()}")


client = nebworking.clientTCP(SERVERIP=HOST, SERVERPORT=PORT, DEBUG=False)
client.addEventCallback(event=Events.NOTIFICATION, callback=Callbacks.newNotification)
client.addEventCallback(event=Events.CONNECTION, callback=Callbacks.newConnection)
client.start()
client.waitForConnectionPacket() #clientTCP runs on another thread so wait until we have a confirmed connection before using our client. Not *necessary*, just VERY highly advised.

#An example of sending data to all the other connected clients. Server does get a relay notification informing them of the rerouting of packets. Server can also block this if configured.
client.sendData(f'Hello other clients! Sincerely, {client.SOCKET.getsockname()}'.encode(encoding=client.ENCODING))

    
