"""
Sipariş alma diyaloğu
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QTabWidget, QWidget,
    QLabel, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from typing import List, Dict


class OrderDialog(QDialog):
    """Sipariş diyaloğu - Ürün seçimi ve sipariş yönetimi"""
    
    def __init__(self, db, table_data, parent=None):
        super().__init__(parent)
        self.db = db
        self.table_data = table_data
        self.table_number = table_data["table_number"]
        self.order_items = []  # {"product": {...}, "quantity": int, "total": float}
        self.init_ui()
        self.load_existing_order()
    
    def init_ui(self):
        """Arayüzü oluştur"""
        self.setWindowTitle(f"Masa {self.table_number} - Sipariş")
        self.setMinimumSize(900, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Başlık
        title = QLabel(f"Masa {self.table_number} - Sipariş")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Ana içerik (yatay layout)
        content_layout = QHBoxLayout()
        
        # Sol taraf: Menü (kategorilere göre sekmeler)
        menu_widget = self.create_menu_widget()
        content_layout.addWidget(menu_widget, stretch=1)
        
        # Sağ taraf: Adisyon tablosu
        order_widget = self.create_order_widget()
        content_layout.addWidget(order_widget, stretch=1)
        
        layout.addLayout(content_layout)
        
        # Alt kısım: Toplam ve butonlar
        bottom_layout = QHBoxLayout()
        
        # Toplam etiketi
        self.total_label = QLabel("Toplam: 0.00 TL")
        self.total_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.total_label.setStyleSheet("color: #27ae60; padding: 10px;")
        bottom_layout.addWidget(self.total_label)
        
        bottom_layout.addStretch()
        
        # Siparişi Kaydet butonu
        btn_save = QPushButton("💾 Siparişi Kaydet")
        btn_save.setMinimumHeight(40)
        btn_save.setMinimumWidth(150)
        btn_save.clicked.connect(self.save_order)
        self.style_button(btn_save, "#3498db")
        bottom_layout.addWidget(btn_save)
        
        # Hesabı Kapat butonu (sadece dolu masalar için)
        if self.table_data["status"] == "Dolu":
            btn_close = QPushButton("💰 Hesabı Kapat")
            btn_close.setMinimumHeight(40)
            btn_close.setMinimumWidth(150)
            btn_close.clicked.connect(self.close_order)
            self.style_button(btn_close, "#27ae60")
            bottom_layout.addWidget(btn_close)
        
        # İptal butonu
        btn_cancel = QPushButton("❌ İptal")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setMinimumWidth(100)
        btn_cancel.clicked.connect(self.reject)
        self.style_button(btn_cancel, "#95a5a6")
        bottom_layout.addWidget(btn_cancel)
        
        layout.addLayout(bottom_layout)
    
    def create_menu_widget(self) -> QWidget:
        """Sol taraftaki menü widget'ını oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Menü")
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        
        # Kategorilere göre sekmeler
        self.menu_tabs = QTabWidget()
        categorized_products = self.db.get_products_by_category()
        
        for category, products in categorized_products.items():
            category_widget = QWidget()
            category_layout = QVBoxLayout(category_widget)
            
            # Scroll için bir layout (basit grid benzeri)
            from PyQt5.QtWidgets import QScrollArea, QGridLayout as QGL
            
            scroll = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QGL(scroll_widget)
            
            for product in products:
                btn = QPushButton(f"{product['name']}\n{product['price']:.2f} TL")
                btn.setMinimumHeight(70)
                btn.setFont(QFont("Arial", 10))
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ecf0f1;
                        border: 1px solid #bdc3c7;
                        border-radius: 5px;
                        text-align: center;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #3498db;
                        color: white;
                    }
                """)
                
                # Ürünü siparişe ekle
                btn.clicked.connect(
                    lambda checked, p=product: self.add_to_order(p)
                )
                
                scroll_layout.addWidget(btn)
            
            scroll.setWidget(scroll_widget)
            scroll.setWidgetResizable(True)
            category_layout.addWidget(scroll)
            
            self.menu_tabs.addTab(category_widget, category)
        
        layout.addWidget(self.menu_tabs)
        
        return widget
    
    def create_order_widget(self) -> QWidget:
        """Sağ taraftaki adisyon tablosunu oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Sipariş Listesi")
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        
        # Adisyon tablosu
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(5)
        self.order_table.setHorizontalHeaderLabels(["Ürün", "Birim Fiyat", "Adet", "Toplam", "İşlem"])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.order_table.setAlternatingRowColors(True)
        layout.addWidget(self.order_table)
        
        return widget
    
    def add_to_order(self, product: Dict):
        """Ürünü siparişe ekle"""
        # Aynı ürün varsa adetini artır
        # ObjectId karşılaştırması için str() kullan
        product_id = str(product.get("_id", ""))
        for item in self.order_items:
            item_product = item.get("product", {})
            item_product_id = str(item_product.get("_id", ""))
            if item_product_id == product_id:
                item["quantity"] += 1
                item["total"] = item["quantity"] * item_product["price"]
                self.update_order_table()
                return
        
        # Yeni ürün ekle
        self.order_items.append({
            "product": product,
            "quantity": 1,
            "total": product["price"]
        })
        self.update_order_table()
    
    def update_order_table(self):
        """Sipariş tablosunu güncelle"""
        self.order_table.setRowCount(len(self.order_items))
        
        for row, item in enumerate(self.order_items):
            product = item["product"]
            quantity = item["quantity"]
            unit_price = product["price"]
            total = item["total"]
            
            # Ürün adı
            self.order_table.setItem(row, 0, QTableWidgetItem(product["name"]))
            
            # Birim fiyat
            price_item = QTableWidgetItem(f"{unit_price:.2f} TL")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.order_table.setItem(row, 1, price_item)
            
            # Adet
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.order_table.setItem(row, 2, qty_item)
            
            # Toplam
            total_item = QTableWidgetItem(f"{total:.2f} TL")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.order_table.setItem(row, 3, total_item)
            
            # Sil butonu
            btn_remove = QPushButton("✖")
            btn_remove.setMaximumWidth(40)
            btn_remove.clicked.connect(lambda checked, r=row: self.remove_item(r))
            self.order_table.setCellWidget(row, 4, btn_remove)
        
        # Toplamı güncelle
        total = sum(item["total"] for item in self.order_items)
        self.total_label.setText(f"Toplam: {total:.2f} TL")
    
    def remove_item(self, row: int):
        """Siparişten ürün çıkar"""
        if 0 <= row < len(self.order_items):
            self.order_items.pop(row)
            self.update_order_table()
    
    def load_existing_order(self):
        """Mevcut siparişi yükle (masa doluysa)"""
        if self.table_data["status"] == "Dolu" and self.table_data.get("current_order"):
            # Mevcut siparişi yükle
            # current_order içinde tam product verisi saklanıyor
            for order_item in self.table_data["current_order"]:
                # Order item yapısını kontrol et ve düzelt
                if isinstance(order_item, dict) and "product" in order_item:
                    self.order_items.append(order_item)
            self.update_order_table()
    
    def save_order(self):
        """Siparişi kaydet"""
        if not self.order_items:
            QMessageBox.warning(self, "Uyarı", "Sipariş boş!")
            return
        
        try:
            # Siparişi masaya kaydet
            self.db.save_order_to_table(self.table_number, self.order_items)
            QMessageBox.information(self, "Başarılı", "Sipariş kaydedildi!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Sipariş kaydedilirken hata oluştu:\n{str(e)}")
    
    def close_order(self):
        """Hesabı kapat"""
        if not self.order_items:
            QMessageBox.warning(self, "Uyarı", "Sipariş boş!")
            return
        
        total = sum(item["total"] for item in self.order_items)
        
        reply = QMessageBox.question(
            self,
            "Onay",
            f"Toplam tutar: {total:.2f} TL\nHesap kapatılsın mı?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.close_order(self.table_number, total)
                QMessageBox.information(
                    self, 
                    "Başarılı", 
                    f"Hesap kapatıldı!\nToplam: {total:.2f} TL"
                )
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Hesap kapatılırken hata oluştu:\n{str(e)}")
    
    def style_button(self, button: QPushButton, color: str):
        """Buton stilini uygula"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
    
    def darken_color(self, color: str) -> str:
        """Rengi koyulaştır"""
        color_map = {
            "#3498db": "#2980b9",
            "#27ae60": "#229954",
            "#95a5a6": "#7f8c8d"
        }
        return color_map.get(color, color)

