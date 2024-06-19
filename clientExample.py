import Nebworking.nebworking as nebworking
from Nebworking import packets
print("I'm the client")
HOST = "192.168.0.58"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
client = nebworking.clientTCP(SERVERIP=HOST, SERVERPORT=PORT, DEBUG=False)
client.start()
client.waitForConnectionPacket()
client.sendData("Example of communication, clientTCP.sendData can send any bytes object, packet switching is handled by the library for both clients and servers.".encode(encoding=client.ENCODING))
while True:
    NOTIFICATION = client.getNotification()
    if not NOTIFICATION:
        continue
    
    print(NOTIFICATION.raw)
    
