# MPT_2a
Projekt sieci z kontrolerem która będzie posiadała Firewall przed atakiem DHCP Spoofing oraz zapewniała usprawnioną kontrolę QoS.

## Środowisko 

1. Pracujemy z Ubuntu wersja 18.+
1. Pobierz Mininet z globalnej dystrubucji ```sudo apt-get install mininet```
1. Sklonuj GITa
1. Zainstaluj pip ```sudo apt install python3-pip```
1. Pobierz RYU ```sudo pip3 install ryu```
1. Pobierz dhcp server ```sudo apt-get install service isc-dhcp-server ```
1. Wizualizacja minineta ```sudo apt-get install python-imaging-tk```

## Kontroler

Kod źródłowy kontrolera znajduje się w folderze /ryu.
Korzystamy z pliku ```simple_switch.py``` który ma prosty mechanizm floodowania i narazie nie dziala.

Skopiowalem dwa pliki simple_switch_stp oraz simple_switch_13 ( znajduje sie w folderze /controller).
Obecnie dziala komunikacja w sieci - do ustawienia budowa i skladnia.

## Uruchamianie
1. Idź do folderu projektu.

2. W terminalu uruchom kontroler RYU.

```
ryu-manager $PWD/simple_switch_stp.py
```

Ten plik to kopia pliku:
$PWD/ryu/ryu/app/simple_switch_stp_13.py

3. W jednym terminalu uruchom topologię ze zdalnym kontrolerem.

Opcja A: Jedynie output z terminala.
```
sudo mn --custom example-topo.py --topo mytopo --mac --controller remote --switch ovsk
```

Opcja B: Wraz z narzedziem do wizualizacji miniNAM:
```
sudo python MiniNAM.py --custom example-topo.py --mac --topo mytopo --controller remote
```

### Wazne

* Learning zabiera duzo czasu - przyklad:
```
mininet> h1 ping h2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
From 10.0.0.1 icmp_seq=9 Destination Host Unreachable
From 10.0.0.1 icmp_seq=10 Destination Host Unreachable
From 10.0.0.1 icmp_seq=11 Destination Host Unreachable
From 10.0.0.1 icmp_seq=12 Destination Host Unreachable
From 10.0.0.1 icmp_seq=13 Destination Host Unreachable
From 10.0.0.1 icmp_seq=14 Destination Host Unreachable
From 10.0.0.1 icmp_seq=15 Destination Host Unreachable
From 10.0.0.1 icmp_seq=16 Destination Host Unreachable
From 10.0.0.1 icmp_seq=17 Destination Host Unreachable
From 10.0.0.1 icmp_seq=18 Destination Host Unreachable
From 10.0.0.1 icmp_seq=19 Destination Host Unreachable
From 10.0.0.1 icmp_seq=20 Destination Host Unreachable
From 10.0.0.1 icmp_seq=21 Destination Host Unreachable
From 10.0.0.1 icmp_seq=22 Destination Host Unreachable
From 10.0.0.1 icmp_seq=23 Destination Host Unreachable
64 bytes from 10.0.0.2: icmp_seq=25 ttl=64 time=1027 ms
64 bytes from 10.0.0.2: icmp_seq=24 ttl=64 time=2051 ms
```
## Żródła
- Instrukcja do laboratorium 1. Zapoznanie ze środowiskiem Mininet.
- https://ernie55ernie.github.io/sdn/2019/03/25/install-mininet-and-ryu-controller.html
- https://github.com/faucetsdn/ryu/blob/master/ryu/app/simple_switch.py
- http://sdnhub.org/resources/useful-mininet-setups/
- https://ryu.readthedocs.io/en/latest/parameters.html
- https://github.com/uccmisl/MiniNAM/tree/master/Examples/Routing
