import sqlite3
import socketio
import eventlet
import sqlite3  # Import from python library
from database import con, cur, runSqlDatabase 
import hashlib # Hashing Method from Python library
from operator import itemgetter

from encryption import generateUserPrivateKey

sio = socketio.Server() # Create a web socket server
app = socketio.WSGIApp(sio) # Wrap socket in a WSGI application

user_session = None

@sio.event
def connect(sid, environ):
    sio.save_session(sid, {'username': None})
    print('connect sid', sid)
    # print('connect environ', environ)

@sio.on('message')
def my_message(event, sid, data):
    print('message ', data)

@sio.on('login')
def login(sid, data):
    global user_session
    print('login sid', sid)
    username, password = itemgetter('username', 'password')(data)
    # Secure user password using md5 hash method
    secure_password = hashlib.md5(password.encode()).hexdigest()
    print(username, " - ", password)
    user = cur.execute("SELECT id, fullname, username, session_id FROM users WHERE username = '%s' AND password = '%s'" % (username, secure_password)).fetchone()
    con.commit()
    print(user)
    if user is None:
        return {
            'status': 'error',
            'id': None
        }
    
    cur.execute("UPDATE users SET session_id = '%s' WHERE username = '%s'" % (sid, username))
    con.commit()
    user_data = {
        'status': 'success',
        'id': str(user[0]),
        'fullname': str(user[1]),
        'username': str(user[2])
    }
    with sio.session(sid) as session:
        session['id'] = str(user[0])
        session['fullname'] = str(user[1])
        session['username'] = str(user[2])
        session['session'] = str(user[3])
    user_session = user_data
    return user_data

@sio.on('auth', namespace='/register')
def register(sid, data):
    fullname, username, password = itemgetter('fullname', 'username', 'password')(data)
    secure_password = hashlib.md5(password.encode()).hexdigest()

    print('Name: ', fullname, ' Username: ', username)
    user_exists = cur.execute("SELECT username FROM users WHERE username = '%s'" % (username)).fetchone()
    con.commit()
    if user_exists is not None:
        return {
            'status': 'error',
            'id': None
        }
    else:
        user_private_key = generateUserPrivateKey()
        user = cur.execute("INSERT INTO users(fullname, username, password, private_key) VALUES(?, ?, ?, ?)", (fullname, username, secure_password, str(user_private_key)))
        con.commit()
        print('user: ', user)
        return {
            'status': 'success'
        }

@sio.on('user_lists')
def lists(sid, data):
    session = sio.get_session(sid)
    print('user lists sid', sid)
    user_id = session['id']
    user_lists = cur.execute("SELECT id, fullname, username FROM users WHERE id != '%s'" % (str(user_id))).fetchall()

    if user_lists != []:
        # print('User lists', user_lists)
        return sio.emit('user_lists', user_lists, to=sid)
    else:
        return None



@sio.on('chat')
def chat(sid, data):
    session = sio.get_session(sid)
    print('chat sid', sid)
    print('chat', data)
    to_id, message = itemgetter('to_id', 'message')(data)
    to_session_id = cur.execute("SELECT session_id FROM users WHERE id = '%s'" % (to_id)).fetchone()
    save_chat = cur.execute("INSERT INTO chats(from_id, from_name, from_username, to_id, message) VALUES(?, ?, ?, ?, ?)", (session['id'], session['fullname'], session['username'], to_id))
    con.commit()
    sio.emit('chat', {
        'from_id': session['id'], 
        'from_name': session['fullname'],
        'from_username': session['username'],
        'to_id': to_id,
        'to_session_id': to_session_id,
        'message': message
    }, skip_sid=sid, to=to_session_id)

@sio.event
def on_disconnect(sid):
    print('disconnect ', sid)


class ChatServerApp():
    def __init__(self) -> None:
        runSqlDatabase()
        eventlet.wsgi.server(eventlet.listen(('', 5000)),app)

if __name__ == '__main__':
    ChatServerApp()