#!/usr/bin/env python
import socket
import sys
from thread import *
 
user = ["user1","user2","user3","user4"]
password = ["pass1","pass2","pass3","pass4"]

def init_sock():
  host = ''   # Symbolic name meaning all available interfaces
  port = int(sys.argv[1]) # Arbitrary non-privileged port
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  print 'Socket created'
   
  #Bind socket to local host and port
  try:
      s.bind((host, port))
  except socket.error , msg:
      print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
      sys.exit()
       
  print 'Socket bind complete'
   
  #Start listening on socket
  s.listen(10)
  print 'Socket now listening'
  return s

#Function for handling connections. This will be used to create threads
def clientthread(conn):
    #Sending message to connected client
    conn.send('Welcome to rettiwt.\n') #send only takes string
    #Receiving from client
    try_count = 3
    while True:
      User = conn.recv(1024)
      print "User",User,"attempting to login"
      Password = conn.recv(1024)
      if any(User in s for s in user) and Password == password[user.index(User)]:
        print "User", User, "login successful"
        conn.send("login successful")
      else:
        print "User",User, "login failed"
        try_count = try_count -1
        if (try_count == 0):
          print "permission denied"
          conn.send("permission denied")
          try:
            thread.exit()
            conn.close()
          except:
            pass
        else:
          conn.send("login failed")

if __name__ == "__main__":
  sock = init_sock()
  while (True):
    conn, addr = sock.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    start_new_thread(clientthread ,(conn,))
  conn.close()
  sock.close()