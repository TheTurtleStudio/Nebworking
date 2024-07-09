import nebworking, packets, typing

print("I'm the server")
HOST = "192.168.0.58"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

class Callbacks():
    @staticmethod
    def handleRelayOverride(headerPacket: packets.packetObject, contentPacket: packets.packetObject):
        print("I'm the relay callback override defined by the end user. They can provide an override for the relay callback and handle the logic themselves here. This lets them decide if a packet gets relayed or not. They can highly configure packet relay logic, which can help with security and also adds modularity to the library.")

    @staticmethod
    def newNotification(notification: typing.Tuple[packets.packetObject, packets.packetObject]):
        print(f"Received header: {notification[0].raw}")
        print(f"Received packet: {notification[1].raw}")




server = nebworking.serverTCP(IP=HOST, PORT=PORT, DEBUG=False, NOTIFICATIONCALLBACK=Callbacks.newNotification)
server.start()