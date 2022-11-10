# TODO Need to put reference
# TODO Need to put reference
from time import sleep
import os
import threading
from google.api_core.extended_operation import ExtendedOperation

from gcpPythonClientHelper import create_instance, delete_bucket, delete_instance, disk_from_image, getInstanceExternalInternalIpByName, read_ini, runCommandsOnAMachineOverSSH, setupMachineByhostIP
import sys
from google.cloud import storage



STORAGE = sys.argv[1]

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
bucketName = params["GCP"]["bucketName"]



boot_disk_server = disk_from_image(disk_type,10,True,source_image=source_image)
boot_disk_client = disk_from_image(disk_type,10,True,source_image=source_image)

machine_names = [params["GCP"]["SERVERNAME"],params["GCP"]["CLIENTNAME"]]

commandsToSetupOnServer = [
    "sudo apt install -y git",
    "git clone https://github.com/GowthamChowta/simple-keyvaluestore.git",
    "sudo apt install -y python3-pip",    
    "sudo pip install google-cloud-core",
    "sudo pip install google-cloud-firestore",
    "sudo pip install google-cloud-compute" ,
    "sudo pip install paramiko",
    "sudo pip install google-cloud-storage"
]
commandsToSetupOnClient = [
    "sudo apt install -y git",
    "git clone https://github.com/GowthamChowta/simple-keyvaluestore.git"    
]
commandsToServer = [
        f"python3 -u simple-keyvaluestore/server.py {SERVERPORT} {STORAGE}"
    ]
commandsToSetupOnClient = [
    "sudo apt install -y git",
    "git clone https://github.com/GowthamChowta/simple-keyvaluestore.git"    
]

def setupServer():
    
    print("Starting server machine")
    ## Starting server machine
    create_instance(project_id=PROJECTID,zone=ZONE,instance_name=machine_names[0],disks=[boot_disk_server],machine_type="e2-medium",external_access=True)
    serverPublicIP,serverInternalIP = getInstanceExternalInternalIpByName(machine_names[0])
    print(f"Server Public IP address is {serverPublicIP}")
    print(f"Removing known hosts if exists for {serverPublicIP}")
    os.system(f"ssh-keygen -R {serverPublicIP}")
    return serverPublicIP, serverInternalIP

def setupClient():    
    ## Starting client machine
    print("Starting Client machine")
    create_instance(project_id=PROJECTID,zone=ZONE,instance_name=machine_names[1],disks=[boot_disk_client],machine_type="e2-micro",external_access=True)
    clientPublicIP, clientInternalIP = getInstanceExternalInternalIpByName(machine_names[1])
    print(f"Client Public IP address is {clientPublicIP}")
    print(f"Removing known hosts if exists for {clientPublicIP}")
    os.system(f"ssh-keygen -R {clientPublicIP}")
    return clientPublicIP, clientInternalIP

def sendDefaultApplicationCredentialsFileToServer(serverPublicIP):
    print("Sending application credentials to the server machine")
    ssh = setupMachineByhostIP(serverPublicIP)
    ftp_client=ssh.open_sftp()
    ftp_client.put(applicationCredentialsPath, f"/home/{USER}/cred.json")
    ftp_client.close()


def installDependenciesOnServer(serverPublicIP):
    print("Installing dependencies on Server")
    ssh = setupMachineByhostIP(serverPublicIP)
    ## Copying the cred.json file to the server
    # commandsToSetupOnServer.append(f"export GOOGLE_APPLICATION_CREDENTIALS='/home/{USER}/cred.json' ")
    runCommandsOnAMachineOverSSH(ssh,commandsToSetupOnServer)
    ## Start server process
    t = threading.Thread(target=runCommandsOnAMachineOverSSH,args=(ssh,commandsToServer))
    t.start()    
    

def installDependenciesOnClient(clientPublicIP, serverInternalIP):
    sshClient = setupMachineByhostIP(clientPublicIP)
    runCommandsOnAMachineOverSSH(sshClient,commandsToSetupOnClient)
    commandsToClient = [
        f"python3 -u simple-keyvaluestore/client.py {SERVERPORT} {serverInternalIP}"
    ]
    runCommandsOnAMachineOverSSH(sshClient,commandsToClient)
    print("Client request successfull")


serverPublicIP, serverInternalIP = setupServer()
clientPublicIP, clientInternalIP = setupClient()
sendDefaultApplicationCredentialsFileToServer(serverPublicIP)
installDependenciesOnServer(serverPublicIP)
installDependenciesOnClient(clientPublicIP, serverInternalIP)
print("Completed key-value store")

# delete_instance(project_id=PROJECTID, zone=ZONE,machine_name=machine_names[0])
# delete_instance(project_id=PROJECTID, zone=ZONE,machine_name=machine_names[1])
# delete_bucket(storage, bucket_name=bucketName)



