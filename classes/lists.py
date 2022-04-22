from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.clock import Clock
import sqlite3

import time
import socketio  # Import from python library
from store import store
from .socket_ import sio

__self = None

class ListScreen(Screen, Widget, socketio.Namespace):
    users = None
    user_chat_id = StringProperty()
    user_chat_fullname = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        super(ListScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        global __self
        __self = self

        login_screen = self.manager.get_screen('login')
        Window.set_title('Chat Lists - ' + login_screen.user['username'])

        Clock.schedule_interval(__self.fetch_users, 2)
        return super().on_pre_enter(*args)

    @sio.on('user_lists')
    def message(users):
        global __self
        __self.users = users
        # print('User lists: ', users)
    
    def fetch_users(self, dt):
        global __self
        __self.boxlayout.clear_widgets()
        sio.emit('user_lists', {})
        time.sleep(0.005)
        if __self.users is not None:
            for user in __self.users:
                (id, fullname, username) = tuple(user)
                # print(tuple(user))
                __self.last_fetch_id = user[0]
                # self.ids['lists'].text += ''.join(username) + '\n'
                # print('id: ', id)
                # print('fullname: ', fullname)
                # print('username: ', username)
                btn = Button(text=str(username), size_hint=(1, .15), padding=(30, 30))
                btn.fbind('on_press', __self.open_chat, id=id, fullname=fullname)
                __self.ids[str(id)] = btn
                __self.boxlayout.add_widget(btn)


    def open_chat(self, instance, id, fullname):
        # print(id)
        self.user_chat_id = str(id)
        self.user_chat_fullname = str(fullname)
        self.manager.current = 'chat'