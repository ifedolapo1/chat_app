from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from store import store
import socketio  # Import from python library
from .popup import Alert
from .socket_ import sio

__self = None
class ChatScreen(Screen, Widget, socketio.Namespace):
    chat_id = None

    def on_pre_enter(self, *args):
        global __self
        __self = self
        lists_screen = self.manager.get_screen('lists')
        __self.chat_id = lists_screen.user_chat_id
        Window.set_title('Chat with - ' + lists_screen.user_chat_fullname)
        print('chat id: ', __self.chat_id)
        self.lists.text = ''

    @sio.on('chat')
    def message(data):
        global __self
        print(sio.get_sid())
        __self.receive_message(data)

    def receive_message(self, data):
        print('Received emitted message: ', data)
        print(data['from_id'], '--------', __self.chat_id)
        if data['from_id'] == __self.chat_id:
            self.lists.text += ' : ' + str(data['message']) + '\n'

    def send_message(self):
        # username = store.get('auth')['uname'] if store.exists('auth') else ''
        text_input = self.input.text
        sio.emit('chat', {
            'to_id': str(__self.chat_id),
            'message': str(text_input)
        })
        print('input : ', text_input)
        self.lists.text += ' : ' + str(text_input) + '\n'
        self.input.text = ''