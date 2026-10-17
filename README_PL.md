<p align="center"><img src="assets/logo.svg" alt="FoxESS Tseries over TCP" width="820"></p>

# FoxESS Tseries over TCP

**Niestandardowa integracja Home Assistant do odbioru lokalnej telemetrii FoxESS T-series przez TCP.** Projekt społecznościowy autorstwa `blasz59150`; nie jest oficjalnym produktem FoxESS ani Home Assistant.

[Repozytorium GitHub](https://github.com/blasz59150/foxess-tseries-over-tcp) · [Zgłoszenia](https://github.com/blasz59150/foxess-tseries-over-tcp/issues) · [English README](README.md) · [Licencja GPL-3.0-or-later](LICENSE)

## Stan projektu

Wersja źródłowa `1.1.0`. Kod i dokumentacja są przygotowane do przeglądu, ale **nie oznacza to testu na żywym falowniku ani zatwierdzenia w HACS**. Nie publikuj tego jako sprawdzonego wydania, dopóki nie przejdzie walidacji w docelowym Home Assistant.

## Funkcje zaimplementowane w kodzie

- konfiguracja adresu IP i portu TCP przez interfejs Home Assistant;
- opcje timeoutu braku danych, przerwy między próbami i progu OFFLINE;
- odbiór ramek FoxESS push przez lokalne TCP i dekodowanie wybranych pól telemetrii;
- encje dla mocy, energii, faz sieciowych, stringów PV i temperatur;
- stan `Online`, czas ostatniego fragmentu TCP, czas ostatniej poprawnej ramki i encja `TCP Diagnostics`;
- ograniczona historia zdarzeń połączenia w pamięci;
- przykładowy dashboard YAML.

### Ograniczenia, które trzeba znać

- CRC16 nie jest obecnie weryfikowane.
- `Last TCP Packet` to znacznik czasu ostatniego fragmentu danych TCP, a nie zapis całego surowego pakietu.
- Diagnostyka pokazuje zdarzenia i liczniki, ale nie gwarantuje wykrycia każdego błędu transmisji ani wszystkich utraconych ramek.
- ID encji mogą się różnić zależnie od rejestru Home Assistant.
- Nie potwierdzono zgodności z każdym modelem i wersją firmware.

## Szybki start

1. Skopiuj `custom_components/foxess_push/` do `/config/custom_components/foxess_push/`.
2. Uruchom ponownie Home Assistant.
3. Wybierz **Ustawienia → Urządzenia i usługi → Dodaj integrację → FoxESS Tseries over TCP**.
4. Podaj adres IP konwertera i port TCP. W instalacji referencyjnej EBYTE NE2-D11 używa `192.168.0.69:502`; w swojej sieci wpisz własne wartości.
5. W ustawieniach integracji dostosuj parametry ponownego łączenia, jeśli to konieczne.
6. Zaimportuj lub skopiuj `dashboards/foxess_tcp.yaml`, a następnie dopasuj identyfikatory encji.

**Szczegółowe instrukcje:**
- [Hardware: falownik, RS485 i konwerter](docs/HARDWARE_PL.md)
- [Konfiguracja sieci i EBYTE NE2-D11](docs/NETWORK_AND_GATEWAY_PL.md)
- [Instalacja i konfiguracja Home Assistant](docs/SOFTWARE_INSTALL_PL.md)
- [Protokół i ustalenia z testów](docs/PROTOCOL_AND_RESEARCH_PL.md)

## Sprzęt i ustawienia referencyjne

| Element | Wartość referencyjna |
|---|---|
| Falownik | FoxESS T4-G3 |
| Konwerter | EBYTE NE2-D11 RS485–Ethernet |
| Tryb konwertera | TCP Server |
| Port TCP | `502` |
| UART | `9600 8N1` |
| Pack Time / Pack Length | `1` / `1024` |
| HA / EBYTE w instalacji referencyjnej | `192.168.0.67` / `192.168.0.69` |

To ustawienia z jednej instalacji, nie uniwersalna recepta. Nie podano numerów pinów ani kolorów przewodów, bo muszą być potwierdzone dla konkretnej rewizji sprzętu. Port TCP `502` nie oznacza, że odbierany strumień jest standardowym Modbus TCP.

## Dashboard

Plik: [`dashboards/foxess_tcp.yaml`](dashboards/foxess_tcp.yaml). Dashboard jest przykładem; przed użyciem sprawdź nazwy encji w Home Assistant. Nie zmienia on automatyzacji ani konfiguracji urządzeń samodzielnie.

## HACS

Repozytorium zawiera plik `hacs.json`, ale nie jest to równoznaczne z akceptacją projektu przez HACS. Do czasu sprawdzenia bieżących wymagań HACS zalecana jest instalacja ręczna.

## Autorstwo i licencja

Projekt jest udostępniany na warunkach [GNU General Public License v3 lub nowszej](LICENSE). Licencja nie blokuje kopiowania, ale przy rozpowszechnianiu kopii i modyfikacji wymaga przestrzegania jej warunków, w tym udostępnienia odpowiedniego kodu źródłowego. Zachowuj historię zmian, oznaczenia autora i informacje o pochodzeniu.

- Autor / maintainer: `blasz59150`
- Repozytorium docelowe: https://github.com/blasz59150/foxess-tseries-over-tcp
- [AUTHORS](AUTHORS.md) · [CHANGELOG](CHANGELOG.md) · [SECURITY](SECURITY.md)

## Bezpieczeństwo

Nie wystawiaj portu konwertera do internetu. Nie wykonuj prac wewnątrz falownika bez kwalifikacji. Zgłaszając problem, usuń z logów prywatne dane sieciowe.
