from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPalette, QColor, QPixmap, QIcon
from PyQt5.QtCore import Qt
from sheep_sense_hayvan_ekleme import HayvanEklemeSayfasi
from sheep_sense_kayitli_hayvanlar import KayitliHayvanlarSayfasi
from sheep_sense_sagim_bilgileri import  SutimBilgileriSayfasi
from sheep_sense_yem_tuketimi import YemAyarlama
from sheep_sense_agirlik_takibi import AgirlikTakibiSayfasi
class ModernMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SheepSense - Ana Menü")
        self.setGeometry(100, 100, 600, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Arka Plan Resmi
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(QPalette.Background, QColor(255, 255, 255))  # Beyaz arka plan
        self.setPalette(p)

        # Arka Plan Fotoğrafı
        pixmap = QPixmap("arkaplansizicon/background_image.jpg")  # Resmi eklemeyi unutmayın!
        background_label = QLabel(self)
        background_label.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio))
        layout.addWidget(background_label)

        # Menü Butonları
        self.animal_button = QPushButton("Hayvan Ekleme")
        self.animal_button.setIcon(QIcon("arkaplansizicon/add.png"))  # İkonu ekliyoruz
        self.animal_button.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 15px;
        """)
        self.animal_button.clicked.connect(self.show_animal_page)

        self.animals_button = QPushButton("Kayıtlı Hayvanlar")
        self.animals_button.setIcon(QIcon("arkaplansizicon/animal.png"))
        self.animals_button.setStyleSheet("""
            background-color: #2196F3;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 15px;
        """)
        self.animals_button.clicked.connect(self.show_animals_page)

        self.milk_button = QPushButton("Sağım Bilgileri")
        self.milk_button.setIcon(QIcon("arkaplansizicon/milking.png"))
        self.milk_button.setStyleSheet("""
            background-color: #FF9800;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 15px;
        """)
        self.milk_button.clicked.connect(self.show_milk_page)

        self.feed_button = QPushButton("Yem Ayarlama ve Yem Tüketimi")
        self.feed_button.setIcon(QIcon("arkaplansizicon/calc.png"))
        self.feed_button.setStyleSheet("""
            background-color: #9C27B0;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 15px;
        """)
        self.feed_button.clicked.connect(self.show_feed_page)

        self.weight_button = QPushButton("Ağırlık Takibi")
        self.weight_button.setIcon(QIcon("arkaplansizicon/weight.png"))
        self.weight_button.setStyleSheet("""
            background-color: #FF5722;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 15px;
        """)
        self.weight_button.clicked.connect(self.show_weight_page)

        self.health_button = QPushButton("Aşı ve Sağlık Kayıtları")
        self.health_button.setIcon(QIcon("arkaplansizicon/asi.png"))
        self.health_button.setStyleSheet("""
            background-color: #673AB7;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 15px;
        """)
        self.health_button.clicked.connect(self.show_health_page)

        self.backup_button = QPushButton("Veri Yedekleme ve Raporlama")
        self.backup_button.setIcon(QIcon("arkaplansizicon/data.png"))
        self.backup_button.setStyleSheet("""
            background-color: #009688;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 15px;
        """)
        self.backup_button.clicked.connect(self.show_backup_page)

        self.notifications_button = QPushButton("Bildirimler")
        self.notifications_button.setIcon(QIcon("arkaplansizicon/bildirim.png"))
        self.notifications_button.setStyleSheet("""
            background-color: #607D8B;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 15px;
        """)
        self.notifications_button.clicked.connect(self.show_notifications_page)

        # Butonları Layout'a ekleme
        layout.addWidget(self.animal_button)
        layout.addWidget(self.animals_button)
        layout.addWidget(self.milk_button)
        layout.addWidget(self.feed_button)
        layout.addWidget(self.weight_button)
        layout.addWidget(self.health_button)
        layout.addWidget(self.backup_button)
        layout.addWidget(self.notifications_button)

        self.setLayout(layout)

    # Her buton için yönlendirme metotları
    def show_animal_page(self):
        self.hayvan_sayfasi = HayvanEklemeSayfasi()
        self.hayvan_sayfasi.show()
        print("Hayvan Ekleme sayfasına gidildi.")

    def show_animals_page(self):
        self.kayitli_hayvanlar_sayfasi = KayitliHayvanlarSayfasi()
        self.kayitli_hayvanlar_sayfasi.show()
        print("Kayıtlı Hayvanlar sayfasına gidildi.")

    def show_milk_page(self):
        self.sagim_sayfasi = SutimBilgileriSayfasi()
        self.sagim_sayfasi.show()
        print("Sağım Bilgileri sayfasına gidildi.")


    def show_feed_page(self):
        self.yem_sayfasi = YemAyarlama()
        self.yem_sayfasi.show()
        print("Yem Ayarlama ve Yem Tüketimi sayfasına gidildi.")

    def show_weight_page(self):
        self.agirlik_sayfasi = AgirlikTakibiSayfasi()
        self.agirlik_sayfasi.show()
        print("Ağırlık Takibi sayfasına gidildi.")

    def show_health_page(self):
        print("Aşı ve Sağlık Kayıtları sayfasına gidildi.")

    def show_backup_page(self):
        print("Veri Yedekleme ve Raporlama sayfasına gidildi.")

    def show_notifications_page(self):
        print("Bildirimler sayfasına gidildi.")

if __name__ == "__main__":
    app = QApplication([])
    window = ModernMenu()
    window.show()
    app.exec_()
