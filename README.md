# MPT_2a
Projekt sieci z kontrolerem która będzie posiadała Firewall przed atakiem DHCP Spoofing oraz zapewniała usprawnioną kontrolę QoS.

## Środowisko 

1. Pracujemy z Ubuntu wersja 18.+
1. Pobierz Mininet z globalnej dystrubucji ```sudo apt-get install mininet```
1. Sklonuj GITa
1. Zainstaluj pip ```sudo apt install python3-pip```
1. Pobierz RYU ```sudo pip3 install ryu```
1. Pobierz dhcp server ```sudo apt-get install service isc-dhcp-server ```

## Kontroler

Kod źródłowy kontrolera znajduje się w folderze /ryu.
Korzystamy z pliku ```simple_switch.py``` który ma prosty mechanizm floodowania i narazie nie dziala.

Plik ten pochodzi z ```/ryu/ryu/app```. Mozemy utworzyć nasz kontroler na jego podstawie.
Import jest z oficjalnej dystrubucji ```ryu``` wiec jeśli chcemy to całkowicie usamodzielnic potrzeba wielu zmian ktore uwazam za niepotrzebne.

## Uruchamianie
1. Idź do folderu projektu.
2. W jednym terminalu uruchom topologię ze zdalnym kontrolerem.
```
sudo mn --custom example-topo.py --topo mytopo --mac --controller remote --switch ovsk
```

3. W kolejnym terminalu uruchom kontroler RYU.

```
ryu-manager $PWD/simple_switch.py
```

## Żródła
- Instrukcja do laboratorium 1. Zapoznanie ze środowiskiem Mininet.
- https://ernie55ernie.github.io/sdn/2019/03/25/install-mininet-and-ryu-controller.html
- https://github.com/faucetsdn/ryu/blob/master/ryu/app/simple_switch.py
- http://sdnhub.org/resources/useful-mininet-setups/
- https://ryu.readthedocs.io/en/latest/parameters.html
