# Sieć i konfiguracja bramki EBYTE NE2-D11

[Instrukcja sprzętowa](HARDWARE_PL.md) · [Instalacja software](SOFTWARE_INSTALL_PL.md) · [Repozytorium](https://github.com/blasz59150/foxess-tseries-over-tcp)

## Topologia referencyjna

- Home Assistant: `192.168.0.67`
- EBYTE NE2-D11: `192.168.0.69`
- Konwerter: Socket A jako **TCP Server**, port `502`
- UART: `9600`, `8` bitów danych, brak parzystości, `1` bit stopu (8N1)
- Pack Time: `1`; Pack Length: `1024`

Adresy IP są tylko przykładem. Dostosuj je do własnej sieci i unikaj konfliktu adresów.

## Konfiguracja krok po kroku

1. Otwórz panel webowy konwertera, korzystając z jego instrukcji i aktualnego adresu IP.
2. Wybierz port/socket używany do RS485 i ustaw tryb TCP Server.
3. Ustaw port TCP zgodny z portem wpisanym później w integracji. W konfiguracji referencyjnej jest to `502`.
4. Ustaw parametry UART na `9600 8N1`.
5. Ustaw Pack Time `1` i Pack Length `1024`, jeśli te opcje występują w danej wersji firmware. Nazwy pól mogą różnić się między rewizjami.
6. Zapisz konfigurację i restartuj konwerter tylko wtedy, gdy masz możliwość odzyskania dostępu.
7. Z poziomu Home Assistant dodaj integrację, wpisując IP i port konwertera.

## Czego nie należy mylić

- **TCP Server** oznacza, że konwerter nasłuchuje na porcie, a integracja Home Assistant łączy się jako klient TCP.
- **RS485** to fizyczna warstwa szeregowa pomiędzy falownikiem i konwerterem.
- **Protokół FoxESS push** ma własne ramki telemetryczne. Port `502` sam w sobie nie czyni go standardowym Modbus TCP.
- W tej wersji kod odczytuje telemetrię. Nie należy traktować jej jako interfejsu do sterowania falownikiem.

## Dostępność i odzyskiwanie

Domyślne opcje integracji: brak danych TCP przez 45 s → rozłączenie i ponowienie; przerwa między próbami 5 s; stan `OFFLINE` po 90 s bez poprawnej ramki telemetrycznej. Można je zmienić w ustawieniach integracji. To wartości konfiguracyjne, nie gwarancja, że każdy falownik będzie wysyłał ramki w takim samym rytmie.

Jeśli utracisz dostęp do panelu konwertera, nie próbuj losowych ustawień. Najpierw sprawdź adres IP, podsieć, kabel Ethernet i instrukcję konkretnej rewizji sprzętu.
