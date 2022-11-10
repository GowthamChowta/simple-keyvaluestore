#!/bin/bash 
PROJECTID=$(awk -F "=" '/PROJECTID/ {print $2}' config.ini)
USERNAME=$(awk -F "=" '/USERNAME/ {print $2}' config.ini)
STORAGE=$(awk -F "=" '/STORAGE/ {print $2}' config.ini)

echo $PROJECTID
echo $USERNAME
echo $STORAGE

gcloud config set project $PROJECTID
echo 'Enabling api property'
gcloud services enable compute.googleapis.com
echo 'Enabling os login property'
gcloud services enable oslogin.googleapis.com
echo 'Enabling datastore property'
gcloud services enable datastore.googleapis.com
echo 'Enabling firestore property'
gcloud services enable firestore.googleapis.com

# Creating a ssh key and transfering the key to a project
ssh-keygen -t rsa -f ~/.ssh/gcp-ass5 -C $USERNAME -b 2048
gcloud compute os-login ssh-keys add --key-file=/Users/chowtagowtham/.ssh/gcp-ass5.pub --project $PROJECTID --ttl=30d
# Setting up SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/gcp-ass5


## Creating a default network
gcloud compute networks create default
gcloud compute firewall-rules create default-allow-icmp --network default --allow icmp --source-ranges 0.0.0.0/0
gcloud compute firewall-rules create default-allow-ssh --network default --allow tcp:22 --source-ranges 0.0.0.0/0
gcloud compute firewall-rules create default-allow-internal --network default --allow tcp:0-65535,udp:0-65535,icmp --source-ranges 10.128.0.0/9


# Starting key-value server, test client 

python3 instance-management.py $STORAGE

