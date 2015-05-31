#!/usr/bin/env python
import socket
import sys
import thread
 
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
      conn.send("User: ")
      id = conn.recv(1024)
      print "User",id,"attempting to login"
      conn.send("Password: ")
      pwd = conn.recv(1024)
      
      if any(id in s for s in user) and pwd == password[user.index(id)]:
        print "User", id, "login successful"
        #conn.send("login successful")
      else:
        print "User",id, "login failed"
        try_count = try_count -1
        if (try_count == 0):
          print "User",id,"permission denied"
          conn.send("!!exit!!")
          conn.close()
          thread.exit()
      
if __name__ == "__main__":
  sock = init_sock()
  while (True):
    conn, addr = sock.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    thread.start_new_thread(clientthread ,(conn,))
  conn.close()
  sock.close()