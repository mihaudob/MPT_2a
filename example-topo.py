# -*- coding: utf-8 -*-

from mininet.topo import Topo

"""
Topologia
h1-s1-             s11                -s4-h3
h2-              s12- s22                -h4
               s13- s23- s33
             s14- s24- s34- s44

"""
class MyTopo( Topo):
    
    def __init__(self):
        Topo.__init__(self)
        
        #deklaracja 4 hostów
        host1 = self.addHost('h1') #source of traffic 1
        host2 = self.addHost('h2') #source of traffic 2

        host3 = self.addHost('h3') #DHCP Server
        host4 = self.addHost('h4') #DHCP Client
        host5 = self.addHost('h5') #attacker

        #serwer DHCP na h3
'''
        print("*** Start DHCP server on h3 ...")
        host3.cmd('sudo apt-get update')
        host3.cmd('echo "interfaces=\\"h3-eth0\\"" >> /etc/default/isc-dhcp-server')

        dhcp_config = """
          subnet 192.168.16.0 netmask 255.255.255.0 {
            range 192.168.16.20 192.168.16.254;
            interface h3-eth0;
          }
        """

        host3.cmd('echo "%s" >> /etc/dhcp/dhcpd.conf' % dhcp_config)
        host3.cmd("service isc-dhcp-server restart &")
        """
        #klient dhcp na h4
        host4.cmd("ifconfig h4-eth0 0")
        host4.cmd("dhclient h4-eth0")
'''
        #pierwszy switch
        switch1 = self.addSwitch('s1')
        self.addLink(host1, switch1)
        self.addLink(host2, switch1)

        #ostatni switch
        switch4 = self.addSwitch('s4')
        self.addLink(host3,switch4)
        self.addLink(host4,switch4)
        self.addLink(host5,switch4)

        #pierwsza warstwa switchy
        switch11 = self.addSwitch('s11')
        switch12 = self.addSwitch('s12')
        switch13 = self.addSwitch('s13')
        switch14 = self.addSwitch('s14')

        #polaczenie pierwszej warstwy ze switchem1
        self.addLink(switch1, switch11)
        self.addLink(switch1, switch12)
        self.addLink(switch1, switch13)
        self.addLink(switch1, switch14)
        
        #druga warstwa switch
        switch22 = self.addSwitch('s22')
        switch23 = self.addSwitch('s23')
        switch24 = self.addSwitch('s24')

        #trzecia warstwa switchy
        switch33 = self.addSwitch('s33')
        switch34 = self.addSwitch('s34')

        #czwarta warstwa switchy
        switch44 = self.addSwitch('s44')
       
        #laczenie warst
        self.addLink(switch12, switch22)
        self.addLink(switch13, switch23)
        self.addLink(switch14, switch24)
        
        self.addLink(switch23, switch33)
        self.addLink(switch24, switch34)

        self.addLink(switch34, switch44)

        #podlaczenie switcha4 ze switchami
        self.addLink(switch4, switch11)
        self.addLink(switch4, switch22)
        self.addLink(switch4, switch33)
        self.addLink(switch4, switch44)

           
topos = { 'mytopo': (   lambda: MyTopo()   ) }
