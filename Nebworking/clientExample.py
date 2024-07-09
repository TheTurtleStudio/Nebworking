import nebworking, packets, typing

print("I'm the client")
HOST = "192.168.0.58"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

class Callbacks():
    @staticmethod
    def newNotification(notification: typing.Tuple[packets.packetObject, packets.packetObject]):
        print(f"Received header: {notification[0].raw}")
        print(f"Received packet: {notification[1].raw}")


client = nebworking.clientTCP(SERVERIP=HOST, SERVERPORT=PORT, DEBUG=False, NOTIFICATIONCALLBACK=Callbacks.newNotification)
client.start()
client.waitForConnectionPacket() #Wait until we connect
print("Sending data using sendData")
client.sendData(f'Hello other clients! Sincerely, {client.SOCKET.getsockname()}'.encode(encoding=client.ENCODING), destinationAddress=packets.AddressType.OTHERS())

    
