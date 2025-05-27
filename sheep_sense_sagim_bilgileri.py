from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QDoubleSpinBox
)
from PyQt5.QtCore import QDate
import sqlite3
import sys

class SutimBilgileriSayfasi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sağım Bilgileri")
        self.setGeometry(100, 100, 900, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.veritabani_baglantisi()
        self.sagim_tablosu_olustur()

        form_layout = QHBoxLayout()

        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Küpe Numarası")

        self.farm_input = QLineEdit()
        self.farm_input.setPlaceholderText("Çiftlik Numarası")

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)

        self.sut_miktari_input = QDoubleSpinBox()
        self.sut_miktari_input.setRange(0.0, 50.0)
        self.sut_miktari_input.setDecimals(2)
        self.sut_miktari_input.setSuffix(" L")

        self.kaydet_btn = QPushButton("Kaydet")
        self.kaydet_btn.clicked.connect(self.sagim_verisi_kaydet)

        form_layout.addWidget(QLabel("Küpe No:"))
        form_layout.addWidget(self.tag_input)
        form_layout.addWidget(QLabel("Çiftlik No:"))
        form_layout.addWidget(self.farm_input)
        form_layout.addWidget(QLabel("Tarih:"))
        form_layout.addWidget(self.date_input)
        form_layout.addWidget(QLabel("Süt Miktarı:"))
        form_layout.addWidget(self.sut_miktari_input)
        form_layout.addWidget(self.kaydet_btn)

        self.layout.addLayout(form_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Küpe No", "Çiftlik No", "Tarih", "Süt Miktarı (L)", "Sil"])
        self.layout.addWidget(self.table)

        self.verileri_yukle()

    def veritabani_baglantisi(self):
        self.conn = sqlite3.connect("milk.db")
        self.cursor = self.conn.cursor()

    def sagim_tablosu_olustur(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sagim_bilgileri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_id TEXT,
                farm_id TEXT,
                date TEXT,
                milk_amount REAL
            )
        """)
        self.conn.commit()

    def bir_yas_ustu_hayvanlar(self):
        try:
            conn_hayvanlar = sqlite3.connect("sheepsense.db")
            cursor = conn_hayvanlar.cursor()
            cursor.execute("SELECT tag_id, farm_id, birthdate FROM animals")
            bugun = QDate.currentDate()
            uygunlar = {}

            for tag_id, farm_id, birthdate_str in cursor.fetchall():
                dogum_tarihi = QDate.fromString(birthdate_str, "yyyy-MM-dd")
                yas_gun = dogum_tarihi.daysTo(bugun)
                if yas_gun >= 365:
                    uygunlar[tag_id] = farm_id

            conn_hayvanlar.close()
            return uygunlar
        except Exception as e:
            print("Hata:", e)
            return {}

    def sagim_verisi_kaydet(self):
        tag_id = self.tag_input.text().strip()
        farm_id = self.farm_input.text().strip()
        tarih = self.date_input.date().toString("yyyy-MM-dd")
        miktar = self.sut_miktari_input.value()

        uygun_hayvanlar = self.bir_yas_ustu_hayvanlar()

        if not tag_id and not farm_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen küpe numarası veya çiftlik numarası girin.")
            return

        # Eksik olan değeri otomatik tamamla
        if tag_id and not farm_id:
            farm_id = uygun_hayvanlar.get(tag_id)
        elif farm_id and not tag_id:
            for k, v in uygun_hayvanlar.items():
                if v == farm_id:
                    tag_id = k
                    break

        if not tag_id or tag_id not in uygun_hayvanlar:
            QMessageBox.warning(self, "Uyarı", "Bu hayvan 1 yaşından küçük ya da veritabanında bulunamadı.")
            return

        if miktar <= 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir süt miktarı girin.")
            return

        self.cursor.execute("""
            INSERT INTO sagim_bilgileri (tag_id, farm_id, date, milk_amount)
            VALUES (?, ?, ?, ?)
        """, (tag_id, farm_id, tarih, miktar))
        self.conn.commit()

        QMessageBox.information(self, "Başarılı", "Sağım bilgisi kaydedildi.")
        self.tag_input.clear()
        self.farm_input.clear()
        self.sut_miktari_input.setValue(0.0)
        self.verileri_yukle()

    def verileri_yukle(self):
        try:
            self.table.setRowCount(0)
            self.cursor.execute("SELECT id, tag_id, farm_id, date, milk_amount FROM sagim_bilgileri ORDER BY date DESC")
            for row_number, row_data in enumerate(self.cursor.fetchall()):
                id_, tag_id, farm_id, tarih, miktar = row_data
                self.table.insertRow(row_number)
                self.table.setItem(row_number, 0, QTableWidgetItem(tag_id))
                self.table.setItem(row_number, 1, QTableWidgetItem(farm_id))
                self.table.setItem(row_number, 2, QTableWidgetItem(tarih))
                self.table.setItem(row_number, 3, QTableWidgetItem(f"{miktar:.2f} L"))

                sil_btn = QPushButton("Sil")
                sil_btn.setStyleSheet("background-color: red; color: white;border-radius: 5px; padding:5px;")
                sil_btn.clicked.connect(lambda checked, row_id=id_: self.kayit_sil(row_id))
                self.table.setCellWidget(row_number, 4, sil_btn)
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Veriler yüklenirken bir hata oluştu: {e}")

    def kayit_sil(self, row_id):
        cevap = QMessageBox.question(self, "Silme Onayı", "Bu kaydı silmek istediğinize emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM sagim_bilgileri WHERE id = ?", (row_id,))
            self.conn.commit()
            self.verileri_yukle()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SutimBilgileriSayfasi()
    window.show()
    sys.exit(app.exec_())
