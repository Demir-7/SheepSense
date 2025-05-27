import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit
)
from PyQt5.QtCore import QDate


class AgirlikTakibiSayfasi(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect("sheepsense.db")
        self.cursor = self.conn.cursor()
        self.setWindowTitle("Ağırlık Takip Sayfası")
        self.setGeometry(100, 100, 700, 500)
        self.tablo_olustur()  # Tabloyu oluştur
        self.arayuz_olustur()

    def tablo_olustur(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS agirlik_bilgileri (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_id TEXT NOT NULL,
                    farm_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    weight REAL NOT NULL
                )
            """)
            self.conn.commit()
            print("Tablo başarıyla oluşturuldu veya zaten var.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Veritabanı Hatası", f"Veritabanı hatası: {e}")

    def arayuz_olustur(self):
        # === Kayıt Bölümü ===
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Küpe Numarası")

        self.farm_input = QLineEdit()
        self.farm_input.setPlaceholderText("Çiftlik Numarası")

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.kilo_input = QDoubleSpinBox()
        self.kilo_input.setRange(0.0, 500.0)
        self.kilo_input.setSingleStep(0.1)
        self.kilo_input.setSuffix(" kg")

        kaydet_btn = QPushButton("Kaydet")
        kaydet_btn.clicked.connect(self.agirlik_verisi_kaydet)

        kayit_layout = QHBoxLayout()
        kayit_layout.addWidget(self.tag_input)
        kayit_layout.addWidget(self.farm_input)
        kayit_layout.addWidget(self.date_input)
        kayit_layout.addWidget(self.kilo_input)
        kayit_layout.addWidget(kaydet_btn)

        # === Arama ve Listeleme Bölümü ===
        self.arama_tag_input = QLineEdit()
        self.arama_tag_input.setPlaceholderText("Ara: Küpe No")

        self.arama_farm_input = QLineEdit()
        self.arama_farm_input.setPlaceholderText("Ara: Çiftlik No")

        ara_btn = QPushButton("Listele")
        ara_btn.clicked.connect(self.verileri_yukle)

        arama_layout = QHBoxLayout()
        arama_layout.addWidget(self.arama_tag_input)
        arama_layout.addWidget(self.arama_farm_input)
        arama_layout.addWidget(ara_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Küpe No", "Çiftlik No", "Tarih", "Ağırlık", "Sil"])

        # === Genel Sayfa Düzeni ===
        main_layout = QVBoxLayout()
        main_layout.addLayout(kayit_layout)
        main_layout.addLayout(arama_layout)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    def agirlik_verisi_kaydet(self):
        tag_id = self.tag_input.text().strip()
        farm_id = self.farm_input.text().strip()
        tarih = self.date_input.date().toString("yyyy-MM-dd")
        kilo = self.kilo_input.value()

        if not tag_id and not farm_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen küpe numarası veya çiftlik numarası girin.")
            return

        # Sadece tag_id varsa çiftlik no'yu çek
        if tag_id and not farm_id:
            self.cursor.execute("SELECT farm_id FROM animals WHERE tag_id = ?", (tag_id,))
            result = self.cursor.fetchone()
            if not result:
                QMessageBox.warning(self, "Uyarı", "Bu küpe numarasına ait hayvan bulunamadı.")
                return
            farm_id = result[0]

        # Sadece farm_id varsa tag_id'yi çek
        if farm_id and not tag_id:
            self.cursor.execute("SELECT tag_id FROM animals WHERE farm_id = ?", (farm_id,))
            result = self.cursor.fetchone()
            if not result:
                QMessageBox.warning(self, "Uyarı", "Bu çiftlik numarasına ait hayvan bulunamadı.")
                return
            tag_id = result[0]

        if kilo <= 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir kilo girin.")
            return

        self.cursor.execute("""
            INSERT INTO agirlik_bilgileri (tag_id, farm_id, date, weight)
            VALUES (?, ?, ?, ?)
        """, (tag_id, farm_id, tarih, kilo))
        self.conn.commit()

        QMessageBox.information(self, "Başarılı", "Ağırlık bilgisi kaydedildi.")
        self.tag_input.clear()
        self.farm_input.clear()
        self.kilo_input.setValue(0.0)
        self.verileri_yukle()

    def verileri_yukle(self):
        tag = self.arama_tag_input.text().strip()
        farm = self.arama_farm_input.text().strip()

        query = "SELECT id, tag_id, farm_id, date, weight FROM agirlik_bilgileri"
        params = []

        if tag:
            query += " WHERE tag_id = ?"
            params.append(tag)
        elif farm:
            query += " WHERE farm_id = ?"
            params.append(farm)

        query += " ORDER BY date DESC"

        self.table.setRowCount(0)
        self.cursor.execute(query, params)
        for row_num, row in enumerate(self.cursor.fetchall()):
            id_, tag_id, farm_id, tarih, kilo = row
            self.table.insertRow(row_num)
            self.table.setItem(row_num, 0, QTableWidgetItem(tag_id))
            self.table.setItem(row_num, 1, QTableWidgetItem(farm_id))
            self.table.setItem(row_num, 2, QTableWidgetItem(tarih))
            self.table.setItem(row_num, 3, QTableWidgetItem(f"{kilo:.2f} kg"))

            sil_btn = QPushButton("Sil")
            sil_btn.setStyleSheet("background-color: red; color: white;")
            sil_btn.clicked.connect(lambda _, rid=id_: self.kayit_sil(rid))
            self.table.setCellWidget(row_num, 4, sil_btn)

    def kayit_sil(self, row_id):
        cevap = QMessageBox.question(self, "Silme Onayı", "Bu kaydı silmek istediğinize emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM agirlik_bilgileri WHERE id = ?", (row_id,))
            self.conn.commit()
            self.verileri_yukle()
