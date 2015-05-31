#!/usr/bin/env python

import socket
import sys
import string
import getpass
import thread

def init_sock():
  host = '127.0.0.1'
  port = int(sys.argv[1])

  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  except socket.error, msg:
    print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
    sys.exit();
   
  print 'Socket Created'

  try:
    remote_ip = socket.gethostbyname( host )
   
  except socket.gaierror:
    #could not resolve
    print 'Hostname could not be resolved. Exiting'
    sys.exit()

  print 'Ip address of ' + host + ' is ' + remote_ip
   
  #Connect to remote server
  s.connect((remote_ip , port))
   
  print 'Socket Connected to ' + host + ' on ip ' + remote_ip
  return s

if __name__ == "__main__":
  sock = init_sock()
  
  #Send some data to remote server
  #first message from server
  print sock.recv(4096)
  while (True):
    reply = sock.recv(4096)
    if (reply.startswith("!!exit!!")):
      print "Connection closed"
      sock.close()
      sys.exit()
    if (not reply.startswith("!!continue!!")):
      input = raw_input(reply)
      sock.send(input)
    else:
      reply = reply.replace("!!continue!!", "", 1)
      print reply
  sock.close()