import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFormLayout, QMessageBox
)

class YemAyarlama(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yem Ayarlama")
        self.resize(500, 500)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.group_box = QComboBox()
        self.group_box.addItems([
            "Kuzu (Normal)",
            "Kuzu Besi",
            "Süt Veren Koyun",
            "Normal Koyun"
        ])
        self.group_box.currentTextChanged.connect(self.toggle_sut_input)

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Canlı Ağırlık (kg)")

        self.sut_input = QLineEdit()
        self.sut_input.setPlaceholderText("Süt Verimi (Litre)")
        self.sut_input.setVisible(False)

        self.adg_input = QLineEdit()
        self.adg_input.setPlaceholderText("Günlük Ağırlık Artışı (gram)")
        self.adg_input.setVisible(False)

        self.result_labels = {
            "dm": QLabel("Kuru Madde: - kg/gün"),
            "energy": QLabel("Enerji: - kcal/gün"),
            "protein": QLabel("Protein: - g/gün")
        }

        form = QFormLayout()
        form.addRow("Hayvan Grubu:", self.group_box)
        form.addRow("Canlı Ağırlık (kg):", self.weight_input)
        form.addRow("Süt Verimi (Litre):", self.sut_input)
        form.addRow("Günlük Ağırlık Artışı (g):", self.adg_input)

        calc_button = QPushButton("Hesapla")
        calc_button.clicked.connect(self.calculate)

        layout.addLayout(form)
        layout.addWidget(calc_button)

        for label in self.result_labels.values():
            layout.addWidget(label)

        self.setLayout(layout)

    def toggle_sut_input(self, text):
        # Süt veren koyun için süt verimi inputu görünür
        self.sut_input.setVisible(text == "Süt Veren Koyun")
        # Kuzu besi için günlük ağırlık artışı inputu görünür
        self.adg_input.setVisible(text == "Kuzu Besi")

    def calculate(self):
        try:
            weight = float(self.weight_input.text())
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçerli bir canlı ağırlık giriniz.")
            return

        group = self.group_box.currentText()
        dm = energy = protein = 0

        if group == "Kuzu (Normal)":
            dm = weight * 0.035
            energy = weight * 65
            protein = weight * 6
        elif group == "Kuzu Besi":
            try:
                adg = float(self.adg_input.text())
            except ValueError:
                QMessageBox.warning(self, "Hata", "Geçerli bir günlük ağırlık artışı giriniz.")
                return
            # Kuru madde ihtiyacı
            dm = weight * 0.045
            # Enerji ihtiyacı
            energy = (weight * 88) + (adg * 2)  # Bakım + büyüme enerjisi
            # Protein ihtiyacı: Yaşama protein ve büyüme için ekstra protein
            protein = ((dm * 0.15) * 1100)   # Büyüme için ekstra protein
        elif group == "Süt Veren Koyun":
            try:
                milk = float(self.sut_input.text())
            except ValueError:
                QMessageBox.warning(self, "Hata", "Geçerli bir süt verimi giriniz.")
                return
            dm = weight * 0.045
            energy = weight * 40 + milk * 475
            protein = weight * 4.25 + milk * 45
        elif group == "Normal Koyun":
            dm = weight * 0.035
            energy = 2300  # Ortalama yaşama payı
            protein = weight * 3.5

        # Sonuçları yazdır
        self.result_labels["dm"].setText(f"Kuru Madde: {dm:.2f} kg/gün")
        self.result_labels["energy"].setText(f"Enerji: {energy:.0f} kcal/gün")
        self.result_labels["protein"].setText(f"Protein: {protein:.0f} g/gün")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YemAyarlama()
    window.show()
    sys.exit(app.exec_())
