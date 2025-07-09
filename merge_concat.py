# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsFeature, QgsGeometry, QgsMessageLog, Qgis,
    QgsDistanceArea,
    QgsProject
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
        
        is_already_in_edit_mode = layer.isEditable()
        
        if not is_already_in_edit_mode:
            self.log_message("Warstwa nie była w trybie edycji. Włączanie edycji...")
            if not layer.startEditing():
                error_msg = "Nie udało się rozpocząć edycji warstwy. Może być tylko do odczytu lub jest zablokowana."
                QMessageBox.critical(None, "Błąd krytyczny", error_msg)
                self.log_message(error_msg, Qgis.Critical)
                return

        try:
            features = list(layer.selectedFeatures())
            feature_ids = [f.id() for f in features]
            fields = layer.fields()
            
            dzialki_field_name = None
            area_field_name = None 
            possible_area_fields = ["powierzchnia", "pole", "area", "pow"]

            for field in fields:
                field_name_lower = field.name().lower()
                if field_name_lower == "nr_dzialki":
                    dzialki_field_name = field.name()
                elif field_name_lower in possible_area_fields:
                    area_field_name = field.name()
            
            valid_geometries, dzialki = [], set()
            max_area_feature_size, max_feat = -1, None

            for feat in features:
                geom = self.validate_geometry(feat.geometry())
                if geom and not geom.isEmpty():
                    valid_geometries.append(geom)
                    current_feat_area = feat.geometry().area()
                    if current_feat_area > max_area_feature_size:
                        max_area_feature_size = current_feat_area
                        max_feat = feat
                    if dzialki_field_name:
                        val = feat.attribute(dzialki_field_name)
                        if val:
                            cleaned_values = [v.strip() for v in str(val).replace(" ", "").split(',') if v.strip()]
                            dzialki.update(cleaned_values)
            
            if len(valid_geometries) < 2: raise Exception("Niewystarczająca liczba obiektów z prawidłową geometrią.")
            if not max_feat: raise Exception("Nie udało się zidentyfikować obiektu bazowego.")

            geom_union = self.validate_geometry(QgsGeometry.unaryUnion(valid_geometries))
            if not geom_union or geom_union.isEmpty(): raise Exception("Nie udało się utworzyć połączonej geometrii.")

            new_feat = QgsFeature(fields)
            new_feat.setGeometry(geom_union)
            
            for i in range(fields.count()):
                new_feat.setAttribute(i, max_feat.attribute(i))

            if dzialki_field_name:
                new_feat.setAttribute(dzialki_field_name, ",".join(sorted(list(dzialki))))
            
            if area_field_name:
                d = QgsDistanceArea()
                d.setEllipsoid(QgsProject.instance().ellipsoid())
                
                new_area_sq_meters = d.measureArea(geom_union)
                new_area_hectares = new_area_sq_meters / 10000.0
                
                rounded_area = round(new_area_hectares, 2)
                
                new_feat.setAttribute(area_field_name, rounded_area)
                
                self.log_message(f"Obliczono {new_area_sq_meters:.2f} m2, zaokrąglono i zapisano jako {rounded_area:.2f} ha w polu '{area_field_name}'")
            else:
                self.log_message("Nie znaleziono pola powierzchni ('powierzchnia', 'area' etc.) do aktualizacji.", Qgis.Warning)
            
            if not layer.addFeature(new_feat): raise Exception("Błąd dostawcy: Nie udało się dodać nowego obiektu.")
            if not layer.deleteFeatures(feature_ids): raise Exception("Błąd dostawcy: Nie udało się usunąć starych obiektów.")
            
            self.log_message("Operacja łączenia zakończona pomyślnie wewnątrz sesji edycyjnej.")
            
            if not is_already_in_edit_mode:
                self.iface.messageBar().pushInfo("Sukces", f"Połączono obiekty. Zapisz zmiany w warstwie.")
            
            layer.triggerRepaint()
            self.iface.mapCanvas().refresh()

        except Exception as e:
            self.log_message(f"Wystąpił błąd: {e}", Qgis.Critical)
            self.log_message(traceback.format_exc(), Qgis.Critical)
            
            if not is_already_in_edit_mode:
                self.log_message("Wycofuję zmiany i wyłączam tryb edycji...", Qgis.Warning)
                layer.rollBack()
            
            QMessageBox.critical(None, "Błąd krytyczny", f"Wystąpił błąd i operacja została przerwana:\n\n{e}")