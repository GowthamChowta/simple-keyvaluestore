from abc import ABC, abstractmethod
import json
import os
from google.cloud import firestore, storage

from constants import NEWLINESEPERATOR, NOTEXISTS
from gcpPythonClientHelper import read_ini

# The `project` parameter is optional and represents which project the client
# will act on behalf of. If not supplied, the client falls back to the default
# project inferred from the environment.

if "simple-keyvaluestore"  not in os.getcwd():
    os.chdir("simple-keyvaluestore/")


params = read_ini()

bucketName = params["GCP"]["bucketName"]
projectId = params["USER"]["PROJECTID"]


class CustomStorage(ABC):
    
    @abstractmethod
    def get(self):
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
        self.db = firestore.Client(project=projectId).collection(u'items')
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
    
    
class GoogleBlobStorage(CustomStorage):
    
    def __init__(self):
        # Instantiates a client
        self.storage_client = storage.Client(project=projectId)
        self.bucket = self.storage_client.bucket(bucketName)
        
    
    def save(self, data):
        """Write and read a blob from GCS using file-like IO"""
        
        blob = self.bucket.blob(data[0])

        # Mode can be specified as wb/rb for bytes mode.
        # See: https://docs.python.org/3/library/io.html
        with blob.open("w") as f:
            f.write(data[1])
        print("Data saved to Blob storage successfully")
    
    def get(self,key):
        try:
            blob = self.bucket.blob(key)            
            with blob.open("r") as f:
                out = f.read()
            return self.parseGetResponse(key,out)
        except Exception as e:
            return self.parseGetResponse(key,None)
            
    
        
        