from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QPushButton, QDialog, QFormLayout, QMessageBox
)
from PyQt5.QtCore import Qt
import sqlite3
from datetime import datetime


class KayitliHayvanlarSayfasi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kayıtlı Hayvanlar")
        self.setGeometry(150, 150, 1300, 700)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        filter_layout = QHBoxLayout()

        # Filtre Alanları
        self.tag_filter_input = QLineEdit(placeholderText="Küpe Numarasına Göre Ara")
        self.gender_filter_input = QComboBox()
        self.gender_filter_input.addItems(["Tüm Cinsiyetler", "Dişi", "Erkek"])
        self.birthdate_filter_input = QLineEdit(placeholderText="Doğum Tarihine Göre Ara")
        self.min_age_filter_input = QLineEdit(placeholderText="Min Yaş (Yıl)")
        self.max_age_filter_input = QLineEdit(placeholderText="Max Yaş (Yıl)")
        self.breed_filter_input = QLineEdit(placeholderText="Irk Adına Göre Ara")
        self.min_weight_filter_input = QLineEdit(placeholderText="Min Ağırlık")
        self.max_weight_filter_input = QLineEdit(placeholderText="Max Ağırlık")
        self.registration_filter_input = QLineEdit(placeholderText="Kayıt Tarihine Göre Ara")
        self.vaccines_filter_input = QLineEdit(placeholderText="Aşı Geçmişine Göre Ara")
        self.diseases_filter_input = QLineEdit(placeholderText="Geçirilmiş Hastalıklara Göre Ara")
        self.vet_notes_filter_input = QLineEdit(placeholderText="Veteriner Notlarına Göre Ara")

        filter_widgets = [
            self.tag_filter_input, self.gender_filter_input, self.birthdate_filter_input,
            self.min_age_filter_input, self.max_age_filter_input, self.breed_filter_input,
            self.min_weight_filter_input, self.max_weight_filter_input, self.registration_filter_input,
            self.vaccines_filter_input, self.diseases_filter_input, self.vet_notes_filter_input
        ]

        for widget in filter_widgets:
            filter_layout.addWidget(widget)
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.filter_animals)
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self.filter_animals)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(18)  # 16 veri + 2 düzenle/sil
        self.table.setHorizontalHeaderLabels([
            "Küpe No", "Cinsiyet", "Doğum Tarihi", "Yaş", "Irk", "Renk",
            "Doğum Ağırlığı", "Mevcut Ağırlık", "Kayıt Tarihi",
            "Lokasyon", "Çiftlik No", "Anne Küpe", "Baba Küpe",
            "Aşı Geçmişi", "Geçirilmiş Hastalıklar", "Veteriner Notları",
            "Düzenle", "Sil"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_animals()

    def calculate_age(self, birthdate_str):
        """'YYYY-MM-DD' formatındaki doğum tarihinden yaş hesaplar."""
        try:
            birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
            today = datetime.today()
            years = today.year - birthdate.year
            months = today.month - birthdate.month
            days = today.day - birthdate.day

            if days < 0:
                months -= 1
                previous_month = (today.month - 1) if today.month > 1 else 12
                previous_year = today.year if today.month > 1 else today.year - 1
                days_in_previous_month = (datetime(previous_year,previous_month + 1 ,1 ) - datetime(previous_year,previous_month,1)).days
                days += days_in_previous_month

            if months < 0:
                years -= 1
                months += 12
            return years,months,days
        except Exception:
            return None

    def load_animals(self):
        """Tüm kayıtlı hayvanları getirir ve tabloya yükler."""
        try:
            conn = sqlite3.connect("sheepsense.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tag_id, gender, birthdate, breed, color,
                       birth_weight, current_weight, register_date,
                       location, farm_id, mother_tag, father_tag,
                       vaccines, diseases, vet_notes
                FROM animals
            """)
            animals = cursor.fetchall()

            self.table.setRowCount(len(animals))
            for row_idx, animal in enumerate(animals):
                for col_idx, value in enumerate(animal):
                    if col_idx == 2:  # Doğum tarihi
                        self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
                        age = self.calculate_age(str(value))
                        if age is not None:
                            years, months, days = age
                            age_text = f"{years} yıl {months} ay {days} gün"
                        else:
                            age_text = "Bilinmiyor"
                        self.table.setItem(row_idx, 3, QTableWidgetItem(age_text))

                    elif col_idx >= 3:
                        self.table.setItem(row_idx, col_idx + 1, QTableWidgetItem(str(value)))
                    else:
                        self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

                # Düzenle ve Sil butonlarını ekle
                edit_button = QPushButton("Düzenle")
                delete_button = QPushButton("Sil")
                delete_button.setStyleSheet("background-color:red;color:white; font-weight:bold;")
                edit_button.clicked.connect(lambda _, row=row_idx: self.edit_animal(row))
                delete_button.clicked.connect(lambda _, row=row_idx: self.delete_animal(row))

                self.table.setCellWidget(row_idx, 16, edit_button)
                self.table.setCellWidget(row_idx, 17, delete_button)

        except sqlite3.Error as e:
            print(f"Veritabanı hatası: {e}")
        finally:
            conn.close()

    def filter_animals(self):
        """Filtrelere göre tabloyu günceller."""
        filters = {
            "tag_id": self.tag_filter_input.text(),
            "gender": self.gender_filter_input.currentText(),
            "birthdate": self.birthdate_filter_input.text(),
            "breed": self.breed_filter_input.text(),
            "min_weight": self.min_weight_filter_input.text(),
            "max_weight": self.max_weight_filter_input.text(),
            "register_date": self.registration_filter_input.text(),
            "vaccines": self.vaccines_filter_input.text(),
            "diseases": self.diseases_filter_input.text(),
            "vet_notes": self.vet_notes_filter_input.text(),
            "min_age":self.min_age_filter_input.text(),
            "max_age":self.max_age_filter_input.text(),
        }

        query = """
            SELECT tag_id, gender, birthdate, breed, color,
                   birth_weight, current_weight, register_date,
                   location, farm_id, mother_tag, father_tag,
                   vaccines, diseases, vet_notes
            FROM animals
            WHERE 1=1
        """
        params = []

        if filters["tag_id"]:
            query += " AND tag_id LIKE ?"
            params.append(f"%{filters['tag_id']}%")
        if filters["gender"] != "Tüm Cinsiyetler":
            query += " AND gender = ?"
            params.append(filters["gender"])
        if filters["birthdate"]:
            query += " AND birthdate LIKE ?"
            params.append(f"%{filters['birthdate']}%")
        if filters["breed"]:
            query += " AND breed LIKE ?"
            params.append(f"%{filters['breed']}%")
        if filters["min_weight"]:
            try:
                min_weight = float(filters["min_weight"])
                query += " AND current_weight >= ?"
                params.append(min_weight)
            except ValueError:
                pass
        if filters["max_weight"]:
            try:
                max_weight = float(filters["max_weight"])
                query += " AND current_weight <= ?"
                params.append(max_weight)
            except ValueError:
                pass
        if filters["register_date"]:
            query += " AND register_date LIKE ?"
            params.append(f"%{filters['register_date']}%")
        if filters["vaccines"]:
            query += " AND vaccines LIKE ?"
            params.append(f"%{filters['vaccines']}%")
        if filters["diseases"]:
            query += " AND diseases LIKE ?"
            params.append(f"%{filters['diseases']}%")
        if filters["vet_notes"]:
            query += " AND vet_notes LIKE ?"
            params.append(f"%{filters['vet_notes']}%")
        if filters["min_age"]:
            try:
                min_age = int(filters["min_age"])
                query += " AND (strftime('%Y','now') - strftime('%Y', birthdate)) >= ? "
                params.append(min_age)
            except ValueError:
                pass  # Hata durumunda sadece geçiyoruz

        if filters["max_age"]:
            try:
                max_age = int(filters["max_age"])
                query += " AND (strftime('%Y','now') - strftime('%Y', birthdate)) <= ? "
                params.append(max_age)
            except ValueError:
                pass  # Hata durumunda sadece geçiyoruz

        try:
            conn = sqlite3.connect("sheepsense.db")
            cursor = conn.cursor()
            cursor.execute(query, params)
            animals = cursor.fetchall()

            self.table.setRowCount(len(animals))
            for row_idx, animal in enumerate(animals):
                for col_idx, value in enumerate(animal):
                    if col_idx == 2:
                        self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
                        age = self.calculate_age(str(value))
                        if age is not None:
                            years, months, days = age
                            age_text = f"{years} yıl {months} ay {days} gün"
                        else:
                            age_text = "Bilinmiyor"
                        self.table.setItem(row_idx, 3, QTableWidgetItem(age_text))

                    elif col_idx >= 3:
                        self.table.setItem(row_idx, col_idx + 1, QTableWidgetItem(str(value)))
                    else:
                        self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

                edit_button = QPushButton("Düzenle")
                delete_button = QPushButton("Sil")
                edit_button.clicked.connect(lambda _, row=row_idx: self.edit_animal(row))
                delete_button.clicked.connect(lambda _, row=row_idx: self.delete_animal(row))

                self.table.setCellWidget(row_idx, 16, edit_button)
                self.table.setCellWidget(row_idx, 17, delete_button)

        except sqlite3.Error as e:
            print(f"Veritabanı hatası: {e}")
        finally:
            conn.close()

    def edit_animal(self, row):
        tag_id = self.table.item(row, 0).text()
        animal_dialog = AnimalEditDialog(tag_id)
        if animal_dialog.exec_():
            self.load_animals()

    def delete_animal(self, row):
        tag_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, 'Silme Onayı',
                                     f"Hayvan {tag_id} kaydını silmek istediğinizden emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("sheepsense.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM animals WHERE tag_id = ?", (tag_id,))
                conn.commit()
                QMessageBox.information(self, "Başarılı", "Kayıt silindi.")
                self.load_animals()
            except sqlite3.Error as e:
                print(f"Silme hatası: {e}")
            finally:
                conn.close()


class AnimalEditDialog(QDialog):
    def __init__(self, tag_id):
        super().__init__()
        self.setWindowTitle("Hayvan Düzenle")
        self.setGeometry(200, 200, 400, 300)
        self.tag_id = tag_id
        self.setup_ui()
        self.load_animal_data()

    def setup_ui(self):
        layout = QFormLayout()
        self.tag_id_input =QLineEdit()  # eklenen1
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Dişi", "Erkek"])
        self.birthdate_input = QLineEdit()
        self.breed_input = QLineEdit()
        self.color_input = QLineEdit()
        self.birth_weight_input = QLineEdit()
        self.current_weight_input = QLineEdit()
        self.register_date_input = QLineEdit()
        self.location_input = QLineEdit()
        self.farm_id_input = QLineEdit()
        self.mother_tag_input = QLineEdit()
        self.father_tag_input = QLineEdit()
        self.vaccines_input = QLineEdit()
        self.diseases_input = QLineEdit()
        self.vet_notes_input = QLineEdit()


        layout.insertRow(0,"Yeni Küpe Numarası",self.tag_id_input)
        layout.addRow("Cinsiyet:", self.gender_input)
        layout.addRow("Doğum Tarihi:", self.birthdate_input)
        layout.addRow("Irk:", self.breed_input)
        layout.addRow("Renk:", self.color_input)
        layout.addRow("Doğum Ağırlığı:", self.birth_weight_input)
        layout.addRow("Mevcut Ağırlık:", self.current_weight_input)
        layout.addRow("Kayıt Tarihi:", self.register_date_input)
        layout.addRow("Lokasyon:", self.location_input)
        layout.addRow("Çiftlik No:", self.farm_id_input)
        layout.addRow("Anne Küpe:", self.mother_tag_input)
        layout.addRow("Baba Küpe:", self.father_tag_input)
        layout.addRow("Aşı Geçmişi:",self.vaccines_input)
        layout.addRow("Geçirilmiş Hastalıklar:",self.diseases_input)
        layout.addRow("Veteriner Notları:",self.vet_notes_input)

        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_changes)

        layout.addRow(self.save_button)
        self.setLayout(layout)

    def load_animal_data(self):
        try:
            conn = sqlite3.connect("sheepsense.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT gender, birthdate, breed, color, birth_weight, current_weight,
                       register_date, location, farm_id, mother_tag, father_tag,
                       vaccines, diseases , vet_notes
                FROM animals
                WHERE tag_id = ?
            """, (self.tag_id,))
            animal = cursor.fetchone()

            if animal:
                self.tag_id_input.setText(self.tag_id)
                self.gender_input.setCurrentText(animal[0])
                self.birthdate_input.setText(animal[1])
                self.breed_input.setText(animal[2])
                self.color_input.setText(animal[3])
                self.birth_weight_input.setText(str(animal[4]))
                self.current_weight_input.setText(str(animal[5]))
                self.register_date_input.setText(animal[6])
                self.location_input.setText(animal[7])
                self.farm_id_input.setText(animal[8])
                self.mother_tag_input.setText(animal[9])
                self.father_tag_input.setText(animal[10])
                self.vaccines_input.setText(animal[11] or "")
                self.diseases_input.setText(animal[12] or "")
                self.vet_notes_input.setText(animal[13] or "")

        except sqlite3.Error as e:
            print(f"Veri yükleme hatası: {e}")
        finally:
            conn.close()

    def save_changes(self):
        try:
            conn = sqlite3.connect("sheepsense.db")
            cursor = conn.cursor()
            new_tag_id = self.tag_id_input.text()
            cursor.execute("""
                UPDATE animals
                SET tag_id = ? ,gender = ?, birthdate = ?, breed = ?, color = ?, birth_weight = ?, current_weight = ?,
                    register_date = ?, location = ?, farm_id = ?, mother_tag = ?, father_tag = ?,
                    vaccines = ?, diseases = ?, vet_notes =? 
                    
                WHERE tag_id = ?
            """, (
                new_tag_id,self.gender_input.currentText(), self.birthdate_input.text(), self.breed_input.text(),
                self.color_input.text(), self.birth_weight_input.text(), self.current_weight_input.text(),
                self.register_date_input.text(), self.location_input.text(), self.farm_id_input.text(),
                self.mother_tag_input.text(), self.father_tag_input.text(), self.vaccines_input.text(),
                self.diseases_input.text(),self.vet_notes_input.text(),
                self.tag_id
            ))

            conn.commit()
            QMessageBox.information(self, "Başarılı", "Hayvan bilgileri güncellendi.")
            self.accept()
        except sqlite3.Error as e:
            print(f"Güncelleme hatası: {e}")
        finally:
            conn.close()

