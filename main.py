from __future__ import unicode_literals
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor
from kivy.uix.label import Label
import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.support import install_twisted_reactor
import sqlite3  # Import from python library
from kivy.storage.jsonstore import JsonStore
import hashlib  # Hashing Method from Python library
from kivy.clock import Clock
# install_twisted_reactor()


""" class EchoClient(Protocol):
    def connectionMade(self):
        print(self)
        print("test connection here")
        self.factory.app.on_connection(self.transport)

    def dataReceived(self, data):
        response = self.factory.app.print_message(data.decode('utf-8'))
        if response:
            self.transport.write(response)


class EchoClientFactory(ClientFactory):
    protocol = EchoClient

    def __init__(self, app):
        self.app = app
        # protocol.connectionMade(self)
        # print(protocol.connectionMade(self))

    def startedConnecting(self, connector):
        self.app.print_message('Started to connect!')

    def clientConnectionLost(self, connector, reason):
        self.app.print_message('Connection lost!')

    def clientConnectionFailed(self, connector, reason):
        self.app.print_message('Connection failed!') """


kivy.require("2.0.0")
# Kivy version required to run application

# Declare which json file to use and assign to the variable store
store = JsonStore('auth.json')

if store.exists('auth'):  # Check if key exists
    store.delete('auth')  # Delete key if it exists


class LoginScreen(Screen, Widget):  # Login screen class for GUI and logic function

    # Login function that connects to the database and authenticate user
    def login(self):  # Declare login function
        # Uses SQLite to connect to file-based database named "database.db"
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        # Get user text input from TextInput username Kivy Widget using id as identifier
        username = self.ids['username'].text
        # Get user text input from TextInput password Kivy Widget using id as identifier
        password = self.ids['password'].text
        if username and password is not None:
            # Secure user password using md5 hash method
            password = hashlib.md5(password.encode()).hexdigest()
            print(username, " ", password)
            user_exists = cur.execute(
                "SELECT username FROM users WHERE username = '%s' AND password = '%s'" % (username, password)).fetchone()
            if user_exists is None:
                return popupAlert('Authentication Error', 'Invalid Credentials')
            else:
                popupAlert('Authenticated', 'Logged in successfully')
                store.put('auth', uname=username)
                screen_manager.current = 'lists'
                con.commit()


class ChatScreen(Screen, Widget):
    def send_message(self):
        username = store.get('auth')['uname'] if store.exists('auth') else ''
        text_input = self.input.text
        print('input : ', text_input)
        self.lists.text += username + ' : ' + str(text_input) + '\n'
        self.input.text = ''


class ListScreen(Screen, Widget):
    last_fetch_id = 0
    user_chat = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.fetch_users, 2)

    def open_chat(self, touch, id):
        print('you clicked here ', id)
        self.manager.current = 'chat'

    def fetch_users(self, dt):
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        username = store.get('auth')['uname'] if store.exists('auth') else ''
        users = cur.execute(
            "SELECT id, username FROM users WHERE username != '%s' AND id > '%d'" % (str(username), self.last_fetch_id)).fetchall()
        if users != []:
            print(users)
            for (id, username) in users:
                self.last_fetch_id = id
                # self.ids['lists'].text += ''.join(username) + '\n'
                id = str(id)
                self.boxlayout.add_widget(
                    Label(text=username + '\n', text_size=(self.width, None), padding=(30, 30), on_touch_down=self.open_chat))


class RegisterScreen(Screen, Widget):
    def register(self):
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        username = self.ids['username'].text
        password = self.ids['password'].text
        if username and password is not None:
            password = hashlib.md5(password.encode()).hexdigest()
            print(username, " ", password)
            user_exists = cur.execute(
                "SELECT username FROM users WHERE username = '%s'" % (username)).fetchone()
            if user_exists is not None:
                return popupAlert('Error', 'User account exists already')

            cur.execute("INSERT INTO users(username, password) VALUES(?, ?)",
                        (username, password))
            popupAlert('Successful', 'User account created successfully')
            self.manager.current = 'login'
            con.commit()


def popupAlert(title, text):
    popup = Popup(title=title, content=Label(text=text),
                  size_hint=(None, None), size=(300, 300))
    popup.open()


screen_manager = ScreenManager()


class ChatApp(App):
    connection = None
    textbox = None
    label = None

    def build(self):
        # root = self.setup_gui()
        # self.connect_to_server()
        screen_manager.add_widget(LoginScreen(name='login'))
        screen_manager.add_widget(RegisterScreen(name='register'))
        screen_manager.add_widget(ChatScreen(name='chat'))
        screen_manager.add_widget(ListScreen(name='lists'))
        return screen_manager

    """ def setup_gui(self):
        self.textbox = TextInput(size_hint_y=.05, multiline=False)
        self.textbox.bind(on_text_validate=self.send_message)
        self.label = Label(text='connecting...\n')
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.label)
        layout.add_widget(self.textbox)
        return layout

    def connect_to_server(self):
        reactor.connectTCP('localhost', 8000, EchoClientFactory(self))

    def on_connection(self, connection):
        print("Successful connection.")
        self.connection = connection
        msg = 'Sending message'
        self.connection.write(msg.encode('utf-8'))
        print(type(connection))

    def send_message(self, *args):
        msg = self.textbox.text
        print(msg)
        print(self.connection)
        if msg and self.connection:
            self.connection.write(msg.encode('utf-8'))
            self.textbox.text = ""

    def print_message(self, msg):
        self.label.text += "{}\n".format(msg) """


if __name__ == '__main__':
    ChatApp().run()
