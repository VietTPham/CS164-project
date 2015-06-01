#!/usr/bin/env python

import socket
import sys
import string
import getpass
import thread
import select
import time

reply = ""
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
  time.sleep(0.05)
  reply = ""
  while (True):
    r, w, x = select.select([sys.stdin, sock], [], [])
    if not r:
      continue
    if r[0] is sys.stdin:
      choice = raw_input()
      sock.send(choice)
    else:
      reply = sock.recv(4096)
      if (reply.startswith("!!exit!!")):
        print "Connection closed"
        sock.close()
        sys.exit()
      elif (reply.startswith("!!continue!!")):
        reply = reply.replace("!!continue!!", "", 99)
        print reply
      elif (reply.startswith("!!new!!")):
        reply = reply.replace("!!new!!", "", 99)
        print reply
      else:
        #print (reply)
        if (reply.startswith("Password:")):
          message = getpass.getpass()
          sock.send(message)
        else:
          sys.stdout.write(reply)
          sys.stdout.flush()
  sock.close()