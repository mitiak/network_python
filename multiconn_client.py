#!/usr/bin/env python3

import socket
import selectors
import types
import os
import sys

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

sel = selectors.DefaultSelector()
messages = [b'Message 1 from client.', b'Message 2 from client.']

def start_connections(host, port, num_conns):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print('[start_connections] starting connection', connid, 'to', server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(connid=connid,
                                        msg_total=sum(len(m) for m in messages),
                                        recv_total=0,
                                        messages=list(messages),
                                        outb=b'')
        print('[start_connections] data={}'.format(data))
        sel.register(sock, events, data=data)

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
            print('received', repr(recv_data), 'from connection', data.connid)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print('closing connection', data.connid)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        print('[service_connection '+ str(sock.fileno()) +'] mask & selectors.EVENT_WRITE')
        print('[service_connection '+ str(sock.fileno()) +'] data={}'.format(data))
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
            print('[service_connection '+ str(sock.fileno()) +'] data.outb = data.messages.pop(0)')
            print('[service_connection '+ str(sock.fileno()) +'] data={}'.format(data))
        if data.outb:
            print('[service_connection '+ str(sock.fileno()) +'] sending', repr(data.outb), 'to connection', data.connid)
            print('[service_connection '+ str(sock.fileno()) +'] data={}'.format(data))
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
            print('[service_connection '+ str(sock.fileno()) +'] data={}'.format(data))

# if len(sys.argv) != 4:
#     print('usage:', sys.argv[0], '<host> <port> <num_connections>')
#     sys.exit(1)

# host, port, num_conns = sys.argv[1:4]
# start_connections(host, int(port), int(num_conns))
start_connections(HOST, PORT, int(sys.argv[1]))

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print('caught keyboard interrupt, exiting')
finally:
    sel.close()
        
