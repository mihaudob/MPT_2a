#!/bin/bash
#konfiguracja dhcp na h5 atakujacym
dhcp_config1="subnet 10.0.0.0 netmask 255.255.255.0 {
interface h5-eth0;
range 10.0.0.150 10.0.0.200;
option subnet-mask 255.255.255.0;
default-lease-time 6200;
max-lease-time 70000;
}"

echo $dhcp_config1 > /etc/dhcp/dhcpd.conf
echo "interfaces=\\"h5-eth0\\"" > /etc/default/isc-dhcp-server

service isc-dhcp-server restart &
