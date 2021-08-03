from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import websocket
import threading
from time import time, sleep

clients = []
# pozClient = PozClient().test0()
class SimpleChat(WebSocket):
    def handleMessage(self):
        for client in clients:
            if client != self:
                client.sendMessage(self.address[0] + u' - ' + self.data)
                print

    def handleConnected(self):
        print(self.address, 'connected')
        for client in clients:
            client.sendMessage(self.address[0] + u' - connected')
        clients.append(self)

    def handleClose(self):
       clients.remove(self)
       print(self.address, 'closed')
       for client in clients:
          client.sendMessage(self.address[0] + u' - disconnected')

def getServer(port = 8001):
    server = SimpleWebSocketServer('', int(port), SimpleChat)
    threading.Thread(target=server.serveforever).start()
    print("server started,...")
    return server

def getClient(port = 8001):
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:"+str(port), origin="local")
    print("client started,...")
    return ws

def test0():
    running = True
    def sending(ws):
        while running:
            ws.send(f"hello, time = {time()}")
            # print("sending...")
            sleep(0.1)
    def receiving(ws):
        while running:
            txt = ws.recv()
            print("txt = ", txt)

    port = 8001
    server = getServer(port=port)
    sender = getClient(port=port)
    threading.Thread(target=sending, args=(sender,)).start()
    receiver = getClient(port=port)
    receiving(receiver)

if __name__=="__main__":
    test0()