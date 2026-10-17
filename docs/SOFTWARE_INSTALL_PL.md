# Instalacja i konfiguracja — Home Assistant

[README PL](../README_PL.md) · [Dashboard](../dashboards/foxess_tcp.yaml) · [Repozytorium](https://github.com/blasz59150/foxess-tseries-over-tcp)

## Wymagania

- Home Assistant z obsługą integracji niestandardowych i przepływów konfiguracji.
- Łączność TCP z konwerterem EBYTE w sieci lokalnej.
- Folder `custom_components/foxess_push/` z plikami tej integracji.

## Instalacja ręczna

1. Pobierz ZIP z sekcji Releases repozytorium (jeśli wydanie zostało opublikowane). Jeśli repozytorium nie ma jeszcze wydania, użyj archiwum źródłowego dostarczonego wraz z projektem.
2. Skopiuj cały folder `custom_components/foxess_push` do `/config/custom_components/foxess_push/`. Upewnij się, że plik `manifest.json` znajduje się bezpośrednio w tym folderze.
3. Sprawdź, czy nie powstała błędna struktura z dodatkowym zagnieżdżeniem, np. `custom_components/foxess_push/foxess_push/`.
4. Uruchom ponownie Home Assistant.
5. Przejdź do **Ustawienia → Urządzenia i usługi → Dodaj integrację** i wyszukaj **FoxESS Tseries over TCP**.
6. Wprowadź adres IP konwertera i port TCP (w instalacji referencyjnej `192.168.0.69`, `502`).
7. Otwórz ustawienia integracji i sprawdź wartości timeoutu, odstępu ponawiania i progu OFFLINE.

## Opcje połączenia

| Opcja | Domyślna | Znaczenie |
|---|---:|---|
| Seconds without TCP data | 45 s | Po takim czasie bez danych TCP połączenie jest uznawane za zawieszone i ponawiane. |
| Reconnect delay | 5 s | Przerwa pomiędzy próbami ponownego połączenia. |
| Offline after | 90 s | Czas bez poprawnej ramki telemetrycznej, po którym encja `Online` przechodzi na OFFLINE. |

Zmiana opcji przeładowuje konfigurację integracji. Zbyt krótki timeout może powodować niepotrzebne ponowne połączenia; dobierz wartości do rzeczywistego rytmu ramek.

## Encje

Integracja tworzy encje pomiarowe dla mocy, energii, parametrów trzech faz, wejść PV i temperatur. Dodatkowo udostępnia: stan połączenia, ostatni pakiet TCP, ostatnią poprawną ramkę i encję `TCP Diagnostics` z atrybutami zdarzeń. Nazwy i identyfikatory encji mogą zostać zmienione przez Home Assistant lub istniejący rejestr encji.

## Dashboard FoxessTCP

Plik: [`dashboards/foxess_tcp.yaml`](../dashboards/foxess_tcp.yaml).

1. W Home Assistant utwórz nowy dashboard i wybierz tryb YAML albo skopiuj zawartość pliku do konfiguracji dashboardu YAML.
2. Po pierwszym uruchomieniu sprawdź identyfikatory encji w **Narzędzia deweloperskie → Stany**.
3. Jeśli istniejące encje mają inne ID, popraw je w YAML. Nie zmieniaj istniejących ID tylko po to, by pasowały do przykładu — może to przerwać automatyzacje.
4. Widok diagnostyczny pokazuje stan i zdarzenia dostępne w kodzie; nie jest to surowy rejestr każdego bajtu TCP.

## HACS

Repozytorium zawiera metadane `hacs.json`, ale nie należy zakładać, że projekt został zatwierdzony przez HACS. Do czasu sprawdzenia wymagań aktualnej wersji HACS instalacja ręczna jest podstawową, udokumentowaną metodą. Po publikacji repozytorium można dodać je w HACS jako repozytorium niestandardowe tylko wtedy, gdy HACS akceptuje jego strukturę i metadane.

## Diagnostyka i ograniczenia

- `TCP Diagnostics` przechowuje ostatnie zdarzenia połączenia w pamięci; historia jest ograniczona i znika po restarcie Home Assistant.
- Liczniki dotyczące ramek opisują to, co otrzymał i rozpoznał kod, a nie gwarantują wykrycia wszystkich błędów transmisji.
- **CRC ramki nie jest w tej wersji weryfikowane.** `invalid_frames` oznacza ramki, które kod odrzucił z powodu rozpoznanej niezgodności struktury/długości/typu, a nie błędy CRC.
- `Last TCP Packet` oznacza czas ostatniego odebranego fragmentu TCP, nie odtworzenie całego surowego pakietu jako tekstu.
- Nie ma jeszcze pełnego eksportu surowych bajtów ostatniej ramki ani niezawodnej identyfikacji „zgubionych pakietów” na poziomie aplikacji. Dokumentujemy przerwę w odbiorze, rozłączenia i próby ponownego połączenia.

## Usuwanie problemów

1. Sprawdź, czy adres IP i port są prawidłowe.
2. Sprawdź logi Home Assistant pod kątem błędów `foxess_push`.
3. Sprawdź, czy konwerter jest osiągalny w LAN i czy jest w trybie TCP Server.
4. Sprawdź RS485 A/B według instrukcji urządzeń; nie zgaduj pinów.
5. Sprawdź, czy ustawienia UART są `9600 8N1`.
6. Nie publikuj pełnych logów, jeśli zawierają dane prywatne.
