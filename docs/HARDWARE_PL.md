# Instrukcja sprzętowa — FoxESS Tseries over TCP

[Powrót do README](../README_PL.md) · [Repozytorium](https://github.com/blasz59150/foxess-tseries-over-tcp)

## 1. Zakres i przykładowa instalacja

Dokument opisuje instalację używaną podczas prac nad projektem: falownik **FoxESS T4-G3**, konwerter **EBYTE NE2-D11 RS485–Ethernet** i Home Assistant OS na HP t620. Inne modele lub wersje firmware mogą zachowywać się inaczej.

```text
FoxESS T4-G3                 EBYTE NE2-D11                 Home Assistant
interfejs RS485  ──RS485──>  RS485 / Ethernet  ──LAN──>   HA OS / integracja
   dane telemetryczne          TCP Server                   TCP client
```

## 2. Co jest potrzebne

- Falownik z obsługiwanym strumieniem telemetrycznym FoxESS T-G3; w instalacji referencyjnej T4-G3.
- EBYTE NE2-D11 skonfigurowany jako konwerter RS485–Ethernet.
- Przewód RS485 odpowiedniego typu oraz przewód Ethernet do lokalnej sieci LAN.
- Zasilanie konwertera zgodne z etykietą i instrukcją producenta.
- Home Assistant OS i dostęp administratora do integracji.

## 3. Podłączenie RS485 — nie zgaduj pinów

1. Wyłącz zasilanie urządzeń przed wykonywaniem połączeń, jeśli wymaga tego instrukcja producenta i procedura instalacyjna. Nie otwieraj części falownika, w której mogą występować niebezpieczne napięcia.
2. Odszukaj w dokumentacji konkretnego wariantu falownika port komunikacyjny przeznaczony do monitoringu/RS485. Nie zakładaj, że każdy port oznaczony COM jest właściwy.
3. Odszukaj na NE2-D11 zaciski wejściowe RS485. Podłącz linię A do zacisku A i B do B **wyłącznie wtedy, gdy oznaczenia obu urządzeń są zgodne**. Oznaczenia A/B bywają różnie interpretowane przez producentów; jeśli brak komunikacji, sprawdź dokumentację i oznaczenia zamiast zmieniać przewody w ciemno.
4. Nie podłączaj przewodu RS485 do zacisków zasilania ani Ethernet. Nie dopisujemy tu numerów pinów ani kolorów przewodów, ponieważ nie zostały potwierdzone dla konkretnej rewizji sprzętu.
5. Podłącz Ethernet konwertera do tej samej sieci LAN co Home Assistant. Nie łącz portu RS485 z portem RJ45 Ethernet.
6. Zasil konwerter zgodnie z jego etykietą/instrukcją. Nie zakładaj, że zasilanie jest dostarczane przez RS485 lub Ethernet.

> **Ważne:** ten dokument nie zastępuje instrukcji elektrycznej FoxESS/EBYTE. Przed publikacją zdjęć lub rysunków zacisków należy potwierdzić je na rzeczywistym urządzeniu.

## 4. Parametry referencyjne EBYTE NE2-D11

Poniższe wartości odpowiadają ustawieniom opisanym dla instalacji używanej w projekcie. Wprowadź je tylko wtedy, gdy pasują do Twojej sieci i sprzętu.

| Parametr | Wartość referencyjna |
|---|---|
| Tryb Socket A | TCP Server |
| Port TCP | `502` |
| Baud rate | `9600` |
| Data bits | `8` |
| Parity | None / brak |
| Stop bits | `1` |
| Pack Time | `1` |
| Pack Length | `1024` |
| IP konwertera w instalacji referencyjnej | `192.168.0.69` |
| IP Home Assistant w instalacji referencyjnej | `192.168.0.67` |

**Adresy IP są przykładowymi adresami prywatnymi z instalacji referencyjnej, a nie wymaganymi adresami.** Ustaw adres zgodny z własną podsiecią i najlepiej zarezerwuj go w DHCP/routerze. Port `502` jest tutaj portem TCP dla strumienia FoxESS przez bramkę — nie oznacza, że ten strumień jest standardowym Modbusem TCP.

## 5. Jak sprawdzić połączenie

1. Sprawdź, czy konwerter odpowiada pod swoim adresem IP w LAN.
2. Sprawdź, czy usługa TCP Server nasłuchuje na skonfigurowanym porcie.
3. Skonfiguruj integrację, wpisując adres IP konwertera i port.
4. Po uruchomieniu obserwuj encję `Online`, `TCP Diagnostics`, `Last TCP Packet` i `Last Valid Frame`.
5. Jeśli nie ma danych, sprawdź logi integracji, zasilanie konwertera, RS485, port TCP i parametry UART. Nie zmieniaj zdalnie ustawień konwertera, jeśli utrata połączenia odetnie Ci możliwość przywrócenia dostępu.

## 6. Bezpieczeństwo

- Nie przekierowuj portu konwertera na routerze do internetu.
- Używaj sieci LAN/VLAN z dostępem ograniczonym do zaufanych urządzeń.
- Nie udostępniaj publicznie zrzutów panelu konwertera zawierających dane sieciowe, których nie chcesz ujawniać.
- Nie wykonuj prac przy instalacji elektrycznej falownika bez odpowiednich kwalifikacji.
