import random
import socket
import sys
import re
from threading import Thread
from time import sleep

from constants import INVALIDCOMMAND, NEWLINESEPERATOR, NOTEXISTS, STORED
from saveLoadDisk import SaveLoadDisk

HOST = socket.gethostbyname(socket.gethostname())
PORT = int(sys.argv[1])



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
    
    def doWork(self, clientSock,saveLoadDisk):
        self.keyValueStore = saveLoadDisk.keyValueStore
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
            self.sendMessageToClient(self.parseGetResponse(key))
            
        elif (self.data[0] == 'set'):            
            key = self.data[1]
            value = self.data[5:]            
            value = " ".join(value)                                              
            self.keyValueStore[key] = value
            saveLoadDisk.writeToJson({key,value})
            self.sendMessageToClient(STORED)                    

    
    def sendMessageToClient(self,message):
        if(type(message)==str):
            message = message.encode()    
        self.clientSock.send(message)
        print("[Server]:",message)
        
    def utf8len(self,s):        
        return str(len(s.encode('utf-8')))    
    
    def parseGetResponse(self,key):
        command = ''        
        if key in self.keyValueStore:
            value = self.keyValueStore[key]
            command = "VALUE" + " " + key +" 0 "+self.utf8len(value) + NEWLINESEPERATOR + value + NEWLINESEPERATOR + "END\r\n"
            # command = value
        else:
            command = "VALUE" + " " + key +" 0 "+self.utf8len(NOTEXISTS.decode()) + NEWLINESEPERATOR + NOTEXISTS.decode() + NEWLINESEPERATOR + "END\r\n"
            # command = NOTEXISTS
        return command
    
    def randomDelay(self):        
        # sleep(random.randint(1,2))
        pass

class Server:
    """Starts a new TCP server
    * For every new incoming connection, it will create new thread for execution. 
    """
    def __init__(self, host, port=8080):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.server.bind((host,port))
        self.server.listen(5);
        self.index = 0        
        self.saveLoadDisk = SaveLoadDisk()        
        print(f"Server is listening on port {PORT}")        
        
    def startServer(self):
        
        while True:
            client_sock, client_addr = self.server.accept()
            print("Accepting connection from ",client_addr)                        
            thread = Thread(target = ServerThread().doWork, args=(client_sock,self.saveLoadDisk ), name = f"t{self.index}" )
            print("Spawned new thread")
            self.index +=1
            thread.start()
        
        
    
            
s = Server(HOST,PORT)
s.startServer()

    