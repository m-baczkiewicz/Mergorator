# Wtyczka MergeConcat dla QGIS

## Opis
Prosta i wydajna wtyczka do łączenia zaznaczonych obiektów wektorowych, która jednocześnie łączy (konkatenuje) wartości z wybranego pola atrybutów. Idealna do pracy z danymi geodezyjnymi, np. przy scalaniu działek ewidencyjnych.

## Główne funkcje
- **Łączenie geometrii**: Tworzy jedną, wspólną geometrię z wielu zaznaczonych obiektów.
- **Inteligentna konkatenacja atrybutów**: Automatycznie znajduje pole o nazwie `nr_dzialki` (wielkość liter nie ma znaczenia) i łączy unikalne numery w jeden ciąg znaków, oddzielony przecinkami.
- **Kopiowanie pozostałych atrybutów**: Atrybuty dla nowego obiektu są kopiowane z tego obiektu, który przed połączeniem miał największą powierzchnię.
- **Walidacja geometrii**: Wtyczka automatycznie próbuje naprawić nieprawidłowe geometrie przed ich połączeniem, co zwiększa stabilność operacji.
- **Integracja z sesją edycyjną QGIS**:
  - Jeśli warstwa nie jest w trybie edycji, wtyczka automatycznie go włączy, wykona operację i zapisze zmiany.
  - Jeśli warstwa jest już w trybie edycji, wtyczka dokona zmian w ramach istniejącej sesji, pozwalając użytkownikowi na kontynuowanie pracy i ręczne zapisanie zmian.

## Instalacja

### Zalecana metoda: Instalacja z pliku ZIP
1. Pobierz plik `MergeConcat.zip`.
2. W QGIS przejdź do menu `Wtyczki` -> `Zarządzaj i instaluj wtyczki...`.
3. Wybierz zakładkę `Zainstaluj z pliku ZIP`.
4. Wskaż pobrany plik `MergeConcat.zip` i kliknij `Zainstaluj wtyczkę`.
5. Wtyczka pojawi się w zakładce `Zainstalowane`. Upewnij się, że jest włączona (zaznaczony checkbox).

### Metoda ręczna (dla zaawansowanych)
1. Rozpakuj plik `MergeConcat.zip`.
2. Skopiuj folder `MergeConcat` do katalogu wtyczek QGIS:
   - **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3. Uruchom ponownie QGIS.

## Jak używać?
1. Otwórz w QGIS warstwę wektorową, którą chcesz edytować (np. plik Shapefile lub warstwę w GeoPackage).
2. Zaznacz co najmniej dwa obiekty, które chcesz połączyć.
3. Kliknij ikonę wtyczki MergeConcat na pasku narzędzi.
4. Gotowe! Obiekty zostaną połączone zgodnie z opisanymi zasadami.


## Logowanie
Wszystkie operacje i ewentualne błędy są zapisywane w **Panelu komunikatów z dziennika** w QGIS (`Widok` -> `Panele`). Sprawdzaj zakładkę **`MergeConcat`**, aby śledzić, co robi wtyczka.

## Autor
*   **Michał Baczkiewicz**
*   Email: `michal.baczkiewicz@at.agro.pl`

## Historia zmian
*   **v1.5** (2025-06-30): Poprawiono metodę sprawdzania statusu edycji dla kompatybilności z różnymi wersjami QGIS. Ulepszono obsługę błędów.
*   **v1.4** (2025-06-30): Wprowadzono inteligentne zarządzanie sesją edycyjną.
*   **v1.3** (2025-06-25): Pierwsza stabilna, działająca wersja z walidacją geometrii.