#!/usr/bin/env python3

'''
Multiconnection server implementation from 
https://realpython.com/python-sockets/
'''
import socket
import selectors
import types
import os

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    print('[accept_wrapper] Entered accept_wrapper(sock)')
    conn, addr = sock.accept()  # Should be ready to read
    print('[accept_wrapper] accepted connection from', addr)
    print('[accept_wrapper] conn=', repr(conn))
    conn.setblocking(False) # Calls made to this socket will no longer block
    print('[accept_wrapper] conn.setblocking(False)')
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    print('[accept_wrapper] data=', repr(data))
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    print('[accept_wrapper] register conn to selector')

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    print('[service_connection '+ str(sock.fileno()) +'] Entered service_connection(key, mask)')
    print('[service_connection '+ str(sock.fileno()) +'] sock=', repr(sock))
    print('[service_connection '+ str(sock.fileno()) +'] data=', repr(data))
    print('[service_connection '+ str(sock.fileno()) +'] mask=', repr(mask))
    if mask & selectors.EVENT_READ:
        print('[service_connection '+ str(sock.fileno()) +'] mask & selectors.EVENT_READ')
        recv_data = sock.recv(1024)  # Should be ready to read
        print('[service_connection '+ str(sock.fileno()) +'] recv_data=',repr(recv_data))
        if recv_data:
            data.outb += recv_data
        else:
            print('[service_connection '+ str(sock.fileno()) +'] closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        print('[service_connection '+ str(sock.fileno()) +'] mask & selectors.EVENT_WRITE')
        if data.outb:
            print('[service_connection '+ str(sock.fileno()) +'] Writing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
        else:
            print('[service_connection '+ str(sock.fileno()) +'] No data to write')

# Create listener socket
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('[main] lsock created: {}'.format(repr(lsock)))
lsock.bind((HOST, PORT))
print('[main] lsock binded: {}'.format(repr(lsock)))
lsock.listen()
print('[main] listening on', (HOST, PORT))

# Calls made to this socket will no longer block
lsock.setblocking(False)
print('[main] lsock.setblocking(False)')

# Registers the socket to be monitored with sel.select() 
# for the events you’re interested in. For the listening
# socket, we want read events: selectors.EVENT_READ
sel.register(lsock, selectors.EVENT_READ, data=None)
print('[main] sel.register(lsock, selectors.EVENT_READ, data=None)')


while True:
    print('\n[main loop] going to select()')
    events = sel.select(timeout=None)
    
    for key, mask in events:
        print('[main loop] key.data={}'.format(repr(key.data)))
        print('[main loop] mask={}'.format(repr(mask)))
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)

