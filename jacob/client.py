#!/usr/bin/python3

import socket
import struct
import sys
import time
import argparse
import string
import urllib.request, urllib.parse
import os
import re

InParser=argparse.ArgumentParser(description='Client')

#Parses input, checks for required data and moves args into variables
InParser.add_argument('s', action='store', help='Load Balancer Address')
InParser.add_argument('p', action='store', type=int, choices=range(1023,65536), metavar="[1024-65535]", help='Port number')
InParser.add_argument('l', action='store', help='Logfile location')

args=InParser.parse_args()

LoadBalancer=args.s
PORT=args.p
logFileLoc=args.l

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (LoadBalancer, PORT)
print(server_address, type(server_address), type(LoadBalancer), type(PORT))

def unpack(data):
    #Unpack incoming messages
    Sender, Type, Message = struct.unpack('>ii24s', data)
    #Decode message from utf-8 and strip padded bytes
    Message = Message.decode('utf-8')
    Message = Message.strip('\x00')
    return Sender, Type, Message;

def pack(Sender, Type, Message):
    #Pack outgoing messages; Header is: | Sender (4 bytes) | Message Type (4 bytes) | Message (Max 24 bytes, utf-8 encoded) |
    Message = bytes(Message, 'utf-8')
    data = struct.pack('>ii24s', Sender, Type, Message)
    return data;

#Start by connecting to the load balancer
sock.connect(server_address)
data = pack(10, 5, "Server Request") #Request the preferred server from the load balancer
sock.send(data)
data = sock.recv(32)
Sender, Type, Message = unpack(data)
if Sender == 20:
    if Type == 10:
        server_address = list(Message.split(",")) #Convert the server to a usable form
        addr = server_address[0]
        port = int(server_address[1])
        server_address = (addr, port)
        print(server_address, type(server_address), type(addr), type(port))
    else:
        #DEBUG Send error message back to load balancer
        print("Error")
        sys.exit()
else:
    print("Error") #Bad sender
    sys.exit()

sock.shutdown(socket.SHUT_RDWR) #Close connection to load balancer
sock.close()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(server_address) #Open connection to the replica server
data = pack(10, 15, "Content Request") #Request the webpage
sock.send(data)
data = sock.recv(32)
Sender, Type, Message = unpack(data)
if Sender == 30:
    if Type == 20:
        format_string = ">ii" + Message + "s"
        load = int(Message) #Message from server is the int size in bytes of the page
        buf = load + 8 #Size of payload + 4 byte sender + 4 byte message type
    else:
        #Error
        print("Error")
        sys.exit()
else:
    print("Error")
    sys.exit()

data = sock.recv(buf)
Sender, Type, WebPage = struct.unpack(format_string, data)
print(WebPage)
