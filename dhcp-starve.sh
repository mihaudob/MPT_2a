#!/bin/bash

while true; do
   # kill all running dhcp clients - just in case
   killall dhclient
   rm -f /var/run/dhclient.pid

   # bring down the interface
   ifconfig eth0 down

   # change the MAC address of the interface and print the new MAC address
   macchanger -a eth0 2>&1 | grep Faked

   # bring the interface up
   ifconfig eth0 up

   # make a new DHCP lease
   dhclient eth0 2>&1 | grep DHCPACK
done