from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from unicodedata import name
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.app import App
import kivy
kivy.require("2.0.0")


class ChatScreen(Screen, Widget):
    pass


class RegisterScreen(Screen, Widget):
    pass


class LoginScreen(Screen, Widget):
    username = ObjectProperty(None)
    password = ObjectProperty(None)

    def reset(self):
        self.username.text = ''
        self.password.text = ''

    def submit(self):
        popupAlert('Authentication Failed', 'Bad Credentials')
        screen_manager.current = 'chat'


def popupAlert(title, text):
    popup = Popup(title=title, content=Label(text=text),
                  size_hint=(None, None), size=(300, 300))
    popup.open()


screen_manager = ScreenManager()


class ChatApp(App):
    def build(self):
        screen_manager.add_widget(LoginScreen(name='login'))
        screen_manager.add_widget(RegisterScreen(name='register'))
        screen_manager.add_widget(ChatScreen(name='chat'))

        return screen_manager


if __name__ == '__main__':
    ChatApp().run()
