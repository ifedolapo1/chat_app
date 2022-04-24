from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from encryption import ECC_decrypt, ec_curve
from store import store
import socketio  # Import from python library
from .socket_ import sio
import tinyec.ec as ec

__self = None
class ChatScreen(Screen, Widget, socketio.Namespace):
    chat_id = None
    lists_screen = None
    login_screen = None

    # function that automatically runs before screen display
    def on_pre_enter(self, *args):
        global __self
        __self = self
        # get screen class of login
        __self.login_screen = self.manager.get_screen('login')
        # get screen class of lists
        __self.lists_screen = self.manager.get_screen('lists')
        __self.chat_id = __self.lists_screen.user_chat_id # get lists screen user chat id
        Window.set_title('Chat with ::: ' + __self.lists_screen.user_chat_fullname) # set window title to user chat name
        print('chat id: ', __self.chat_id)
        self.lists.text = ''

    # event that is fired when client recieved an emiited event from server
    @sio.on('chat')
    def message(data):
        global __self
        print(sio.get_sid())
        __self.receive_message(data)

    def receive_message(self, data):
        print('Received emitted message: ', data)
        print(data['from_id'], '--------', __self.chat_id)
        if data['from_id'] == __self.chat_id:
            message = eval(data['message'])
            ciphertextPubKeyG = ec.Point(ec_curve, message['ciphertextPubKeyX'], message['ciphertextPubKeyY']) # generate ciphertext public key from Elliptic curve Point
            message_to_tuple = (message['ciphertext'], message['nonce'], message['authTag'], ciphertextPubKeyG)
            decrypted_message = ECC_decrypt(message_to_tuple, int(__self.login_screen.user['private_key'])) # decrypt the encrypted message
            self.lists.text += data['from_name'] + ' : ' + decrypted_message.decode('utf-8') + '\n'

    # function to send message to another user
    def send_message(self):
        text_input = self.input.text
        sio.emit('chat', {
            'to_id': str(__self.chat_id),
            'message': str(text_input)
        })
        print('input : ', text_input)
        self.lists.text += __self.lists_screen.user_chat_fullname + ' ::: ' + str(text_input) + '\n'
        self.input.text = ''