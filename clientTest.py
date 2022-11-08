from random import random
import socket
import sys
import random
import json
from client import Client

HOST = socket.gethostbyname(socket.gethostname())
PORT = int(sys.argv[1])
# Default type of client is TCP
type ='tcp'
if len(sys.argv) == 3:
    type = sys.argv[2]

c = Client(HOST,type,PORT)
"""Function to load the JSON file when the server starts"""
with open('./tests/mockData.json', 'r') as f:
        keyValueStore = json.load(f)

keys = list(keyValueStore.keys())
keysLen = len(keys)
print(keysLen)
# Each client will do 5 set/get operation on random key/value pairs
for i in range(5):
    rKeyIndex = random.randint(0,keysLen-1)
    value = keyValueStore[keys[rKeyIndex]]
    if random.random()>=0.5:
        c.set(keys[rKeyIndex],value)
    else:
        c.get(keys[rKeyIndex])
    