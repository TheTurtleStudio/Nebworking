from Nebworking.multiclientHelper import ClientLogicTemplate as _ClientLogicTemplate
from threading import current_thread
from Nebworking.packets import PacketType
from Nebworking.packets import packetObject

class ClientLogic(_ClientLogicTemplate):
    def main(self):
        while True:
            notification = self.awaitQueue()
            header: packetObject = notification[0]
            packet: packetObject = notification[1]
            print(f"Received header: {header.raw}")
            print(f"Received packet: {packet.raw}")
            if packet.packetType == PacketType.CONNECTION:
                self.serverHook.sendData(data=b'Hello new connection!', destinationAddress=self.clientObject.ADDRESS)