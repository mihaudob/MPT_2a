#!/bin/bash
COUNTER=0
DATE=$(date)
while true; do
   COUNTER=$[$COUNTER+1]
   echo "${DATE}: Uruchomienie: $COUNTER"
   # kill all running dhcp clients - just in case

   rm -f /var/run/dhclient.pid
   echo "${DATE}: Usuwanie"
   # bring down the interface
   ifconfig h1-eth0 down
   echo "${DATE}: Interface Down"

   # change the MAC address of the interface and print the new MAC address
   macchanger -a h1-eth0 2>&1 | grep Faked
   echo "${DATE}: Macchanger"

   # bring the interface up
   ifconfig h1-eth0 up
   echo "${DATE}: Interface Up"
   # Nie dziala ta czesc
   # make a new DHCP lease
   dhclient h1-eth0 2>&1 | grep DHCPACK
   echo "${DATE}: New Lease"

   #killall dhclient
   echo "${DATE}: Zakonczenie: $COUNTER"
done
