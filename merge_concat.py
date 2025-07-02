# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsFeature, QgsGeometry, QgsMessageLog, Qgis, QgsVectorDataProvider,
    edit 
)
from qgis.utils import iface
import os
import traceback

class MergeConcatPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.action = QAction(QIcon(icon_path), "Połącz z konkatenacją (SHP)", self.iface.mainWindow())
        self.action.triggered.connect(self.merge_selected_with_concat)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&MergeConcat", self.action)

    def unload(self):
        self.iface.removePluginMenu("&MergeConcat", self.action)
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def log_message(self, message, level=Qgis.Info):
        QgsMessageLog.logMessage(message, "MergeConcat", level)

    def validate_geometry(self, geometry):
        if not geometry.isGeosValid():
            self.log_message("Wykryto nieprawidłową geometrię - próba naprawy.", Qgis.Warning)
            return geometry.makeValid()
        return geometry

    def merge_selected_with_concat(self):
        layer = self.iface.activeLayer()
        if not layer or not hasattr(layer, 'selectedFeatureCount'):
            QMessageBox.warning(None, "Błąd", "Wybierz aktywną warstwę wektorową.")
            return

        if layer.isTemporary():
            QMessageBox.critical(
                None, 
                "Operacja zablokowana",
                "Wybrana warstwa ('{}') jest warstwą tymczasową.\n\n"
                "Aby uniknąć błędów i utraty danych, proszę najpierw zapisać ją jako stały plik Shapefile.\n\n"
                "Kliknij prawym przyciskiem na warstwę -> Eksportuj -> Zapisz obiekty jako... i wybierz format 'ESRI Shapefile'.".format(layer.name())
            )
            return

        selected_count = layer.selectedFeatureCount()
        if selected_count < 2:
            QMessageBox.warning(None, "Błąd", f"Zaznacz co najmniej 2 obiekty. Zaznaczono: {selected_count}.")
            return

        self.log_message(f"Rozpoczęcie łączenia {selected_count} obiektów na warstwie '{layer.name()}'.")
        
        try:
            with edit(layer): 
                features = list(layer.selectedFeatures())
                feature_ids = [f.id() for f in features]

                fields = layer.fields()
                dzialki_field_name = None
                dzialki_field_index = -1
                for field in fields:
                    if field.name().lower() == "nr_dzialki":
                        dzialki_field_name = field.name()
                        dzialki_field_index = fields.indexFromName(dzialki_field_name)
                        break

                valid_geometries = []
                dzialki = set()
                max_area = -1
                max_feat = None

                for feat in features:
                    geom = self.validate_geometry(feat.geometry())
                    if geom and not geom.isEmpty():
                        valid_geometries.append(geom)
                        area = geom.area()
                        if area > max_area:
                            max_area = area
                            max_feat = feat
                        if dzialki_field_name:
                            val = feat.attribute(dzialki_field_name)
                            if val:
                                cleaned_values = [v.strip() for v in str(val).replace(" ", "").split(',') if v.strip()]
                                dzialki.update(cleaned_values)
                
                if len(valid_geometries) < 2:
                    raise Exception("Niewystarczająca liczba obiektów z prawidłową geometrią do połączenia.")
                
                if not max_feat: 
                    raise Exception("Nie udało się zidentyfikować obiektu z największą powierzchnią (do skopiowania atrybutów).")

                geom_union = QgsGeometry.unaryUnion(valid_geometries)
                geom_union = self.validate_geometry(geom_union)

                if not geom_union or geom_union.isEmpty():
                    raise Exception("Nie udało się utworzyć prawidłowej połączonej geometrii.")

                new_feat = QgsFeature(fields)
                new_feat.setGeometry(geom_union)

                for i in range(fields.count()):
                    new_feat.setAttribute(i, max_feat.attribute(i))

                if dzialki_field_name:
                    concatenated_dzialki = ",".join(sorted(list(dzialki)))
                    
                    field_def = fields.field(dzialki_field_index)
                    field_len = field_def.length()
                    
                    if field_len > 0 and len(concatenated_dzialki.encode('utf-8')) > field_len:
                        raise Exception(
                            f"WARTOŚĆ ZA DŁUGA DLA POLA SHAPEFILE!\n\n"
                            f"Połączone numery działek ('{concatenated_dzialki[:50]}...') "
                            f"mają {len(concatenated_dzialki)} znaków, a maksymalna dozwolona długość "
                            f"dla pola '{dzialki_field_name}' to {field_len} znaków.\n\n"
                            "Proszę zmniejszyć liczbę zaznaczonych obiektów i spróbować ponownie."
                        )
                    
                    new_feat.setAttribute(dzialki_field_index, concatenated_dzialki)
                
                if not layer.addFeature(new_feat):
                    raise Exception("Błąd dostawcy danych: Nie udało się dodać nowego, połączonego obiektu.")

                if not layer.deleteFeatures(feature_ids):
                    raise Exception("Błąd dostawcy danych: Nie udało się usunąć oryginalnych obiektów.")
            
            self.iface.messageBar().pushSuccess("Sukces", f"Pomyślnie połączono {selected_count} obiektów.")
            layer.triggerRepaint()

        except Exception as e:
            last_provider_error = layer.dataProvider().lastError()
            error_msg = str(e)
            
            is_shapefile = "ESRI Shapefile" in layer.dataProvider().name()
            
            shp_advice = ""
            if is_shapefile:
                shp_advice = (
                    "\n\nPracujesz na pliku Shapefile. Najczęstsze przyczyny błędów zapisu to:\n"
                    "1. BLOKADA PLIKU: Inny program (lub podgląd w Eksploratorze Windows) blokuje jeden z plików (.shp, .shx, .dbf). Zamknij wszystko, co może używać tego pliku.\n"
                    "2. UPRAWNIENIA: Brak uprawnień do zapisu w folderze, gdzie znajduje się plik.\n"
                    "3. ŚCIEŻKA SIECIOWA: Chwilowe problemy z połączeniem do dysku sieciowego."
                )

            full_error_message = (
                f"Wystąpił krytyczny błąd: {error_msg}\n"
                f"{shp_advice}\n\n"
                f"Szczegóły techniczne:\n"
                f"Błąd dostawcy danych: {last_provider_error or '(brak szczegółów)'}\n"
                f"Źródło danych: {layer.source()}"
            )

            self.log_message(full_error_message, Qgis.Critical)
            self.log_message(traceback.format_exc(), Qgis.Critical)
            QMessageBox.critical(None, "Błąd krytyczny", full_error_message)