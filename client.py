import socket
from time import sleep
import sys


class Client: 
    
    def __init__(self,host,type,port=8080):
        self.host = host
        self.port = port
        self.type = type
        self.createClientFunc = self.createTCPClient
    
    def createTCPClient(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
        self.client.connect((self.host,self.port))  
                                  
                
    def utf8len(self,s):        
        return str(len(s.encode('utf-8')))
    
    def sendMessageToServer(self,command):
        print("[Client]:",command)
        self.client.send(command.encode())
                
    def receiveACKMessageFromServer(self):
        messageFromServer = self.client.recv(2048)
        print("[Server]:",messageFromServer.decode());
    
    def createSendReceiveMessageFromServer(self,command):  
        # 1. Creates a TCP/Memcached client              
        self.createClientFunc()
        # 2. Sends message to server
        self.sendMessageToServer(command)
        # 3. Recevives ACK message from server
        self.receiveACKMessageFromServer()  

    def set(self,key,value):
        if self.type == "tcp":        
            command = "set" + " " + key + " " + self.utf8len(value) +" 0 " +"\r\n" + value + "\r\n";             
            self.createSendReceiveMessageFromServer(command)
        elif self.type == 'memcached':
            self.createClientFunc()
            print("[Client]: Memcached set(key,value):",key,value)
            out = self.client.set(key,value)   
            print("[Server]:",out);                             
    
    def get(self,key):
        if self.type == 'tcp':
            command = "get"+ " "+key+"\r\n";
            self.createSendReceiveMessageFromServer(command)
        else:
            self.createClientFunc()
            print("[Client]: Memcached get(key):",key)            
            out = self.client.get(key)
            print("[Server]:",out);        
        
port = int(sys.argv[1])
serverInternalIp = sys.argv[2]
serverInternalIp = socket.gethostbyname(socket.gethostname())

c = Client(serverInternalIp,"tcp",port)
c.set("20","120")
print(c.get("30"))
print(c.get("20"))
print(c.get("200"))
