#!/bin/bash
COUNTER=0
DATE=$(date)
while true; do
   COUNTER=$[$COUNTER+1]
   echo "$(date): Uruchomienie: $COUNTER"
   # kill all running dhcp clients - just in case

   rm -f /var/run/dhclient.pid
   echo "$(date): Usuwanie"
   # bring down the interface
   ifconfig h1-eth0 down
   echo "$(date): Interface Down"

   # change the MAC address of the interface and print the new MAC address
   macchanger -a h1-eth0 2>&1 | grep Faked
   echo "$(date): Macchanger"

   # bring the interface up
   ifconfig h1-eth0 up
   echo "$(date): Interface Up"
   # Nie dziala ta czesc
   # make a new DHCP lease
   dhclient h1-eth0 2>&1 | grep DHCPACK
   echo "$(date): New Lease"

   #killall dhclient
   echo "$(date): Zakonczenie: $COUNTER"
done
