import time
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
import socketio
from .popup import Alert
from .socket_ import sio
from operator import itemgetter

class RegisterScreen(Screen, Widget, socketio.Namespace):
    @sio.event(namespace='/register')
    def message(self, data):
        print('register ', data)
        self.user = data

    def __init__(self, **kw):
        self.user = None
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        print("yooks, works")
        return super().on_pre_enter(*args)

    def register(self):
        fullname = self.fullname.text
        username = self.username.text
        password = self.password.text

        if username and password is not None:
            sio.emit('auth', {
                'fullname': fullname,
                'username': username, 
                'password': password
                }, namespace='/register', callback=self.message)
            time.sleep(0.05)

            if self.user is not None:
                status = itemgetter('status')(self.user)
                if status == 'error':
                    print('Error message!', self.user)
                    Alert('Register Error', 'Something went wrong. Try again')
                else:
                    Alert('Successful', 'User account created successfully')
                    self.manager.current = 'login'