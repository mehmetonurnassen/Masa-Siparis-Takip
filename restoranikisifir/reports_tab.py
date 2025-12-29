"""
Ciro ve kazanç raporları ekranı
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
    QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta


class ReportsTab(QWidget):
    """Ciro ve kazanç raporları widget'ı"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.refresh_reports()
    
    def init_ui(self):
        """Arayüzü oluştur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Başlık
        title = QLabel("💰 Ciro ve Kazanç Raporları")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        
        # Özet kartları (Grid layout)
        summary_layout = QGridLayout()
        summary_layout.setSpacing(15)
        
        # Toplam Ciro kartı
        self.total_revenue_card = self.create_summary_card(
            "Toplam Ciro", 
            "0.00 TL", 
            "#3498db"
        )
        summary_layout.addWidget(self.total_revenue_card, 0, 0)
        
        # Bugünkü Ciro kartı
        self.today_revenue_card = self.create_summary_card(
            "Bugünkü Ciro", 
            "0.00 TL", 
            "#27ae60"
        )
        summary_layout.addWidget(self.today_revenue_card, 0, 1)
        
        # Bu Ayki Ciro kartı
        self.month_revenue_card = self.create_summary_card(
            "Bu Ayki Ciro", 
            "0.00 TL", 
            "#9b59b6"
        )
        summary_layout.addWidget(self.month_revenue_card, 0, 2)
        
        # Toplam Sipariş Sayısı kartı
        self.total_orders_card = self.create_summary_card(
            "Toplam Sipariş", 
            "0", 
            "#e67e22"
        )
        summary_layout.addWidget(self.total_orders_card, 1, 0)
        
        # Bugünkü Sipariş Sayısı kartı
        self.today_orders_card = self.create_summary_card(
            "Bugünkü Sipariş", 
            "0", 
            "#1abc9c"
        )
        summary_layout.addWidget(self.today_orders_card, 1, 1)
        
        # Ortalama Sipariş Tutarı kartı
        self.avg_order_card = self.create_summary_card(
            "Ortalama Sipariş", 
            "0.00 TL", 
            "#e74c3c"
        )
        summary_layout.addWidget(self.avg_order_card, 1, 2)
        
        layout.addLayout(summary_layout)
        
        # Yenile butonu
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_refresh = QPushButton("🔄 Yenile")
        btn_refresh.setMinimumHeight(40)
        btn_refresh.setMinimumWidth(150)
        btn_refresh.clicked.connect(self.refresh_reports)
        self.style_button(btn_refresh, "#3498db")
        btn_layout.addWidget(btn_refresh)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Sipariş geçmişi başlığı
        history_title = QLabel("Sipariş Geçmişi")
        history_title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(history_title)
        
        # Sipariş geçmişi tablosu
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels([
            "Tarih/Saat", "Masa No", "Ürün Sayısı", "Toplam Tutar", "Durum"
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.orders_table, stretch=1)
    
    def create_summary_card(self, title: str, value: str, color: str) -> QGroupBox:
        """Özet kartı oluştur"""
        card = QGroupBox(title)
        card.setMinimumHeight(120)
        card.setFont(QFont("Arial", 10, QFont.Bold))
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"color: {color}; padding: 10px;")
        layout.addWidget(value_label, stretch=1)
        
        card.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {color};
                border-radius: 10px;
                background-color: white;
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {color};
            }}
        """)
        
        # Value label'ı saklamak için referans ekle
        card.value_label = value_label
        
        return card
    
    def update_card_value(self, card: QGroupBox, value: str, color: str = None):
        """Kart değerini güncelle"""
        if hasattr(card, 'value_label'):
            card.value_label.setText(value)
            if color:
                card.value_label.setStyleSheet(f"color: {color}; padding: 10px;")
    
    def refresh_reports(self):
        """Raporları yenile"""
        try:
            # Toplam ciro
            total_revenue = self.db.get_total_revenue()
            self.update_card_value(
                self.total_revenue_card, 
                f"{total_revenue:.2f} TL",
                "#3498db"
            )
            
            # Bugünkü ciro
            today_revenue = self.db.get_today_revenue()
            self.update_card_value(
                self.today_revenue_card, 
                f"{today_revenue:.2f} TL",
                "#27ae60"
            )
            
            # Bu ayki ciro
            month_revenue = self.db.get_this_month_revenue()
            self.update_card_value(
                self.month_revenue_card, 
                f"{month_revenue:.2f} TL",
                "#9b59b6"
            )
            
            # Toplam sipariş sayısı
            total_orders = self.db.get_order_count()
            self.update_card_value(
                self.total_orders_card, 
                str(total_orders),
                "#e67e22"
            )
            
            # Bugünkü sipariş sayısı
            today_orders = self.db.get_today_order_count()
            self.update_card_value(
                self.today_orders_card, 
                str(today_orders),
                "#1abc9c"
            )
            
            # Ortalama sipariş tutarı
            avg_order = total_revenue / total_orders if total_orders > 0 else 0.0
            self.update_card_value(
                self.avg_order_card, 
                f"{avg_order:.2f} TL",
                "#e74c3c"
            )
            
            # Sipariş geçmişini yükle
            self.load_order_history()
            
        except Exception as e:
            print(f"Rapor yüklenirken hata: {e}")
    
    def load_order_history(self):
        """Sipariş geçmişini yükle"""
        orders = self.db.get_all_orders()
        
        self.orders_table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            # Tarih/Saat
            order_date = order.get("date", datetime.now())
            if isinstance(order_date, datetime):
                date_str = order_date.strftime("%d.%m.%Y %H:%M")
            else:
                date_str = str(order_date)
            
            date_item = QTableWidgetItem(date_str)
            self.orders_table.setItem(row, 0, date_item)
            
            # Masa No
            table_item = QTableWidgetItem(str(order.get("table_number", "-")))
            table_item.setTextAlignment(Qt.AlignCenter)
            self.orders_table.setItem(row, 1, table_item)
            
            # Ürün Sayısı
            items = order.get("items", [])
            total_items = sum(item.get("quantity", 0) for item in items)
            items_item = QTableWidgetItem(str(total_items))
            items_item.setTextAlignment(Qt.AlignCenter)
            self.orders_table.setItem(row, 2, items_item)
            
            # Toplam Tutar
            total = order.get("total", 0.0)
            total_item = QTableWidgetItem(f"{total:.2f} TL")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.orders_table.setItem(row, 3, total_item)
            
            # Durum
            status_item = QTableWidgetItem(order.get("status", "-"))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.orders_table.setItem(row, 4, status_item)
        
        # Tarihe göre sırala (en yeni üstte)
        self.orders_table.sortItems(0, Qt.DescendingOrder)
    
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
            "#3498db": "#2980b9",
            "#27ae60": "#229954",
            "#9b59b6": "#8e44ad",
            "#e67e22": "#d35400",
            "#1abc9c": "#16a085",
            "#e74c3c": "#c0392b"
        }
        return color_map.get(color, color)

