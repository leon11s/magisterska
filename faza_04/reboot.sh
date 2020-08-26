#!/bin/bash

container_name="prod-ubuntu-ssh-k8s-edgenet-5"

# Define a timestamp function
timestamp() {
  date +"%Y-%m-%d %H:%M:%S"
}

echo "-----------------------" >> compose_reboot.log
echo "Reboot ${container_name} at:"  >> compose_reboot.log
timestamp >> compose_reboot.log
docker-compose down &>> compose_reboot.log
sleep 5
docker-compose up -d &>> compose_reboot.log
