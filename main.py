from __future__ import unicode_literals
import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

# import screen classes
from classes.chat import ChatScreen
from classes.lists import ListScreen
from classes.login import LoginScreen
from classes.register import RegisterScreen

# import socket io
from classes.socket_ import sio, connect_socket

# Kivy version required to run application
kivy.require("2.0.0")

# Set window size for the application
Window.size = (400, 650)

# Load ui screens
Builder.load_file('ui/login.kv')
Builder.load_file('ui/register.kv')
Builder.load_file('ui/lists.kv')
Builder.load_file('ui/chat.kv')

screen_manager = ScreenManager()

class ChatApp(App):
    def on_stop(self):
        sio.disconnect()
        return super().on_stop()

    def build(self):
        connect_socket()
        screen_manager.add_widget(LoginScreen(name='login'))
        screen_manager.add_widget(RegisterScreen(name='register'))
        screen_manager.add_widget(ChatScreen(name='chat'))
        screen_manager.add_widget(ListScreen(name='lists'))
        return screen_manager

if __name__ == '__main__':
    ChatApp().run()