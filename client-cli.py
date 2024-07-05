import socket
import os
import json
import sys
from chat import Chat

# TARGET_IP = "127.0.0.1"
# TARGET_PORT = 8889

class ChatClient:
    def __init__(self, TARGET_IP, TARGET_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(TARGET_IP)
        print(TARGET_PORT)
        self.server_address = (TARGET_IP,int(TARGET_PORT))
        self.sock.connect(self.server_address)
        self.tokenid=""
        self.address_ip = TARGET_IP
        self.address_port = TARGET_PORT
        
    def proses(self,cmdline):
        j=cmdline.split(" ")
        try:
            command=j[0].strip()
            if (command=='addrealm'):
                realm_id=j[1].strip()
                realm_address=j[2].strip()
                realm_port=j[3].strip()
                return self.addrealm(realm_id,realm_address,realm_port)
                
            elif (command=='checkrealm'):
                return self.checkrealm()
                
            elif (command=='sendrealm'):
                realm_id=j[1].strip()
                usernameto = j[2].strip()
                message=""
                for w in j[3:]:
                    message="{} {}" . format(message,w)
                return self.sendrealm(realm_id,usernameto,message)

            elif (command=='inboxrealm'):
                realm_id=j[1].strip()
                return self.inboxrealm(realm_id)
            
            elif command == 'sendgrouprealm':
                realm_id = j[1].strip()
                groupname = j[2].strip()
                message=""
                for w in j[3:]:
                    message="{} {}" . format(message,w)
                return self.sendgrouprealm(realm_id, groupname, message)
            
            elif (command=='inboxgrouprealm'):
                realm_id=j[1].strip()
                groupname=j[2].strip()
                return self.inboxgrouprealm(realm_id,groupname)
            
            elif command == "sessioncheck":
                return self.sessioncheck()
            
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
                return "-Maaf, command tidak benar"
        
    def sendstring(self,string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(64)
                print("diterima dari server",data)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivemsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return { 'status' : 'ERROR', 'message' : 'Gagal'}

    def login(self,username,password):
        string="auth {} {} \r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
        
    def logout(self):
        string = "logout \r\n"
        result = self.sendstring(string)
        if result["status"] == "OK":
            self.tokenid = ""
            return "user logged out"
        else:
            return "Error, {}".format(result["message"])

    def send_message(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
        
    def inbox(self):
        if self.tokenid == "":
            return "Error, not authorized. Please log in first."
        string = "inbox {} \r\n".format(self.tokenid)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            messages = result['messages']
            inbox_messages = ""
            for user, user_messages in messages.items():
                for msg in user_messages:
                    inbox_messages += "From: {}\n".format(msg['msg_from'])
                    inbox_messages += "To: {}\n".format(msg['msg_to'])
                    if isinstance(msg['msg'], dict):
                        inbox_messages += "Message: {}\n".format(msg['msg']['msg'])
                    else:
                        inbox_messages += "Message: {}\n".format(msg['msg'])
                    inbox_messages += "\n"
            if inbox_messages:
                return inbox_messages
            else:
                return "No messages in the inbox."
        else:
            return "Error, {}".format(result['message'])

    def create_group(self, groupname, password):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="addgroup {} {} {} \r\n" . format(self.tokenid, groupname, password)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "added {} group" . format(groupname)
        else:
            return "Error, {}" . format(result['message'])
        
    def join_group(self, groupname, password):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="joingroup {} {} {} \r\n" . format(self.tokenid, groupname, password)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "joined {} group" . format(groupname)
        else:
            return "Error, {}" . format(result['message'])
    
    def send_group(self, groupname, message):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendgroup {} {} {} \r\n" . format(self.tokenid, groupname, message)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "group message sent to {} group" . format(groupname)
        else:
            return "Error, {}" . format(result['message'])
        
    def inbox_group(self, groupname):
        if self.tokenid == "":
            return "Error, not authorized"
        string = "inboxgroup {} {}\r\n".format(self.tokenid, groupname)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            messages = result['messages']
            inbox_messages = ""
            for group, group_messages in messages.items():
                for msg in group_messages:
                    inbox_messages += "From: {}\n".format(msg['msg_from'])
                    inbox_messages += "To: {}\n".format(msg['msg_to'])
                    if isinstance(msg['msg'], dict):
                        inbox_messages += "Message: {}\n".format(msg['msg']['msg'])
                    else:
                        inbox_messages += "Message: {}\n".format(msg['msg'])
                    inbox_messages += "\n"
            if inbox_messages:
                return inbox_messages
            else:
                return "No messages in the group inbox."
        else:
            return "Error, {}".format(result['message'])

    # Realm-related
    def addrealm(self, realm_id, realm_address, realm_port):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="addrealm {} {} {} {} {}\r\n" . format(realm_id, realm_address, realm_port, self.address_ip, self.address_port)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "added {} realm" . format(realm_id)
        else:
            return "Error, {}" . format(result['message'])
        
    def checkrealm(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="checkrealm\r\n"
        result = self.sendstring(string)
        if result['status']=='OK':
            return "returned realm list: {}".format(json.dumps(result['message']))
        else:
            return "Error, {}" . format(result['message'])
    
    def sendrealm(self, realm_id, usernameto, message):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendrealm {} {} {} {} {} {}\r\n" . format(self.address_ip, self.address_port, self.tokenid, realm_id, usernameto, message)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "realm message sent to user {} realm {}" . format(usernameto, realm_id)
        else:
            return "Error, {}" . format(result['message'])
        
    def inboxrealm(self, realm_id):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inboxrealm {} {}\r\n" . format(self.tokenid, realm_id)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])
        
    def sendgrouprealm(self, realm_id, groupname, message):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendgrouprealm {} {} {} {} {} {} \r\n" . format(self.address_ip, self.address_port, self.tokenid, realm_id, groupname, message)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "group message sent to {} group in realm {}" . format(groupname, realm_id)
        else:
            return "Error, {}" . format(result['message'])

    def inboxgrouprealm(self, realm_id, groupname):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inboxgrouprealm {} {} {}\r\n" . format(self.tokenid, realm_id, groupname)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])
        
    def sessioncheck(self):
        string = "sessioncheck {} \r\n"
        result = self.sendstring(string)
        if result["status"] == "OK":
            return result["message"]
        
if __name__=="__main__":
    TARGET_IP = "172.18.0.3"
    TARGET_PORT = 8889
    try:
        TARGET_IP = sys.argv[1]
    except:
        pass
    try:
        TARGET_PORT = int(sys.argv[2])
    except:
        pass
    cc = ChatClient(TARGET_IP, TARGET_PORT)
    c = Chat()
    # while True:
    #     cmdline = input("Command {}:" . format(cc.tokenid))
    #     print(cc.proses(cmdline))
        
    while True:
        print("\n")
        print("List User: " + str(c.users.keys()) + " dan Passwordnya: " + str(
            c.users['messi']['password']) + ", " + str(c.users['henderson']['password']) + ", " + str(
            c.users['lineker']['password']))

        if cc.tokenid == "":
            print("Please select a command:")
            print("1. Login")
            print("2. Exit")
            command = input("Command: ")

            if command == "1":
                username = input("Username: ")
                password = input("Password: ")
                login_result = cc.login(username, password)
                print(login_result)
            elif command == "2":
                break
            else:
                print("Invalid command. Please try again.")

        else:
            print("Command:")
            print("1. Logout")
            print("2. Send message")
            print("3. Send group message")
            print("4. Add realm")
            print("5. Send realm message")
            print("6. Send group realm message")
            print("7. Inbox")
            print("8. Realm inbox")
            print("9. Create group")
            print("10. Add group member")
            print("11. Send group message")
            print("12. Inbox group")
            print("13. Realm related")

            cmdline = input("Command {}: ".format(cc.tokenid))

            if cmdline == "1":
                cc.logout()
                continue

            if cc.tokenid == "":
                print("Error, not authorized. Please log in first.")
                continue

            elif cmdline == "2":
                #cmdline.startswith("send"):
                print("Send Message")
                username_to = input("Send to: ")
                message = input("Message: ")
                result = cc.send_message(username_to, message)
                print(result)
                
            elif cmdline == "3":
                # cmdline.startswith("sendgroup"):
                # _, usernames_to = cmdline.split(" ")
                print("Send Group Message")
                username_to = input("Send to: ")
                message = input("Message: ")
                result = cc.send_group_message(username_to, message)
                print(result)
                  
            elif cmdline == "4":
                #cmdline.startswith("addrealm"):
                #_, realm_id, address, port = cmdline.split(" ")
                print("Add Realm")
                realm_id = input("Realm id: ")
                address = input("Addres: ")
                port = input("Port: ")
                result = cc.add_realm(realm_id, address, port)
                print(result)
                
            elif cmdline == "5":
                # cmdline.startswith("sendrealm"):
                # _, realm_id, username_to = cmdline.split(" ")
                print("Send Realm Message")
                realm_id = input("Realm ID: ")
                username_to = input("Send to: ")
                message = input("Message: ")
                result = cc.send_realm_message(realm_id, username_to, message)
                print(result)

            elif cmdline == "6":
                # cmdline.startswith("sendgrouprealm"):
                # _, realm_id, usernames_to = cmdline.split(" ")
                print("Send Group Realm Message")
                realm_id = input("Realm ID: ")
                username_to = input("Send to: ")
                message = input("Message: ")
                result = cc.send_group_realm_message(realm_id, usernames_to, message)
                print(result)

            elif cmdline == "7":
                # cmdline.startswith("inbox"):
                print("Inbox")
                result = cc.inbox()
                print(result)

            elif cmdline == "8":
                # cmdline.startswith("realminbox"):
                # _, realm_id = cmdline.split(" ")
                print("Realm Inbox")
                realm_id = input("Realm ID: ")
                result = cc.realm_inbox(realm_id)
                print(result)

            elif cmdline == "9":
                # cmdline.startswith("creategroup"):
                print("Create Group")
                groupname = input("Group name: ")
                password = input("Password: ")
                result = cc.create_group(groupname, password)
                print(result)

            elif cmdline == "10":
                # cmdline.startswith("addgroupmember"):
                print("Join Group Member")
                groupname = input("Group name: ")
                password = input("Password: ")
                result = cc.join_group(groupname, password)
                print(result)

            elif cmdline == "11":
                # cmdline.startswith("removegroupmember"):
                print("Send Message Group")
                groupname = input("Group name: ")
                message = input("Message: ")
                result = cc.send_group(groupname, message)
                print(result)

            elif cmdline == "12":
                # cmdline.startswith("viewgroupmembers"):
                print("View Inbox Group")
                groupname = input("Group name: ")
                result = cc.inbox_group(groupname)
                print(result)
                
            elif cmdline == "13":
                print("Realm Related")
                cmdline = input("Command {}:" . format(cc.tokenid))
                print(cc.proses(cmdline))

            else:
                print("Invalid command. Please try again.")
    