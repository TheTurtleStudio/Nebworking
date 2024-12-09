import Nebworking.nebworking as nebworking
import Nebworking.packets as packets
from Nebworking.eventTypes import Events
import typing
from socket import socket

print("I'm the client")
HOST = "192.168.0.58"  # The server's hostname or IP address
PORT = 65432  # The port used by the server


    
class Client():
    def __init__(self):
        self.client = nebworking.clientTCP(SERVERIP=HOST, SERVERPORT=PORT, DEBUG=False)
        self.client.addEventCallback(event=Events.NOTIFICATION, callback=self.newNotification)
        self.client.addEventCallback(event=Events.CONNECTION, callback=self.newConnection)
        self.client.start()
        self.handleLogic()
        
    def handleLogic(self):
        #clientTCP runs on another thread so wait until we have a confirmed connection before using our client. Not *necessary*, just VERY highly advised.
        self.client.waitForConnectionPacket() 
        #An example of sending data to all the other connected clients. Server does get a relay notification informing them of the rerouting of packets. Server can also block this if configured.
        self.client.sendData(f'Hello other clients! Sincerely, {self.client.SOCKET.getsockname()}'.encode(encoding=self.client.ENCODING))
            
    
    
    '''START CALLBACKS'''
    def newNotification(self, notification: typing.Tuple[packets.packetObject, packets.packetObject]):
        print(f"Received header: {notification[0].raw}")
        print(f"Received packet: {notification[1].raw}")
        
    def newConnection(self, connection: socket):
        print(f"Connected to: {connection.getpeername()}")
        
client = Client()