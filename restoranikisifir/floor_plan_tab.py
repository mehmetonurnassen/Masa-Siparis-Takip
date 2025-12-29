"""
Dinamik masa planı ekranı
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QGridLayout, QMessageBox, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from order_dialog import OrderDialog


class FloorPlanTab(QWidget):
    """Masa planı sekmesi - Dinamik masa yönetimi"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.table_buttons = {}  # table_number -> button mapping
        self.init_ui()
        self.refresh_floor_plan()
    
    def init_ui(self):
        """Arayüzü oluştur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Başlık
        title = QLabel("Masa Planı")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        
        # Grid layout için container widget
        self.floor_container = QWidget()
        self.grid_layout = QGridLayout(self.floor_container)
        self.grid_layout.setSpacing(10)
        layout.addWidget(self.floor_container, stretch=1)
        
        # Alt kısım butonları
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Masa ekle butonu
        self.btn_add = QPushButton("➕ Masa Ekle")
        self.btn_add.setMinimumHeight(40)
        self.btn_add.setMinimumWidth(150)
        self.btn_add.clicked.connect(self.add_table)
        self.style_button(self.btn_add, "#27ae60")
        button_layout.addWidget(self.btn_add)
        
        # Masa sil butonu
        self.btn_remove = QPushButton("➖ Masa Sil")
        self.btn_remove.setMinimumHeight(40)
        self.btn_remove.setMinimumWidth(150)
        self.btn_remove.clicked.connect(self.remove_table)
        self.style_button(self.btn_remove, "#e74c3c")
        button_layout.addWidget(self.btn_remove)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def style_button(self, button: QPushButton, color: str):
        """Buton stilini uygula"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.8)};
            }}
        """)
    
    def darken_color(self, color: str, factor: float = 0.9) -> str:
        """Rengi koyulaştır (basit yaklaşım)"""
        # Hex rengi koyulaştır
        color_map = {
            "#27ae60": "#229954",
            "#e74c3c": "#c0392b",
            "#3498db": "#2980b9"
        }
        return color_map.get(color, color)
    
    def refresh_floor_plan(self):
        """Masa planını yeniden çiz"""
        # Mevcut butonları temizle
        for button in self.table_buttons.values():
            self.grid_layout.removeWidget(button)
            button.deleteLater()
        self.table_buttons.clear()
        
        # Masaları veritabanından çek
        tables = self.db.get_all_tables()
        
        if not tables:
            # Masalar yoksa bilgi mesajı göster
            info_label = QLabel("Henüz masa yok. Yukarıdaki butondan masa ekleyebilirsiniz.")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("color: #7f8c8d; font-size: 14px; padding: 20px;")
            self.grid_layout.addWidget(info_label, 0, 0)
            return
        
        # Izgara boyutunu hesapla (yaklaşık kare bir düzen için)
        import math
        num_tables = len(tables)
        cols = math.ceil(math.sqrt(num_tables))
        rows = math.ceil(num_tables / cols)
        
        # Butonları ızgaraya yerleştir
        for idx, table in enumerate(tables):
            table_num = table["table_number"]
            status = table["status"]
            
            # Masa butonu oluştur
            btn = QPushButton(f"Masa {table_num}\n{status}")
            btn.setMinimumSize(120, 100)
            btn.setFont(QFont("Arial", 12, QFont.Bold))
            
            # Duruma göre renk
            if status == "Boş":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: 2px solid #229954;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: #229954;
                    }
                """)
            else:  # Dolu
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: 2px solid #c0392b;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
            
            # Buton tıklama olayı
            btn.clicked.connect(lambda checked, tn=table_num: self.open_order_dialog(tn))
            
            # Izgaraya ekle
            row = idx // cols
            col = idx % cols
            self.grid_layout.addWidget(btn, row, col)
            
            # Mapping'de sakla
            self.table_buttons[table_num] = btn
        
        # Izgarayı ortala
        for i in range(cols):
            self.grid_layout.setColumnStretch(i, 1)
        for i in range(rows):
            self.grid_layout.setRowStretch(i, 1)
    
    def add_table(self):
        """Yeni masa ekle"""
        try:
            new_table_num = self.db.add_table()
            self.refresh_floor_plan()
            QMessageBox.information(
                self, 
                "Başarılı", 
                f"Masa {new_table_num} başarıyla eklendi."
            )
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Masa eklenirken hata oluştu:\n{str(e)}")
    
    def remove_table(self):
        """En yüksek numaralı masayı sil"""
        tables = self.db.get_all_tables()
        if not tables:
            QMessageBox.warning(self, "Uyarı", "Silinecek masa yok.")
            return
        
        # En yüksek numaralı masayı bul
        max_table = max(tables, key=lambda t: t["table_number"])
        table_num = max_table["table_number"]
        status = max_table["status"]
        
        if status == "Dolu":
            QMessageBox.warning(
                self, 
                "Uyarı", 
                f"Masa {table_num} şu anda dolu. Sipariş kapatılmadan masa silinemez!"
            )
            return
        
        # Onay al
        reply = QMessageBox.question(
            self,
            "Onay",
            f"Masa {table_num} silinecek. Emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_table(table_num)
                self.refresh_floor_plan()
                QMessageBox.information(self, "Başarılı", f"Masa {table_num} silindi.")
            except ValueError as e:
                QMessageBox.warning(self, "Hata", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Masa silinirken hata oluştu:\n{str(e)}")
    
    def open_order_dialog(self, table_number: int):
        """Sipariş diyaloğunu aç"""
        table_data = self.db.get_table(table_number)
        if not table_data:
            QMessageBox.warning(self, "Hata", "Masa bulunamadı!")
            return
        
        dialog = OrderDialog(self.db, table_data, self)
        dialog.exec_()
        # Diyalog kapatıldıktan sonra masa planını yenile
        self.refresh_floor_plan()

