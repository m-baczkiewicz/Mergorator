# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsFeature, QgsGeometry, QgsMessageLog, Qgis, QgsVectorDataProvider
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
        self.action = QAction(QIcon(icon_path), "Połącz z konkatenacją", self.iface.mainWindow())
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

        selected_count = layer.selectedFeatureCount()
        if selected_count < 2:
            QMessageBox.warning(None, "Błąd", f"Zaznacz co najmniej 2 obiekty. Zaznaczono: {selected_count}.")
            return

        self.log_message(f"Rozpoczęcie łączenia {selected_count} obiektów na warstwie '{layer.name()}'.")
        
        # --- OSTATECZNA I POPRAWNA METODA SPRAWDZANIA EDYCJI ---
        was_editing_before = layer.editBuffer() is not None
        
        try:
            if not was_editing_before:
                self.log_message("Warstwa nie była w trybie edycji. Próba włączenia edycji...")
                if not layer.startEditing():
                    raise Exception("Nie udało się rozpocząć edycji warstwy. Może być tylko do odczytu "
                                    "lub jest zablokowana. Spróbuj zapisać ją do nowego pliku i ponowić operację.")

            features = list(layer.selectedFeatures())
            feature_ids = [f.id() for f in features]

            field_names = [field.name().lower() for field in layer.fields()]
            has_dzialki_field = "nr_dzialki" in field_names
            
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
                    if has_dzialki_field:
                        val = feat.attribute("nr_dzialki")
                        if val:
                            cleaned_values = [v.strip() for v in str(val).replace(" ", "").split(',') if v.strip()]
                            dzialki.update(cleaned_values)
            
            if len(valid_geometries) < 2:
                raise Exception("Niewystarczająca liczba obiektów z prawidłową geometrią do połączenia.")
            
            if not max_feat: max_feat = features[0]

            geom_union = QgsGeometry.unaryUnion(valid_geometries)
            geom_union = self.validate_geometry(geom_union)

            if not geom_union or geom_union.isEmpty():
                raise Exception("Nie udało się utworzyć prawidłowej połączonej geometrii.")

            new_feat = QgsFeature(layer.fields())
            new_feat.setGeometry(geom_union)

            for field in layer.fields():
                name = field.name()
                if name.lower() == "nr_dzialki":
                    new_feat.setAttribute(name, ",".join(sorted(list(dzialki))))
                else:
                    new_feat.setAttribute(name, max_feat.attribute(name))
            
            if not layer.addFeature(new_feat):
                raise Exception("Nie udało się dodać nowego obiektu.")

            if not layer.deleteFeatures(feature_ids):
                raise Exception("Nie udało się usunąć oryginalnych obiektów.")
            
            if not was_editing_before:
                self.log_message("Zatwierdzanie zmian i wyłączanie edycji...")
                if not layer.commitChanges():
                    raise Exception(f"Nie udało się zapisać zmian. Błąd dostawcy danych: {layer.dataProvider().lastError()}")
            else:
                self.log_message("Operacja wykonana w istniejącej sesji edycyjnej.")

            self.iface.messageBar().pushSuccess("Sukces", f"Pomyślnie połączono {selected_count} obiektów.")
            layer.triggerRepaint()

        except Exception as e:
            # W razie błędu, wycofujemy zmiany tylko jeśli to my włączyliśmy edycję
            # Sprawdzamy ponownie, czy bufor istnieje
            is_currently_editing = layer.editBuffer() is not None
            if not was_editing_before and is_currently_editing:
                self.log_message("Wystąpił błąd. Wycofywanie zmian...", Qgis.Critical)
                layer.rollBack()

            error_msg = f"Wystąpił błąd: {str(e)}"
            self.log_message(error_msg, Qgis.Critical)
            self.log_message(traceback.format_exc(), Qgis.Critical)
            QMessageBox.critical(None, "Błąd krytyczny", f"{error_msg}")