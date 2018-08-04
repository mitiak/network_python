#!/usr/bin/env python3

import socket
import time
import sys

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print('Socket created. s=', repr(s))
    time.sleep(3)
    s.connect((HOST, PORT))
    print('Socket connected to {}', str((HOST, PORT)))
    time.sleep(int(sys.argv[1]))
    s.sendall(b'Hello, World !')
    data = s.recv(1024)

print('Received: ', repr(data))
