# TODO Need to put reference
# TODO Need to put reference
from time import sleep
import os
import threading
from google.api_core.extended_operation import ExtendedOperation

from gcpPythonClientHelper import create_instance, disk_from_image, getInstanceExternalInternalIpByName, read_ini, runCommandsOnAMachineOverSSH, setupMachineByhostIP


params = read_ini()

applicationCredentialsPath = params["GCP"]["applicationCredentials"]
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = applicationCredentialsPath
ZONE= params["USER"]["ZONE"]
PROJECTID=params["USER"]["PROJECTID"]
USER =params["USER"]["USERNAME"]
SSHFilePath = params["USER"]["SSHFilePath"]
SERVERPORT =params["USER"]["SERVERPORT"]


image_name=params["GCP"]["imageName"]
source_image=params["GCP"]["sourceImage"]
disk_type=f'zones/{ZONE}/diskTypes/pd-balanced'


boot_disk_server = disk_from_image(disk_type,10,True,source_image=source_image)
boot_disk_client = disk_from_image(disk_type,10,True,source_image=source_image)

machine_names = ["keyvalue4-server","keyvalue4-client"]
commandsToSetupOnServer = [
    "sudo apt install -y git",
    "git clone https://github.com/GowthamChowta/simple-keyvaluestore.git",
    "sudo apt install -y python3-pip",    
    "sudo pip install google-cloud-core",
    "sudo pip install google-cloud-firestore",
    "sudo pip install google-cloud-compute" 
]
commandsToSetupOnClient = [
    "sudo apt install -y git",
    "git clone https://github.com/GowthamChowta/simple-keyvaluestore.git"    
]


print("Starting server machine")
commandsToServer = [
    f"python3 -u simple-keyvaluestore/server.py {SERVERPORT} firestore"
]
## Starting server machine
create_instance(project_id=PROJECTID,zone=ZONE,instance_name=machine_names[0],disks=[boot_disk_server],machine_type="e2-medium",external_access=True)
serverPublicIP,serverInternalIP = getInstanceExternalInternalIpByName(machine_names[0])
print(f"Server Public IP address is {serverPublicIP}")
print(f"Removing known hosts if exists for {serverPublicIP}")
os.system(f"ssh-keygen -R {serverPublicIP}")

## Starting client machine
create_instance(project_id=PROJECTID,zone=ZONE,instance_name=machine_names[1],disks=[boot_disk_client],machine_type="e2-micro",external_access=True)
clientPublicIP, clientInternalIP = getInstanceExternalInternalIpByName(machine_names[1])
print(f"Client Public IP address is {clientPublicIP}")
print(f"Removing known hosts if exists for {clientPublicIP}")
os.system(f"ssh-keygen -R {clientPublicIP}")

print("Installing dependencies on Server")
sleep(5)
ssh = setupMachineByhostIP(serverPublicIP)
ftp_client=ssh.open_sftp()
ftp_client.put(applicationCredentialsPath, f"/home/{USER}/cred.json")
ftp_client.close()

# commandsToSetupOnServer.append(f"sudo scp -o StrictHostKeyChecking=no {applicationCredentialsPath} {USER}@{serverPublicIP}:/home/{USER}/cred.json")
commandsToSetupOnServer.append(f"export GOOGLE_APPLICATION_CREDENTIALS='/home/{USER}/cred.json' ")
runCommandsOnAMachineOverSSH(ssh,commandsToSetupOnServer)


## Start server process
t = threading.Thread(target=runCommandsOnAMachineOverSSH,args=(ssh,commandsToServer))
t.start()


print("Installing dependencies on Client")
sleep(5)
commandsToSetupOnClient = [
    "sudo apt install -y git",
    "git clone https://github.com/GowthamChowta/simple-keyvaluestore.git"    
]
sshClient = setupMachineByhostIP(clientPublicIP)
runCommandsOnAMachineOverSSH(sshClient,commandsToSetupOnClient)

commandsToClient = [
    f"python3 -u simple-keyvaluestore/client.py {SERVERPORT} {serverInternalIP}"
]

runCommandsOnAMachineOverSSH(sshClient,commandsToClient)
print("Installing dependencies")
