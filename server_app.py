from twisted.internet import reactor
from twisted.internet import protocol
from kivy.uix.label import Label
from kivy.app import App
from kivy.support import install_twisted_reactor
import sqlite3
# Uncomment below line if you don't have twisted reactor installed
# install_twisted_reactor()


class EchoServer(protocol.Protocol):
    def dataReceived(self, data):
        print(data)
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
        self.sql_build()
        self.label = Label(text='server started\n')
        reactor.listenTCP(8000, EchoServerFactory(self))
        return self.label

    def sql_build(self):
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        # Check if table exists in database before creating
        cur.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username, password)")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY, from_username, to_username, text,  enc_text, time)")

        con.commit()
        con.close()

    def handle_message(self, msg):
        msg = msg.decode('utf-8')
        self.label.text = "received:  {}\n".format(msg)

        if msg == "send":
            msg = "received"
        self.label.text += "responded: {}\n".format(msg)
        return msg.encode('utf-8')


if __name__ == '__main__':
    TwistedServerApp().run()
