from mininet.topo import Topo

"""
Topologia
h1-s1-             s11                -s6-h3
h2-              s12- s22                -h4
               s13- s23- s33
             s14- s24- s34- s44
           s15- s25- s35- s45- s55
         s16- s26- s36- s46- s56- s66
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
        switch6 = self.addSwitch('s6')
        self.addLink(host3,switch6)
        self.addLink(host4,switch6)

        #pierwsza warstwa switchy
        switch11 = self.addSwitch('s11')
        switch12 = self.addSwitch('s12')
        switch13 = self.addSwitch('s13')
        switch14 = self.addSwitch('s14')
        switch15 = self.addSwitch('s15')
        switch16 = self.addSwitch('s16')

        #polaczenie pierwszej warstwy ze switchem1
        self.addLink(switch1, switch11)
        self.addLink(switch1, switch12)
        self.addLink(switch1, switch13)
        self.addLink(switch1, switch14)
        self.addLink(switch1, switch15)
        self.addLink(switch1, switch16)
        
        #druga warstwa switch
        switch22 = self.addSwitch('s22')
        switch23 = self.addSwitch('s23')
        switch24 = self.addSwitch('s24')
        switch25 = self.addSwitch('s25')
        switch26 = self.addSwitch('s26')

        #trzecia warstwa switchy
        switch33 = self.addSwitch('s33')
        switch34 = self.addSwitch('s34')
        switch35 = self.addSwitch('s35')
        switch36 = self.addSwitch('s36')

        #czwarta warstwa switchy
        switch44 = self.addSwitch('s44')
        switch45 = self.addSwitch('s45')
        switch46 = self.addSwitch('s46')        
        
        #piata warstwa switchy
        switch55 = self.addSwitch('s55')
        switch56 = self.addSwitch('s56')
            
        #szosta warstwa switchy
        switch66 = self.addSwitch('s66')

        #laczenie warst
        self.addLink(switch12, switch22)
        self.addLink(switch13, switch23)
        self.addLink(switch14, switch24)
        self.addLink(switch15, switch25)
        self.addLink(switch16, switch26)
        
        self.addLink(switch23, switch33)
        self.addLink(switch24, switch34)
        self.addLink(switch25, switch35)
        self.addLink(switch26, switch36)

        self.addLink(switch34, switch44)
        self.addLink(switch35, switch45)
        self.addLink(switch36, switch46)

        self.addLink(switch45, switch55)
        self.addLink(switch46, switch56)

        self.addLink(switch56, switch66)
    
        #podlaczenie switcha6 ze switchami
        self.addLink(switch6, switch11)
        self.addLink(switch6, switch22)
        self.addLink(switch6, switch33)
        self.addLink(switch6, switch44)
        self.addLink(switch6, switch55)
        self.addLink(switch6, switch66)
           
topos = { 'mytopo': (   lambda: MyTopo()   ) }
