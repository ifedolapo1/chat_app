from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.clock import Clock
import sqlite3  # Import from python library
from store import store

class ListScreen(Screen, Widget):
    last_fetch_id = 0
    user_chat_id = StringProperty()

    def on_pre_enter(self, *args):
        return super().on_pre_enter(*args)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.fetch_users, 2)

    def open_chat(self, instance, id):
        print(id)
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
                btn = Button(text=username, 
                             size_hint=(None, None), 
                             text_size=(self.width, None), 
                             padding=(30, 30))
                btn.fbind('on_press', self.open_chat, id=id)
                self.ids[str(id)] = btn
                self.boxlayout.add_widget(btn)
