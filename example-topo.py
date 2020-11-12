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
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')

        host3 = self.addHost('h3')
        host4 = self.addHost('h4')

        #pierwszy switch
        switch1 = self.addSwitch('s1')
        self.addLink(host1, switch1)
        self.addLink(host2, switch1)

        #ostatni switch
        switch6 = self.addSwitch('s4')
        self.addLink(host3,switch4)
        self.addLink(host4,switch4)

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

        #podlaczenie switcha6 ze switchami
        self.addLink(switch4, switch11)
        self.addLink(switch4, switch22)
        self.addLink(switch4, switch33)
        self.addLink(switch4, switch44)

           
topos = { 'mytopo': (   lambda: MyTopo()   ) }
