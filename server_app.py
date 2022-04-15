import sqlite3
import socketio
import eventlet
import sqlite3  # Import from python library
from database import con, cur, runSqlDatabase 
import hashlib # Hashing Method from Python library
from operator import itemgetter

sio = socketio.Server() # Create a web socket server
app = socketio.WSGIApp(sio) # Wrap socket in a WSGI application

@sio.event
def connect(sid, environ):
    # sio.save_session(sid, {'username': None})
    print('connect ', sid)

@sio.on('message')
def my_message(event, sid, data):
    print('message ', data)

@sio.on('auth', namespace='/login')
def login(sid, data):
    print('sid', sid)
    username, password = itemgetter('username', 'password')(data)
    # Secure user password using md5 hash method
    secure_password = hashlib.md5(password.encode()).hexdigest()
    print(username, " - ", password)
    user = cur.execute("SELECT id, username FROM users WHERE username = '%s' AND password = '%s'" % (username, secure_password)).fetchone()
    con.commit()
    print(user)
    if user is None:
        return {
            'status': 'error',
            'id': None
        }
    user_data = {
        'status': 'success',
        'id': str(user[0]),
        'username': str(user[1])
    }
    with sio.session(sid) as session:
        session['username'] = str(user[1])
        session['id'] = str(user[0])
    return user_data

@sio.on('chat', namespace='/chat')
def chat(sid, data):
    print('chat', data)
    pass

@sio.event
def on_disconnect(sid):
    print('disconnect ', sid)


class ChatServerApp():
    def __init__(self) -> None:
        runSqlDatabase()
        eventlet.wsgi.server(eventlet.listen(('', 5000)),app)

if __name__ == '__main__':
    ChatServerApp()