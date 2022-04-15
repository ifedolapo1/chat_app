import time
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen

import socketio  # Import from python library
from .popup import Alert
from .socket_ import sio
from store import store
from operator import itemgetter

# Login screen class for GUI and logic function
class LoginScreen(Screen, Widget, socketio.Namespace):
    @sio.event(namespace='/login')
    def message(self, data):
        print(data)
        self.user = data
        
    def __init__(self, **kw):
        self.user = None
        super().__init__(**kw)
        
    # Login function that connects to the server and authenticate user
    def login(self):
        # Get user text input from TextInput username Kivy Widget using id as identifier
        username = self.username.text
        # Get user text input from TextInput password Kivy Widget using id as identifier
        password = self.password.text

        if username and password is not None:
            sio.emit('auth', {'username': username, 'password': password}, namespace='/login', callback=self.message)
            time.sleep(0.3)

            if self.user is not None:
                status = itemgetter('status')(self.user)
                if status == 'error':
                    print('Error message!', self.user)
                    Alert('Authentication Error', 'Invalid Credentials')
                else:
                    id, username = itemgetter('id', 'username')(self.user)
                    print('Success message!', self.user)
                    # store.put(self, 'auth', {
                    #     'id': str(id),
                    #     'username': str(username)
                    # })
                    Alert('Authentication Success', 'You are now logged in')
                    self.manager.current = 'lists'