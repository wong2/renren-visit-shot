# coding: utf-8

import socket
import struct
from config import SERVER_HOST, SERVER_PORT, SERVER_IPv6

def _get_socket():
    if SERVER_IPv6:
        s = socket.socket(socket.AF_INET6)
    else:
        s = socket.socket()
    s.connect((SERVER_HOST, SERVER_PORT))
    return s

def background_add_job(user_id, token, target):
    s = _get_socket()
    s.send("\x01")
    luid = len(user_id)
    ltoken = len(token)
    s.send(struct.pack('!B', luid))
    s.send(struct.pack('!B', ltoken))
    s.send(user_id + token)
    s.send(struct.pack('!I', target))
    s.close()

def background_del_job(user_id):
    s = _get_socket()
    s.send("\x02")
    luid = len(user_id)
    s.send(struct.pack('!B', luid))
    s.send(struct.pack('!B', 1))
    s.send(user_id)


def background_query_job(user_id):
    s = _get_socket()
    s.send("\x03")
    luid = len(user_id)
    s.send(struct.pack('!B', luid))
    s.send(struct.pack('!B', 1))
    s.send(user_id)
    ret = s.recv(13)
    ok = bool(struct.unpack('!B', ret[0])[0])
    now_val = struct.unpack('!I', ret[1:5])[0]
    timestamp = struct.unpack('!Q', ret[5:])[0]
    return (ok, now_val, timestamp)
