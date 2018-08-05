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
server_str = 'Multi-conn server'

sel = selectors.DefaultSelector()

# Since the listening socket was registered for the event 
# selectors.EVENT_READ, it should be ready to read. We call 
# sock.accept() and then immediately call conn.setblocking(False) 
# to put the socket in non-blocking mode.
def accept_wrapper(sock):

    # the main objective in this version of the server since we don’t 
    # want it to block. If it blocks, then the entire server is stalled 
    # until it returns. Which means other sockets are left waiting
    conn, addr = sock.accept() 
    conn.setblocking(False) 

    # data is used to store whatever arbitrary data you’d like along with 
    # the socket. It’s returned when select() returns. We’ll use data to 
    # keep track of what’s been sent and received on the socket
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')

    # Since we want to know when the client connection is ready 
    # for reading and writing, both of those events are set
    events = selectors.EVENT_READ | selectors.EVENT_WRITE

    sel.register(conn, events, data=data)

    print('['+server_str+'] New connection is registered', conn.getsockname() + conn.getpeername())


# This is the heart of the simple multi-connection server. 
# key is the namedtuple returned from select() that contains 
# the socket object (fileobj) and data object. mask contains 
# the events that are ready.
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    peer_name = sock.getpeername()
    
    # If the socket is ready for reading, then mask & selectors.EVENT_READ 
    # is true, and sock.recv() is called
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print('[' + str(peer_name[1]) + '] Data Received: ' + str(recv_data))
            data.outb += recv_data
        else:
            # This means that the client has closed their socket,
            # so the server should too. But don’t forget to first 
            # call sel.unregister() so it’s no longer monitored by select().
            sel.unregister(sock)
            sock.close()
            print('[' + str(peer_name[1]) + '] Connection Closed')

    # When the socket is ready for writing, which should always be the 
    # case for a healthy socket, any received data stored in data.outb 
    # is echoed to the client using sock.send(). The bytes sent are 
    # then removed from the send buffer
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('[' + str(peer_name[1]) + '] Writing Data: ' + str(data.outb))
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
        else:
            pass

# Create listener socket
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.bind((HOST, PORT))
listen_socket.listen()

# Calls made to this socket will no longer block
listen_socket.setblocking(False)

# Registers the socket to be monitored with sel.select() 
# for the events you’re interested in. For the listening
# socket, we want read events: selectors.EVENT_READ
sel.register(listen_socket, selectors.EVENT_READ, data=None)
print('['+server_str+'] Listening on port', PORT)

while True:

    # blocks until there are sockets ready for I/O. It returns a 
    # list of (key, events) tuples, one for each socket. key is a 
    # SelectorKey namedtuple that contains a fileobj attribute. 
    # key.fileobj is the socket object, and mask is an event mask 
    # of the operations that are ready
    events = sel.select(timeout=None)
    
    # if key.data is None, then we know it’s from the listening 
    # socket and we need to accept() the connection.
    # If key.data is not None, then we know it’s a client socket 
    # that’s already been accepted, and we need to service it.
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)

