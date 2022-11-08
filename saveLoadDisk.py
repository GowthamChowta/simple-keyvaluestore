import json


class SaveLoadDisk:
    
    def __init__(self):
        self.keyValueStore = self.loadJson()
        
    def loadJson(self):
        """Function to load the JSON file when the server starts"""
        with open('data.json', 'r') as f:
            try:
                self.keyValueStore = json.load(f)
            except:
                self.keyValueStore = dict()
        return self.keyValueStore
    
    def writeToJson(self,newData):        
        # self.keyValueStore.update(newData)
        print(f"Writing data to disk")
        with open('data.json', 'w') as f:
            json.dump(self.keyValueStore, f)
        print(f"Writing data to disk Complete")
        
        
        