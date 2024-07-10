from Nebworking.multiclientHelper import ClientLogicTemplate as _ClientLogicTemplate
from threading import current_thread

class ClientLogic(_ClientLogicTemplate):
    def main(self):
        while True:
            notification = self.awaitQueue()
            print(f"Received header: {notification[0].raw}")
            print(f"Received packet: {notification[1].raw}")