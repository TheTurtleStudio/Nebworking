import nebworking, packets, typing, eventTypes

print("I'm the server")
HOST = "192.168.0.58"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

class Callbacks():
    @staticmethod
    def newNotification(notification: typing.Tuple[packets.packetObject, packets.packetObject]):
        print(f"Received header: {notification[0].raw}")
        print(f"Received packet: {notification[1].raw}")


server = nebworking.serverTCP(IP=HOST, PORT=PORT, DEBUG=False)
server.addEventCallback(event=eventTypes.Events.NOTIFICATION, callback=Callbacks.newNotification)
server.start()