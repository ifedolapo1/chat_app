import time
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen

import socketio  # Import from python library
from .popup import Alert
from .socket_ import sio
from store import store
from operator import itemgetter

__self = None

# Login screen class for GUI and logic function
class LoginScreen(Screen, Widget, socketio.Namespace):
    def __init__(self, **kw):
        self.user = None
        super().__init__(**kw)
    
    def on_pre_enter(self, *args):
        global __self
        __self = self
    
    # callback event that is fired when server returns request from emitted event
    @sio.on('login')
    def message(self, data):
        print("Login socket request callback: ", data)
        self.user = data
        
    # Login function that connects to the server and authenticate user
    def login(self):
        # Get user text input from TextInput username Kivy Widget using id as identifier
        username = self.username.text
        # Get user text input from TextInput password Kivy Widget using id as identifier
        password = self.password.text

        if username and password is not None:
            sio.emit('login', {'username': username, 'password': password}, callback=self.message) # reference line 24
            time.sleep(0.05)

            if self.user is not None:
                status = itemgetter('status')(self.user)
                if status == 'error':
                    print('Error message!', self.user)
                    Alert('Authentication Error', 'Invalid Credentials')
                else:
                    fullname, username = itemgetter('fullname', 'username')(self.user)
                    Window.set_title('Welcome - ' + fullname) # set window title to fullname
                    print('Success message!', self.user)
                    Alert('Authentication Success', 'You are now logged in \n as the username ' + username)

                    # set textinput box to empty
                    self.username.text = ''
                    self.password.text = ''
                    
                    # switch screen to lists
                    self.manager.current = 'lists'