from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from store import store
import socketio  # Import from python library
from .popup import Alert
from .socket_ import sio

class ChatScreen(Screen, Widget):
    def send_message(self):
        # username = store.get('auth')['uname'] if store.exists('auth') else ''
        text_input = self.input.text
        sio.emit('chat', {
            'username': 'hello',
            'message': str(text_input)
        }, namespace='/chat')
        print('input : ', text_input)
        self.lists.text += ' : ' + str(text_input) + '\n'
        self.input.text = ''