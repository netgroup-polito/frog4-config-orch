#!/bin/bash
hs="$(cat /etc/hostname)" && echo "127.0.1.1 $hs" >> /etc/hosts
./start_dhcp.sh
sleep 1
cd generic-nfv-configuration-and-management && ./start_dhcp_agent.sh
