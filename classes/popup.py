from kivy.uix.label import Label
from kivy.uix.popup import Popup

def Alert(title, text):
    popup = Popup(title=title, content=Label(text=text),
                  size_hint=(None, None), size=(300, 300))
    popup.open()