"""
Menü yönetimi ekranı - CRUD işlemleri
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog,
    QLabel, QLineEdit, QDoubleSpinBox, QComboBox, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from typing import Dict, Optional


class ProductDialog(QDialog):
    """Ürün ekleme/düzenleme diyaloğu"""
    
    def __init__(self, db, parent=None, product_data: Optional[Dict] = None):
        super().__init__(parent)
        self.db = db
        self.product_data = product_data
        self.init_ui()
        
        if product_data:
            self.load_product_data()
    
    def init_ui(self):
        """Arayüzü oluştur"""
        self.setWindowTitle("Ürün Ekle" if not self.product_data else "Ürün Düzenle")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Ürün adı
        layout.addWidget(QLabel("Ürün Adı:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        # Fiyat
        layout.addWidget(QLabel("Fiyat (TL):"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(10000.0)
        self.price_input.setDecimals(2)
        self.price_input.setSingleStep(0.50)
        layout.addWidget(self.price_input)
        
        # Kategori
        layout.addWidget(QLabel("Kategori:"))
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        # Mevcut kategorileri yükle
        categorized = self.db.get_products_by_category()
        self.category_input.addItems(sorted(categorized.keys()))
        self.category_input.addItem("Diğer")
        layout.addWidget(self.category_input)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_save = QPushButton("Kaydet")
        btn_save.clicked.connect(self.accept)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
    
    def load_product_data(self):
        """Mevcut ürün verilerini yükle"""
        if self.product_data:
            self.name_input.setText(self.product_data.get("name", ""))
            self.price_input.setValue(self.product_data.get("price", 0.0))
            
            category = self.product_data.get("category", "Diğer")
            index = self.category_input.findText(category)
            if index >= 0:
                self.category_input.setCurrentIndex(index)
            else:
                self.category_input.setCurrentText(category)
    
    def get_product_data(self) -> Dict:
        """Form verilerini al"""
        return {
            "name": self.name_input.text().strip(),
            "price": self.price_input.value(),
            "category": self.category_input.currentText().strip() or "Diğer"
        }


class MenuManagement(QWidget):
    """Menü yönetimi widget'ı"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.refresh_products()
    
    def init_ui(self):
        """Arayüzü oluştur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Başlık
        title = QLabel("Menü Yönetimi")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_add = QPushButton("➕ Yeni Ürün Ekle")
        btn_add.setMinimumHeight(40)
        btn_add.setMinimumWidth(150)
        btn_add.clicked.connect(self.add_product)
        self.style_button(btn_add, "#27ae60")
        button_layout.addWidget(btn_add)
        
        btn_delete = QPushButton("➖ Seçili Ürünü Sil")
        btn_delete.setMinimumHeight(40)
        btn_delete.setMinimumWidth(150)
        btn_delete.clicked.connect(self.delete_product)
        self.style_button(btn_delete, "#e74c3c")
        button_layout.addWidget(btn_delete)
        
        btn_refresh = QPushButton("🔄 Yenile")
        btn_refresh.setMinimumHeight(40)
        btn_refresh.setMinimumWidth(100)
        btn_refresh.clicked.connect(self.refresh_products)
        self.style_button(btn_refresh, "#3498db")
        button_layout.addWidget(btn_refresh)
        
        layout.addLayout(button_layout)
        
        # Ürün tablosu
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["Ürün Adı", "Fiyat (TL)", "Kategori", "İşlem"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.products_table)
    
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
        """)
    
    def darken_color(self, color: str) -> str:
        """Rengi koyulaştır"""
        color_map = {
            "#27ae60": "#229954",
            "#e74c3c": "#c0392b",
            "#3498db": "#2980b9"
        }
        return color_map.get(color, color)
    
    def refresh_products(self):
        """Ürün listesini yenile"""
        products = self.db.get_all_products()
        
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Ürün adı
            self.products_table.setItem(row, 0, QTableWidgetItem(product["name"]))
            
            # Fiyat
            price_item = QTableWidgetItem(f"{product['price']:.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.products_table.setItem(row, 1, price_item)
            
            # Kategori
            self.products_table.setItem(row, 2, QTableWidgetItem(product.get("category", "Diğer")))
            
            # Düzenle butonu
            btn_edit = QPushButton("✏️ Düzenle")
            btn_edit.setMaximumWidth(100)
            btn_edit.clicked.connect(lambda checked, p=product: self.edit_product(p))
            self.products_table.setCellWidget(row, 3, btn_edit)
    
    def add_product(self):
        """Yeni ürün ekle"""
        dialog = ProductDialog(self.db, self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_product_data()
            
            if not data["name"]:
                QMessageBox.warning(self, "Uyarı", "Ürün adı boş olamaz!")
                return
            
            try:
                self.db.add_product(data["name"], data["price"], data["category"])
                QMessageBox.information(self, "Başarılı", "Ürün eklendi!")
                self.refresh_products()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Ürün eklenirken hata oluştu:\n{str(e)}")
    
    def edit_product(self, product: Dict):
        """Ürün düzenle"""
        dialog = ProductDialog(self.db, self, product)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_product_data()
            
            if not data["name"]:
                QMessageBox.warning(self, "Uyarı", "Ürün adı boş olamaz!")
                return
            
            try:
                # Mevcut ürünü sil
                self.db.delete_product(product["_id"])
                # Yeni verilerle ekle
                self.db.add_product(data["name"], data["price"], data["category"])
                QMessageBox.information(self, "Başarılı", "Ürün güncellendi!")
                self.refresh_products()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Ürün güncellenirken hata oluştu:\n{str(e)}")
    
    def delete_product(self):
        """Seçili ürünü sil"""
        current_row = self.products_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir ürün seçin!")
            return
        
        product_name = self.products_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self,
            "Onay",
            f"'{product_name}' ürünü silinecek. Emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Ürünü bul ve sil
                products = self.db.get_all_products()
                product = products[current_row]
                self.db.delete_product(product["_id"])
                QMessageBox.information(self, "Başarılı", "Ürün silindi!")
                self.refresh_products()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Ürün silinirken hata oluştu:\n{str(e)}")

