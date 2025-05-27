from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QDateEdit, QComboBox,
    QPushButton, QTextEdit, QMessageBox, QFormLayout
)
from PyQt5.QtCore import QDate
import sqlite3


class HayvanEklemeSayfasi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hayvan Ekleme")
        self.setGeometry(150, 150, 500, 750)
        self.setup_database()
        self.init_ui()

    def setup_database(self):
        try:
            self.conn = sqlite3.connect("sheepsense.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS animals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_id TEXT UNIQUE NOT NULL , 
                    gender TEXT,
                    birthdate TEXT,
                    breed TEXT,
                    color TEXT,
                    register_date TEXT,
                    location TEXT,
                    farm_id TEXT,
                    birth_weight REAL,
                    current_weight REAL,
                    vaccines TEXT,
                    diseases TEXT,
                    vet_notes TEXT,
                    mother_tag TEXT,
                    father_tag TEXT,
                    birth_type TEXT,
                    birth_count INTEGER
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Veritabanı Hatası", f"Veritabanı hatası: {e}")

    def init_ui(self):
        self.layout = QFormLayout()

        # Form alanlarını tanımlıyoruz
        self.tag_input = QLineEdit()
        self.gender_input = QComboBox(); self.gender_input.addItems(["Dişi", "Erkek"])
        self.birthdate_input = QDateEdit(calendarPopup=True); self.birthdate_input.setDate(QDate.currentDate())
        self.breed_input = QLineEdit()
        self.color_input = QLineEdit()
        self.register_date_input = QDateEdit(calendarPopup=True); self.register_date_input.setDate(QDate.currentDate())
        self.location_input = QLineEdit()
        self.farm_id_input = QLineEdit()
        self.birth_weight_input = QLineEdit()
        self.current_weight_input = QLineEdit()
        self.vaccines_input = QTextEdit()
        self.diseases_input = QTextEdit()
        self.vet_notes_input = QTextEdit()
        self.mother_tag_input = QLineEdit()
        self.father_tag_input = QLineEdit()
        self.birth_type_input = QComboBox(); self.birth_type_input.addItems(["Normal", "Sezaryen"])
        self.birth_count_input = QLineEdit()

        # Butonlar
        self.save_button = QPushButton("Kaydet"); self.save_button.clicked.connect(self.save_animal)
        self.update_weight_button = QPushButton("Ağırlığı Güncelle"); self.update_weight_button.clicked.connect(self.update_current_weight)
        self.delete_button = QPushButton("Sil"); self.delete_button.clicked.connect(self.delete_animal)

        # Formu yerleştiriyoruz
        fields = [
            ("Küpe Numarası (ID):", self.tag_input),
            ("Cinsiyet:", self.gender_input),
            ("Doğum Tarihi:", self.birthdate_input),
            ("Irk / Cins:", self.breed_input),
            ("Renk / Özellik:", self.color_input),
            ("Kayıt Tarihi:", self.register_date_input),
            ("Lokasyon:", self.location_input),
            ("Çiftlik Numarası:", self.farm_id_input),
            ("Doğum Ağırlığı (kg):", self.birth_weight_input),
            ("Mevcut Ağırlık (kg):", self.current_weight_input),
            ("", self.update_weight_button),
            ("Aşı Geçmişi:", self.vaccines_input),
            ("Geçirilmiş Hastalıklar / Tedavi:", self.diseases_input),
            ("Veteriner Notları:", self.vet_notes_input),
            ("Anne Küpe No:", self.mother_tag_input),
            ("Baba Küpe No:", self.father_tag_input),
            ("Doğum Yöntemi:", self.birth_type_input),
            ("Doğum Sayısı:", self.birth_count_input),
            ("", self.save_button),
            ("", self.delete_button)
        ]

        for label, widget in fields:
            self.layout.addRow(label, widget)

        self.setLayout(self.layout)

    def save_animal(self):
        if not self.tag_input.text():   #bu yoruma alınmış 3 satır küpe numarasını boş bırakmaya yarıyor.
            QMessageBox.warning(self, "Hata", "Küpe Numarası boş olamaz!")
            return

        try:
            self.cursor.execute('''
                INSERT INTO animals (
                    tag_id, gender, birthdate, breed, color, register_date, location, farm_id,
                    birth_weight, current_weight, vaccines, diseases, vet_notes,
                    mother_tag, father_tag, birth_type, birth_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.tag_input.text(),
                self.gender_input.currentText() or None,
                self.birthdate_input.date().toString("yyyy-MM-dd"),
                self.breed_input.text() or None,
                self.color_input.text() or None,
                self.register_date_input.date().toString("yyyy-MM-dd"),
                self.location_input.text() or None,
                self.farm_id_input.text() or None,
                float(self.birth_weight_input.text()) if self.birth_weight_input.text() else None,
                float(self.current_weight_input.text()) if self.current_weight_input.text() else None,
                self.vaccines_input.toPlainText() or None,
                self.diseases_input.toPlainText() or None,
                self.vet_notes_input.toPlainText() or None,
                self.mother_tag_input.text() or None,
                self.father_tag_input.text() or None,
                self.birth_type_input.currentText() or None,
                int(self.birth_count_input.text()) if self.birth_count_input.text() else None
            ))
            self.conn.commit()
            QMessageBox.information(self, "Başarılı", "Hayvan kaydedildi!")
            self.clear_form()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Hata", "Bu küpe numarası zaten kayıtlı!")
        except ValueError:
            QMessageBox.warning(self, "Hata", "Sayısal alanlar geçerli bir sayı olmalı.")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Veritabanı Hatası", f"Veritabanı hatası: {e}")

    def update_current_weight(self):
        tag_id = self.tag_input.text()
        current_weight = self.current_weight_input.text()

        if not tag_id or not current_weight:
            QMessageBox.warning(self, "Hata", "Küpe Numarası ve Ağırlık alanlarını doldurun.")
            return

        try:
            self.cursor.execute('''
                UPDATE animals SET current_weight = ? WHERE tag_id = ?
            ''', (float(current_weight), tag_id))
            self.conn.commit()
            QMessageBox.information(self, "Başarılı", "Ağırlık güncellendi!")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Hata: {e}")

    def delete_animal(self):
        tag_id = self.tag_input.text()
        if not tag_id:
            QMessageBox.warning(self, "Hata", "Küpe Numarası girin.")
            return

        reply = QMessageBox.question(self, 'Silme Onayı',
                                     f"{tag_id} numaralı hayvanı silmek istiyor musunuz?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                # Hayvanı siliyoruz
                self.cursor.execute("DELETE FROM animals WHERE tag_id = ?", (tag_id,))
                self.conn.commit()

                # Silme işleminden sonra ID sırasını yeniden düzenlemek için
                self.cursor.execute('''
                    UPDATE animals
                    SET id = rowid
                ''')
                self.conn.commit()

                # Sıfırlanan ID'ler ile diğer verileri tekrar kontrol edebiliriz
                QMessageBox.information(self, "Başarılı", "Hayvan silindi!")
                self.clear_form()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Hata", f"Silme hatası: {e}")

    def clear_form(self):
        for widget in self.findChildren((QLineEdit, QTextEdit)):
            widget.clear()
        self.gender_input.setCurrentIndex(0)
        self.birth_type_input.setCurrentIndex(0)
        self.birthdate_input.setDate(QDate.currentDate())
        self.register_date_input.setDate(QDate.currentDate())
