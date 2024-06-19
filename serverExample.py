import pickle
import Nebworking.nebworking as nebworking
from Nebworking import packets
HOST = "192.168.0.58"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
server = nebworking.serverTCP(IP=HOST, PORT=PORT, DEBUG=False)
server.start()
server.NOTIFICATIONS
while True:
    if server.NOTIFICATIONS.empty():
        continue

    NOTIFICATION: packets.packetObject = server.NOTIFICATIONS.get()
    print(NOTIFICATION.raw)