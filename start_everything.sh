#!/bin/bash 


# Creating a ssh key and transfering the key to a project
ssh-keygen -t rsa -f ~/.ssh/gcp-ass5 -C chgowt_iu_edu -b 2048
gcloud compute os-login ssh-keys add --key-file=/Users/chowtagowtham/.ssh/gcp-ass5.pub --project=test-chgowt-1 --ttl=30d
# Setting up SSH agent
eval "$(ssh-agent -s)"
ssh-keyadd /Users/chowtagowtham/.ssh/gcp-ass5

## Creating a default network
gcloud compute networks create default
gcloud compute firewall-rules create default-allow-icmp --network default --allow icmp --source-ranges 0.0.0.0/0
gcloud compute firewall-rules create default-allow-ssh --network default --allow tcp:22 --source-ranges 0.0.0.0/0
gcloud compute firewall-rules create default-allow-internal --network default --allow tcp:0-65535,udp:0-65535,icmp --source-ranges 10.128.0.0/9


# Starting key-value server, test client 

python3 instance-management.py

