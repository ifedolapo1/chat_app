# import websocket client
import socketio

# initialize socket client
sio = socketio.Client()
sio_connect = 'http://localhost:5000'

@sio.event
def connect():
    print('Established connection')

@sio.event
def connect_error(data):
    print("The connection failed! : start server_app.py before running the application")
    return

@sio.on('login')
def login(sid, data):
    print(data)

@sio.event
def disconnect():
    print('Disconnected from server')

def connect_socket():
    sio.connect(sio_connect, wait=True, wait_timeout=100)
    # sio.wait()
