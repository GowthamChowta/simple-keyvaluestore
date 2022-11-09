from abc import ABC, abstractmethod
import json
import os
from google.cloud import firestore

from constants import NEWLINESEPERATOR, NOTEXISTS

# The `project` parameter is optional and represents which project the client
# will act on behalf of. If not supplied, the client falls back to the default
# project inferred from the environment.

if "simple-keyvaluestore"  not in os.getcwd():
    os.chdir("simple-keyvaluestore/")


class CustomStorage(ABC):
    
    @abstractmethod
    def load(self):
        pass
    @abstractmethod
    def save(self,data):
        pass
    
    def utf8len(self,s:str):        
        return str(len(s.encode('utf-8')))  
    
    def parseGetResponse(self,key,value):
        command = ''        
        if value !=None:            
            command = "VALUE" + " " + key +" 0 "+self.utf8len(value) + NEWLINESEPERATOR + value + NEWLINESEPERATOR + "END\r\n"
            # command = value
        else:
            command = "VALUE" + " " + key +" 0 "+self.utf8len(NOTEXISTS.decode()) + NEWLINESEPERATOR + NOTEXISTS.decode() + NEWLINESEPERATOR + "END\r\n"
            # command = NOTEXISTS
        return command    

class SaveLoadDisk(CustomStorage):
    
    def __init__(self):
        self.keyValueStore = self.load()
        
    def load(self):
        """Function to load the JSON file when the server starts"""
        with open('./data.json', 'r') as f:
            try:
                self.keyValueStore = json.load(f)
            except:
                self.keyValueStore = dict()
        return self.keyValueStore
    
    def save(self,newData):        
        print("new data is",newData)
        self.keyValueStore[newData[0]] = newData[1]        
        print(f"Writing data to disk")
        with open('./data.json', 'w') as f:
            json.dump(self.keyValueStore, f)
        print(f"Writing data to disk Complete")
        
        
    def get(self,key):
        if key in self.keyValueStore:
            return self.parseGetResponse(key,self.keyValueStore[key])
        else:
            return self.parseGetResponse(key,None)
        
        
class GoogleFireStore(CustomStorage):
    
    def __init__(self):        
        self.load()
    
    def load(self):
        self.db = firestore.Client(project='test-chgowt-1').collection(u'items')
        return self.db
    
    def save(self,data):
        
        doc_ref = self.db.document(f'{data[0]}')
        doc_ref.set({
            "key": data[0],
            "value":data[1]
        })
        print("Data saved to firestore successfully")
    
    def get(self,key):
        doc_ref = self.db.document(u''+key)
        doc = doc_ref.get()
        if doc.exists:
            print(doc.to_dict())
            return self.parseGetResponse(key,doc.to_dict()["value"])                        
        else:
            return self.parseGetResponse(key,None)
    
        
        
        