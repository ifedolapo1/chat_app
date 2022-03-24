from kivy.app import App
from kivy.uix.label import Label
from twisted.internet import protocol
from twisted.internet import reactor
from kivy.support import install_twisted_reactor

# Uncomment below line if you don't have twisted reactor installed
# install_twisted_reactor()


class EchoServer(protocol.Protocol):
    def dataReceived(self, data):
        response = self.factory.app.handle_message(data)
        if response:
            self.transport.write(response)


class EchoServerFactory(protocol.Factory):
    protocol = EchoServer

    def __init__(self, app):
        self.app = app


class TwistedServerApp(App):
    label = None

    def build(self):
        self.label = Label(text='server started\n')
        reactor.listenTCP(8000, EchoServerFactory(self))
        return self.label

    def handle_message(self, msg):
        msg = msg.decode('utf-8')
        self.label.text = "received:  {}\n".format(msg)

        if msg == "ping":
            msg = "Pong"
        if msg == "plop":
            msg = "Kivy Rocks!!!"
        self.label.text += "responded: {}\n".format(msg)
        return msg.encode('utf-8')


if __name__ == '__main__':
    TwistedServerApp().run()
