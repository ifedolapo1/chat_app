from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.clock import Clock

import time
import socketio  # Import from python library
from store import store
from .socket_ import sio

__self = None

class ListScreen(Screen, Widget, socketio.Namespace):
    users = None
    user_chat_id = StringProperty()
    user_chat_fullname = StringProperty()
    login_screen = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        super(ListScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        global __self
        __self = self

        __self.login_screen = self.manager.get_screen('login')
        Window.set_title('Chat Lists - ' + __self.login_screen.user['username'])

        Clock.schedule_interval(__self.fetch_users, 2)
        return super().on_pre_enter(*args)

    @sio.on('user_lists')
    def message(users):
        global __self
        __self.users = users
    
    def fetch_users(self, dt):
        global __self
        __self.boxlayout.clear_widgets()
        sio.emit('user_lists', {})
        time.sleep(0.005)
        if __self.users is not None:
            for user in __self.users:
                (id, fullname, username) = tuple(user)
                __self.last_fetch_id = user[0]

                btn = Button(text=str(fullname), size_hint=(1, 1), padding=(30, 30), height=40)
                btn.fbind('on_press', __self.open_chat, id=id, fullname=fullname)
                __self.ids[str(id)] = btn
                __self.boxlayout.add_widget(btn)


    # function to open chat of selected user
    def open_chat(self, instance, id, fullname):
        self.user_chat_id = str(id)
        self.user_chat_fullname = str(fullname)
        self.manager.current = 'chat'

    # logout function
    def logout(self):
        self.login_screen.user = None
        self.manager.current = 'login'
        pass