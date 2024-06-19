import pickle
import Nebworking.nebworking as nebworking
from Nebworking import packets
print("I'm the server")
HOST = "192.168.0.58"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
server = nebworking.serverTCP(IP=HOST, PORT=PORT, DEBUG=False)
server.start()
while True:
    NOTIFICATION = server.getNotification()
    if not NOTIFICATION:
        continue
    
    print(NOTIFICATION.raw)
    if NOTIFICATION.packetType == packets.PacketType.PAYLOAD:
        server.sendData(NOTIFICATION.data['payload'])