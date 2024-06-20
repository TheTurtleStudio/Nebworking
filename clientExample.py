import Nebworking.nebworking as nebworking
from Nebworking import packets
print("I'm the client")
HOST = "192.168.0.58"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
client = nebworking.clientTCP(SERVERIP=HOST, SERVERPORT=PORT, DEBUG=False)
client.start()
client.waitForConnectionPacket()
client.sendData(f'Hello other clients! Sincerely, {client.SOCKET.getsockname()}'.encode(encoding=client.ENCODING), destinationAddress=packets.AddressType.OTHERS())
while True:
    NOTIFICATION = client.getNotification()
    if not NOTIFICATION:
        continue
    
    print(NOTIFICATION.raw)
    
