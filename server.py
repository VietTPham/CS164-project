#!/usr/bin/env python
import socket
import sys
import thread
 
user = ["user1","user2","user3","user4"]
user_online = [0,0,0,0,0]
user_conn = [0,0,0,0,0]
password = ["pass1","pass2","pass3","pass4"]
messagecount = 0
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
      #mark that the user is online
      user_online[user.index(id)] = 1
      #mark the user conn number
      user_conn[user.index(id)] = conn
      
      conn.send(check_unread(id))
      while True:
        menu(conn,id)
    else:
      try_count -= 1
      if (try_count == 0):
        print "User",id,"permission denied"
        conn.send("!!exit!!")
        conn.close()
        thread.exit()

def check_unread(id):
  unread = 0
  for line in open(id,"r").readlines():
    if line.startswith("unread:"):
      unread += 1
  unread_message = "You have",unread,"unread messages\n"
  return ' '.join(str(x) for x in unread_message)

def menu(conn, id):
  conn.send(
  """Main menu
  (1) See Offline Messages
  (2) Edit Subscriptions
  (3) Post a Message
  (4) Logout
  select: """)
  choice = conn.recv(1024)
  if (choice == "1"):
    see_offline_message(conn, id)
  elif (choice == "2"):
    edit_subscriptions(conn, id)
  elif (choice == "3"):
    post_a_message(conn, id)
  elif (choice == "4"):
    #mark user as offline then exit
    user_online[user.index(id)] = 0
    conn.send("!!exit!!")
    conn.close()
    thread.exit()
  else:
    conn.send("Invalid choice")
def see_offline_message(conn, id):
  print id
def edit_subscriptions(conn, id):
  print id
def post_a_message(conn, id):
  print id
if __name__ == "__main__":
  sock = init_sock()
  while (True):
    conn, addr = sock.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    thread.start_new_thread(clientthread ,(conn,))
  conn.close()
  sock.close()