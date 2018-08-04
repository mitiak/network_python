#!/usr/bin/env python3
import socket
'''
Multiconnection client implementation from 
https://realpython.com/python-sockets/
'''
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

#create the socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print('[before binding]: s={}'.format(s))

    s.bind((HOST, PORT))
    print('s.bind(({}, {}))'.format(HOST, PORT))
    print('[after binding]: s={}'.format(s))
    
    s.listen()
    print('s.listen()')

    
    conn, addr = s.accept()
    print('conn, addr = s.accept()')
    print('conn={}\n, addr={}'.format(repr(conn), repr(addr)))

    with conn:
        print('Connected: ' + str(addr))

        while True:
            print('Waiting for data')
            data = conn.recv(1024) # Blocking
            print('Recieved:', data)
            if not data:
                break
            conn.sendall(data)


    



    