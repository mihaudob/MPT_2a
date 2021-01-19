#!/bin/bash

while true; do
   # kill all running dhcp clients - just in case

   rm -f /var/run/dhclient.pid

   # bring down the interface
   ifconfig h1-eth0 down

   # change the MAC address of the interface and print the new MAC address
   macchanger -a h1-eth0 2>&1 | grep Faked

   # bring the interface up
   ifconfig h1-eth0 up

   # make a new DHCP lease
   dhclient h1-eth0 2>&1 | grep DHCPACK

   killall dhclient
done
