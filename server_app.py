import socketio
import eventlet
from database import con, cur, runSqlDatabase 
import hashlib # Hashing Method from Python library
from operator import itemgetter
import tinyec.ec as ec

from encryption import ECC_encrypt, generateUserPrivateKey, generateUserPublicKey, ec_curve

sio = socketio.Server() # Create a web socket server
app = socketio.WSGIApp(sio) # Wrap socket in a WSGI application

""" 

Socket event that fires when a client connects
to the real-time server
@def connect function
@params sid, environ
"sid" is the client generate Session ID
"environ" is the client connection details

@def save_session
Function to save client session details for later use

"""
@sio.event
def connect(sid, environ):
    print('User current sid', sid)
    sio.save_session(sid, {'username': None})

@sio.on('message')
def my_message(event, sid, data):
    print('message ', data)

""" 

Socket event that is fired when the client requests
to login using a username and a password.

@params sid, data
"sid" is the client generate Session ID
"data" is the information passed from client emitted event

"""
@sio.on('login')
def login(sid, data):
    # destructure "data" to get "username", "password"
    username, password = itemgetter('username', 'password')(data)
    # Secure user password using md5 hash method
    secure_password = hashlib.md5(password.encode()).hexdigest()
    # Fetch details from SQLite database if "username" and "password"
    # is correct and available.
    user = cur.execute("SELECT id, fullname, username, private_key FROM users WHERE username = '%s' AND password = '%s'" % (username, secure_password)).fetchone()
    con.commit() # commit database execution
    print(user)
    if user is None:
        return {
            'status': 'error',
            'id': None
        }
    # Set client "sid" session ID to session_id of user identified by username
    cur.execute("UPDATE users SET session_id = '%s' WHERE username = '%s'" % (sid, username))
    con.commit() # commit database execution
    key = eval(user[3])
    # create user data dict object
    user_data = {
        'status': 'success',
        'id': str(user[0]),
        'fullname': str(user[1]),
        'username': str(user[2]),
        'private_key': key['private_key'],
        'public_key_X': key['public_key_X'],
        'public_key_Y': key['public_key_Y']
    }
    # set user info to session storage
    with sio.session(sid) as session:
        session['id'] = str(user[0])
        session['fullname'] = str(user[1])
        session['username'] = str(user[2])
        session['session'] = str(user[3])
        session['private_key'] = key['private_key'],
        session['public_key_X'] = key['public_key_X'],
        session['public_key_Y'] = key['public_key_Y']
    return user_data


""" 

Socket event that is fired when the client requests
to register using a "fullname", "username" and a "password".

@params sid, data
"sid" is the client generate Session ID
"data" is the information passed from client emitted event

"""
@sio.on('auth', namespace='/register')
def register(sid, data):
    # destructured "fullname", "username", "password" from data
    fullname, username, password = itemgetter('fullname', 'username', 'password')(data)
    secure_password = hashlib.md5(password.encode()).hexdigest()

    print('Name: ', fullname, ' Username: ', username)
    # check if user already exists to avoid duplicate account
    user_exists = cur.execute("SELECT username FROM users WHERE username = '%s'" % (username)).fetchone()
    con.commit()
    if user_exists is not None:
        return {
            'status': 'error',
            'id': None
        }
    else:
        user_private_key = generateUserPrivateKey() # generates private key for user
        user_public_key = generateUserPublicKey(user_private_key) # generate user public key
        key = {
            'private_key': user_private_key,
            'public_key_X': user_public_key.x,
            'public_key_Y': user_public_key.y,
        }
        # insert data into the user table to create a new user account
        user = cur.execute("INSERT INTO users(fullname, username, password, private_key) VALUES(?, ?, ?, ?)", (fullname, username, secure_password, format(key)))
        con.commit() # commit database execution
        print('user: ', user)
        return {
            'status': 'success'
        }


""" 

Socket event that is fired when the client requests
to fetch lists of available users to chat

@params sid, data
"sid" is the client generate Session ID
"data" is the information passed from client emitted event
"data" is empty as we don't need request data

"""
@sio.on('user_lists')
def lists(sid, data):
    session = sio.get_session(sid) # get user data from session storage
    user_id = session['id'] # get user id from session
    # fetch lists of user from the database while excluding current logged in user
    user_lists = cur.execute("SELECT id, fullname, username FROM users WHERE id != '%s'" % (str(user_id))).fetchall()

    if user_lists != []:
        # print('User lists', user_lists)
        # emit event to the request client session id
        # using the "to" @param
        return sio.emit('user_lists', user_lists, to=sid)
    else:
        return None


""" 

Socket event that is fired when the client requests
to send a chat message to another user

@params sid, data
"sid" is the client generate Session ID
"data" is the information passed from client emitted event

"""
@sio.on('chat')
def chat(sid, data):
    session = sio.get_session(sid) # get user data from session storage
    print('chat', data)
    # destructure "to_id", "message" from "data"
    to_id, message = itemgetter('to_id', 'message')(data)
    # mine_user_private_key = cur.execute("SELECT private_key FROM users WHERE id = '%s'" % (str(session['id']))).fetchone()
    mine_user_private_key = session['private_key'] # get private key from session storage
    print('encrypted private key: ', mine_user_private_key)
    # fetch receiver session_id and private_key
    user = cur.execute("SELECT session_id, private_key, fullname FROM users WHERE id = '%s'" % (to_id)).fetchone()
    to_session_id = user[0] # get receiver "session_id"
    key = eval(user[1]) # evaluate given data to tuple/dict
    user_public_key = ec.Point(ec_curve, key['public_key_X'], key['public_key_Y']) # get public key using Elliptic curve Point
    # encrypt sender message
    encrypted_message = ECC_encrypt(bytes(message, 'utf-8'), user_public_key, int(mine_user_private_key[0]))

    # create encrypted message dict object
    encrypted_message_obj = {
        'ciphertext': encrypted_message[0],
        'nonce': encrypted_message[1],
        'authTag': encrypted_message[2],
        'ciphertextPubKeyX': encrypted_message[3].x,
        'ciphertextPubKeyY': encrypted_message[3].y,
        'ciphertextPubKey': hex(encrypted_message[3].x) + hex(encrypted_message[3].y % 2)[2:]
    }

    print('encrypted message object: ', encrypted_message_obj)

    # insert chat message into the database
    cur.execute("INSERT INTO chats(from_id, from_fullname, from_username, to_id, encrypted_message) VALUES(?, ?, ?, ?, ?)", (session['id'], session['fullname'], session['username'], str(to_id), format(encrypted_message_obj)))
    con.commit() # execute database 

    # emit chat event to receiver socket "session_id"
    sio.emit('chat', {
        'from_id': session['id'], 
        'from_name': user[2],
        'from_username': session['username'],
        'to_id': to_id,
        'to_session_id': to_session_id,
        'to_private_key': user[1],
        'message': format(encrypted_message_obj)
    }, skip_sid=sid, to=to_session_id)

# event fired on client disconnection
@sio.event
def on_disconnect(sid):
    print('disconnect ', sid)

""" 
main chat class to run initial sqlite database and start the server
"""
class ChatServerApp():
    def __init__(self) -> None:
        runSqlDatabase()
        eventlet.wsgi.server(eventlet.listen(('', 5000)),app)

if __name__ == '__main__':
    ChatServerApp()