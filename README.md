# <img src="icon.png" width="48" align="center"> Mergorator

![Plugin Version](https://img.shields.io/badge/Wersja-2.0.0-blue)
![QGIS Version](https://img.shields.io/badge/QGIS-3.16%2B-green)
![License](https://img.shields.io/badge/Licencja-MIT-lightgrey)

## Opis
Wtyczka została stworzona na potrzeby firmy A.T w celu automatyzacji powtarzalnych czynności i uproszczenia pracy z danymi przestrzennymi. Jej celem jest zwiększenie efektywności oraz ograniczenie liczby błędów podczas codziennej pracy z warstwami wektorowymi.
Prosta i wydajna wtyczka do łączenia zaznaczonych obiektów wektorowych, która jednocześnie łączy (konkatenuje) wartości z wybranego pola atrybutów. Idealna do pracy z danymi geodezyjnymi, np. przy scalaniu działek ewidencyjnych.

**Mergorator** to prosta, ale potężna wtyczka do QGIS, stworzona z myślą o efektywnej pracy z danymi wektorowymi, zwłaszcza w formacie **Shapefile**. Jej głównym zadaniem jest łączenie zaznaczonych obiektów (np. działek ewidencyjnych) w jeden i automatyczna konkatenacja (scalanie) ich atrybutów z wybranego pola.

Wtyczka została zaprojektowana, aby rozwiązywać typowe problemy napotykane podczas edycji plików SHP, takie jak błędy zapisu spowodowane pracą na warstwach tymczasowych czy przekroczeniem limitu długości pola atrybutu.

### Główne Funkcje

*   **Łączenie geometrii**: Łączy geometrię dwóch lub więcej zaznaczonych obiektów.
*   **Inteligentne kopiowanie atrybutów**: Wszystkie atrybuty nowego obiektu są kopiowane z największego poligonu źródłowego.
*   **Konkatenacja numerów działek**: Automatycznie znajduje pole o nazwie `nr_dzialki` i scala wartości z tego pola ze wszystkich łączonych obiektów w jeden, posortowany ciąg tekstowy (np. `12,13,15/2`).

## Description

**Mergorator** is a simple yet powerful QGIS plugin designed for efficient work with vector data, especially the **Shapefile** format. Its main purpose is to merge selected features (e.g., land parcels) into a single feature and automatically concatenate their attributes from a specified field.

The plugin was designed to solve common issues encountered while editing SHP files, such as save errors caused by editing temporary layers or exceeding attribute field length limits.

### Key Features

*   **Merge Geometries**: Merges the geometry of two or more selected features.
*   **Smart Attribute Copying**: All attributes for the new feature are copied from the largest source polygon.
*   **Parcel Number Concatenation**: Automatically finds a field named `nr_dzialki` and merges values from this field from all source features into a single, sorted string (e.g., `12,13,15/2`).
*   **Shapefile-Specific Safeguards**: Built-in mechanisms to protect against:
    *   Editing unstable temporary layers (the operation is blocked).
    *   Exceeding the maximum text field length (254 characters for SHP).

---

## ⚙️ Instalacja / Installation

1.  Pobierz najnowszą wersję wtyczki jako plik `.zip`.
2.  W QGIS, przejdź do menu `Wtyczki` -> `Zarządzaj wtyczkami...`.
3.  W nowym oknie wybierz zakładkę `Zainstaluj z pliku ZIP`.
4.  Wskaż pobrany plik `.zip` i kliknij `Zainstaluj wtyczkę`.
5.  Po instalacji upewnij się, że wtyczka jest włączona na liście `Zainstalowane`.

1.  Download the latest version of the plugin as a `.zip` file.
2.  In QGIS, go to `Plugins` -> `Manage and Install Plugins...`.
3.  In the new window, select the `Install from ZIP` tab.
4.  Point to the downloaded `.zip` file and click `Install Plugin`.
5.  After installation, ensure the plugin is enabled in the `Installed` list.


## 👤 Autor / Author

*   **Michał Baczkiewicz**
*   Email: `michal.baczkiewicz@at.agro.pl`

## Historia zmian
*   **2.0.1** (2025-07-09): Powierzchnia złączonej warstwy aktualizuje się.
*   **2.0.0** (2025-07-04): Zmiana podejścia edycjji, warstwa uruchamia tryb edycji i w nim pozostaje, commit usunięty.
*   **1.9.3** (2025-07-04): Testy, zmiana ścieżki dostępu, poprawka w pliku metadanych.
*   **v1.6.2** (2025-07-02): Aktualizacja opisow, styli oraz poprawienie działania w warstwie tymczasowej.
*   **v1.6** (2025-07-01): Wprowadzono działanie usprawniające edycje, narzędzie działa niezależnie od trybu edycji.
*   **v1.5** (2025-06-30): Poprawiono metodę sprawdzania statusu edycji dla kompatybilności z różnymi wersjami QGIS. Ulepszono obsługę błędów.
*   **v1.4** (2025-06-30): Wprowadzono inteligentne zarządzanie sesją edycyjną.
*   **v1.3** (2025-06-25): Pierwsza stabilna, działająca wersja z walidacją geometrii.

=======
*   **Michał Baczkiewicz** - [m-baczkiewicz](https://m-baczkiewicz.github.io/Portfolio/index.html)

