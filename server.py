import random
import socket
import sys
import re
from threading import Thread
from time import sleep
import os

from constants import INVALIDCOMMAND, NEWLINESEPERATOR, NOTEXISTS, STORED
from gcpPythonClientHelper import read_ini
from saveLoadDisk import GoogleBlobStorage, GoogleFireStore, SaveLoadDisk

HOST = socket.gethostbyname(socket.gethostname())
PORT = int(sys.argv[1])
STORAGE = sys.argv[2]

params = read_ini()
USER =params["USER"]["USERNAME"]
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f"/home/{USER}/cred.json"

class ServerThread:
    """
    Does the actual work. 
    Parses the message from client and sends appropriate response back.
    """    
                  
    def validateAndParseMessage(self,message):
        message = message.decode()
        data = re.split(" |\r\n",message)[:-1]
        # Get array message should be of length 2
        if(len(data)==2 and data[0] == "get"):
            self.data = data
        # set array message should be of length 6
        elif (data[0] == "set"):            
            self.data = data
        else:
            return False
        return True
    
    def doWork(self, clientSock,storage):
        self.randomDelay()
        self.clientSock = clientSock   
        messageFromClient = self.clientSock.recv(2048)    
        print("[Client]:",messageFromClient)
        isValid = self.validateAndParseMessage(messageFromClient)
        if(not isValid):
            self.sendMessageToClient(INVALIDCOMMAND)            
            return            
        
        if (self.data[0] == 'get'):
            _,key = self.data
            
            self.sendMessageToClient(storage.get(key))
            
        elif (self.data[0] == 'set'):            
            key = self.data[1]
            value = self.data[5:]            
            value = " ".join(value)                                                          
            storage.save([key,value])
            self.sendMessageToClient(STORED)    

    
    def sendMessageToClient(self,message):
        if(type(message)==str):
            message = message.encode()    
        self.clientSock.send(message)
        print("[Server]:",message)
        
    
    def randomDelay(self):        
        # sleep(random.randint(1,2))
        pass

class Server:
    """Starts a new TCP server
    * For every new incoming connection, it will create new thread for execution. 
    """
    def __init__(self, host, port=8080, storage="default"):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host,port))
        self.server.listen(5)
        self.index = 0       
        if storage == "default": 
            self.storage = SaveLoadDisk()        
        elif storage == "firestore":
            self.storage = GoogleFireStore()
        elif storage == "blobstorage":
            self.storage = GoogleBlobStorage()
        print(f"Server is listening on port {PORT}")        
        
    def startServer(self):
        
        while True:
            client_sock, client_addr = self.server.accept()
            print("Accepting connection from ",client_addr)                        
            thread = Thread(target = ServerThread().doWork, args=(client_sock,self.storage ), name = f"t{self.index}" )
            print("Spawned new thread")
            self.index +=1
            thread.start()
        
        
    
            
s = Server(HOST,PORT, STORAGE)
s.startServer()

    