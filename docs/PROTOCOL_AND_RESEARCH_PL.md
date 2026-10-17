# Protokół i ustalenia badawcze

## Źródła i zakres

Projekt korzysta z dokumentu protokołu FoxESS „Monitoring Protocol”, wersja B1.05.00/B1.05.01, który wskazuje zastosowanie do T-G3 Manager 1.22 i nowszych (oraz T-G2 Manager 1.35 i nowszych). Dokument podaje parametry RS485 9600 bps, 8 bitów danych, brak parzystości, 1 bit stopu i big-endian dla pól wielobajtowych.

Dokument producenta opisuje ramkę telemetryczną z nagłówkiem `7E 7E`, kodem funkcji, znacznikiem czasu, długością, danymi użytkownika, CRC16 little-endian i zakończeniem `E7 E7`. W dokumencie pojawia się interwał 90 s dla określonego typu danych; nie należy zakładać, że każda wersja firmware i każda ramka mają identyczną częstotliwość.

## Wnioski z testów projektu

- Próby interpretowania strumienia jako standardowego Modbus TCP nie odpowiadały zaobserwowanym ramkom.
- W strumieniu zaobserwowano ramki zaczynające się `7E 7E` i kończące `E7 E7`, zgodne z opisem FoxESS push.
- Integracja odbiera dane z lokalnego serwera TCP konwertera i mapuje wybrane pola telemetrii.

## Ważne ograniczenia implementacji

- Wersja 1.1.0 nie weryfikuje CRC16, mimo że pole CRC występuje w protokole.
- Parser weryfikuje wybrane elementy struktury, długość ramki i zakończenie, a następnie mapuje znane pola.
- Dekodowanie jest oparte na aktualnie mapowanym układzie danych i wymaga dalszej walidacji dla innych modeli/wersji firmware.
- Odbiór TCP w kawałkach nie jest tym samym co granice ramek protokołu; parser buforuje dane, ale diagnostyka nie przechowuje wszystkich surowych ramek.

## Materiały producenta

W repozytorium można umieścić kopie dokumentów tylko wtedy, gdy ich warunki dystrybucji na to pozwalają. W przeciwnym razie podaj nazwę, wersję i źródło, zamiast dodawać plik bez zgody. W rozmowie użyto pliku `Monitoring_Protocol_VB1.05.00_20.pdf`; przed publikacją sprawdź warunki jego redystrybucji.
