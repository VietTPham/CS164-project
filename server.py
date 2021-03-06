#!/usr/bin/env python
import socket
import sys
import thread
import subprocess
import time
import getpass

user = ["user1","user2","user3","user4", "user5", "user6"]
user_online = [0,0,0,0,0,0]
user_conn = [0,0,0,0,0,0]
password = ["pass1","pass2","pass3","pass4", "pass5", "pass6"]
messagecount = 0
storedcount = 0
path = "./profile/"
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
    conn.send("Username: ")
    id = conn.recv(4096)
    #print "User",id,"attempting to login"
    conn.send("Password: ")
    pwd = conn.recv(4096)
    
    if (id in user) and (pwd == password[user.index(id)]):
      #mark that the user is online
      user_online[user.index(id)] = 1
      #mark the user conn number
      user_conn[user.index(id)] = conn
      
      conn.send(check_unread(id))
      while True:
        menu(conn, id)
    else:
      try_count -= 1
      if (try_count == 0):
        #print "User",id,"permission denied"
        conn.send("!!exit!!")
        conn.close()
        thread.exit()

def check_unread(id):
  unread = 0
  for line in open(path+id,"r").readlines():
    if line.startswith("unread:"):
      unread += 1
  unread_message = "You have",unread,"unread messages\n"
  time.sleep(0.05)
  return ' '.join(str(x) for x in unread_message)

def menu(conn, id):
  conn.send(
  """
  Main menu
  (1) See Offline Messages
  (2) Edit Subscriptions
  (3) Post a Message
  (4) Hashtag Search
  (5) See Followers   
  (6) Logout
  select: """)
  choice = conn.recv(4096)
  if (choice == "1"):
    see_offline_message(conn, id)
  elif (choice == "2"):
    edit_subscriptions(conn, id, user)
  elif (choice == "3"):
    post_a_message(conn, id)
  elif (choice == "4"):
    hashtag_search(conn, id)
  elif (choice == "5"):
    see_followers(conn, id)
  elif (choice == "6"):
    #mark user as offline then exit
    #print id, "logout"
    user_online[user.index(id)] = 0
    user_conn[user.index(id)] = 0
    conn.send("!!exit!!")
    conn.close()
    thread.exit()
  else:
    conn.send("Invalid choice")
def see_offline_message(conn, id):
  conn.send(
  """
  See Offline Messages
  (1) See all messages
  (2) Message from a user
  (3) Return to main menu
  select: """)
  choice = conn.recv(4096)
  has_at_least_one_unread = False
  if (choice == "1"):
    #check file for all instande of "unread: " at the beginning of a line
    temp_file = open(path+id+".tmp", "w")
    for line in open(path+id,"r").readlines():
      if line.startswith("unread:"):
        line_without_unread = line.replace("unread: ", "", 1)
        temp_file.write(line_without_unread)
        conn.send("!!continue!!"+line_without_unread)
        has_at_least_one_unread = True
      else:
        temp_file.write(line)
    if has_at_least_one_unread == False:
      conn.send('!!continue!!No offline message.')
    temp_file.close()
    subprocess.call(['mv', path+id+'.tmp', path+id])
  elif (choice == "2"):
    follow = get_follow(id)
    if (len(follow) == 0):
      conn.send('!!continue!!No subscription, returning to main menu.')
      time.sleep(0.05)
    else:
      counter = 0
      string = "\n  Select a user"
      for user in follow:
        string += "\n  ("+str(counter+1)+") "+follow[counter]
        counter += 1
      string += "  ("+str(counter+1)+") "+"Return to main menu\n  select: "
      conn.send(string)
      choice = conn.recv(4096)
      if(choice != counter+1):
        #get the user you want to read
        follow_id = follow[int(choice)-1]
        #check the user file for any unread and update the file
        temp_file = open(path+id+".tmp", "w")
        for line in open(path+id,"r").readlines():
          if line.startswith("unread:") and (line.replace("unread: ", "", 1).startswith("@"+follow_id)):
            line_without_unread = line.replace("unread: ", "", 1)
            temp_file.write(line_without_unread)
            conn.send("!!continue!!"+line_without_unread)
            has_at_least_one_unread = True
          else:
            temp_file.write(line)
        if has_at_least_one_unread == False:
          conn.send('!!continue!!No offline message.')
        temp_file.close()
        subprocess.call(['mv', path+id+'.tmp', path+id])
      else:
        return
  else:
    return
def edit_subscriptions(conn, id, user):
  conn.send(
  """
  Edit Subscriptsion
  (1) Add a subscription
  (2) Drop a subscription
  (3) Return to main menu
  select: """)
  choice = conn.recv(4096)
  if (choice == "1"):
    conn.send("Add a subscription: ")
    choice = conn.recv(4096)
    id_follow = get_follow(id)
    if (choice not in user) or (choice == id):
      conn.send("!!continue!!Invalid user.")
      time.sleep(0.05)
      return
    if (choice in id_follow):
      conn.send("!!continue!!Already subscribed to user.")
      time.sleep(0.05)
      return
    remove_line_with_id("follow", id)
    insert_follow_string = id+": "+choice.replace("\n","",2)
    for i in id_follow:
      insert_follow_string += " "+i
    
    file = open(path+"follow", "a")
    file.write(insert_follow_string+"\n")
    file.close()
    #Add choice to follower file
    name = choice.replace("\n","",99)
    line_without_name = ""
    found = False
    for line in open(path+"follower","r").readlines():
      if name+": " in line:
        line_without_name = line.replace(": ", ": "+id+" ", 1)
        found = True
    if not found:
      line_without_name = name+": "+id+"\n"
    remove_line_with_id("follower", name)
    file = open(path+"follower", "a")
    file.write(line_without_name)
    file.close()
  elif (choice == "2"):
    follow = get_follow(id)
    if (len(follow) == 0 ):
      conn.send("!!continue!!No subscription.")
      time.sleep(0.05)
      return
    elif (len(follow) > 1):
      counter = 0
      string = "\n  Select a user to remove"
      for user in follow:
        string += "\n  ("+str(counter+1)+") "+follow[counter]
        counter += 1
      string += "  ("+str(counter+1)+") "+"Return to main menu\n  select: "
      conn.send(string)
      choice = conn.recv(4096)
      if (choice == str(counter+1)):
        return
      else:
        name = follow[int(choice)-1]
        if(choice != counter+1):
          follow.pop(int(choice)-1)
        elif (choice == str(counter+1)):
          return
        #parse file
        remove_line_with_id("follow", id)
        #insert deleted line back
        insert_follow_string = id+":"
        for i in follow:
          insert_follow_string += " "+i
        insert_follow_string +="\n"
        #with open(path+"follow", "a") as myfile:
        file = open(path+"follow", "a")
        file.write(insert_follow_string)
        
        #remove from follower file
        name = name.replace("\n","",99)
        line_without_name = ""
        for line in open(path+"follower","r").readlines():
          if name+": " in line:
            line_without_name = line.replace(id, "", 1)
        remove_line_with_id("follower", name)
        file = open(path+"follower", "a")
        file.write(line_without_name)
        file.close()
  elif (choice == "3"):
    return
def post_a_message(conn, id):
  conn.send("Enter your teewt: ")
  teewt = conn.recv(4096)
  if len(teewt) > 140:
    conn.send("!!continue!!Error: Teewt is longer than 140 characters.")
    time.sleep(0.05)
    return
  conn.send("Include hastag? y/n: ")
  choice = conn.recv(4096)
  hashtag = ""
  if choice == "y":
    conn.send("Enter hashtag separated by space: ")
    hashtag +="#"
    hashtag += conn.recv(4096)
    teewt += " "+hashtag.replace(" ", " #", 99)
  all_teewt = open(path+"all_teewt","a")
  teewt = "@"+id+": "+teewt+"\n"
  all_teewt.write(teewt)
  
  global messagecount
  messagecount += 1
  all_teewt.close()
  follower = []
  for line in open(path+"follower","r").readlines():
    if (line.startswith(id)):
      follower = line.replace(id+": ", "", 1)
      follower = follower.replace("\n","",99)
      follower = follower.split(" ")
  if len(follower) != 0:
    for u in follower:
      index = user.index(u)
      #if user is offline
      if (user_online[index] == 0):
        write_to_offline_file = open(path+user[index],"a")
        write_to_offline_file.write("unread: "+teewt)
        write_to_offline_file.close()
        global storedcount
        storedcount +=1
      #if user is online, then send it to there conn
      elif (user_online[index] == 1):
        write_to_offline_file = open(path+user[index],"a")
        write_to_offline_file.write(teewt)
        write_to_offline_file.close()
        user_conn[index].send("!!new!!New teewt: "+teewt)
        time.sleep(0.05)
        
def hashtag_search(conn, id):
  conn.send("Enter hashtag to search: ")
  choice = conn.recv(4096)
  choice = "#"+choice.replace("\n","",1)
  found = []
  string = ""
  for s in reversed(open(path+"all_teewt").readlines()):
    if (choice in s):
      found.append(s)
    if (len(found) == 10):
      break
  for s in found:
    string += s.replace("\n","",1) + "\n"
  conn.send("!!continue!!"+string)
  time.sleep(0.05)
def see_followers(conn, id):
  at_leat_one = False
  follower = []
  for line in open(path+"follower","r").readlines():
    if (line.startswith(id)):
      follower = line.replace(id+": ", "", 1)
  if len(follower) == 0:
    conn.send("!!continue!!No follower.")
    time.sleep(0.05)
    return
  conn.send("!!continue!!"+"Follower: "+follower)
  time.sleep(0.05)

def get_follow(id):
  at_leat_one = False
  follow = []
  for line in open(path+"follow","r").readlines():
    if (line.startswith(id)):
      follow = line.replace(id+": ", "", 1)
      if len(follow) > 2:
        follow = follow.split(" ")
  return follow
def remove_line_with_id(file, id):
  temp_file = open(path+file+".tmp", "w")
  for line in open(path+file,"r").readlines():
    if not line.startswith(id):
      temp_file.write(line)
  temp_file.close()
  subprocess.call(['mv', path+file+'.tmp', path+file])
      
def admin_command(user, password, user_online, user_conn):
  while True:
    input = raw_input("Command: ")
    if (input == "messagecount"):
      global messagecount
      print messagecount
    elif (input == "usercount"):
      online_user = 0
      for u in user_online:
        if (u == 1):
          online_user += 1
      print online_user
    elif (input == "storedcount"):
      global storedcount
      print storedcount
    elif (input == "getuser"):
      print user
      print password
      print user_online
      print user_conn
    elif (input == "newuser"):
      input = raw_input("Username: ")
      user.append(input)
      #create init file
      temp_file = open(path+input, "w")
      temp_file.close()
      input = getpass.getpass("Password: ")
      password.append(input)
      user_online.append(0)
      user_conn.append(0)
    elif (input == "help"):
      print "Avaliable command:\n  messagecount\n  usercount\n  storedcount\n  getuser"
      
      
def set_messagecount(num):
  messagecount = num
def get_messagecount():
  return messagecount
if __name__ == "__main__":
  sock = init_sock()
  thread.start_new_thread(admin_command,(user,password,user_online, user_conn, ) )
  while (True):
    conn, addr = sock.accept()
    #print 'Connected with ' + addr[0] + ':' + str(addr[1])
    thread.start_new_thread(clientthread ,(conn,))
  conn.close()
  sock.close()
