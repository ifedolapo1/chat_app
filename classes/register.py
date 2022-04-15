from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
import sqlite3  # Import from python library
import hashlib # Hashing Method from Python library
from . import popup

class RegisterScreen(Screen, Widget):
    def on_pre_enter(self, *args):
        print("yooks, works")
        return super().on_pre_enter(*args)

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
                return popup.Alert('Error', 'User account exists already')

            cur.execute("INSERT INTO users(username, password) VALUES(?, ?)",
                        (username, password))
            popup.Alert('Successful', 'User account created successfully')
            self.manager.current = 'login'
            con.commit()