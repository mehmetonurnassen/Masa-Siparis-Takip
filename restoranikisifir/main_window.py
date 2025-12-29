"""
Ana pencere ve navigasyon sistemi
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QStackedWidget, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from floor_plan_tab import FloorPlanTab
from menu_management import MenuManagement
from reports_tab import ReportsTab


class MainWindow(QMainWindow):
    """Ana pencere sınıfı"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        self.setWindowTitle("Restoran Yönetim Sistemi")
        self.setGeometry(100, 100, 1200, 800)
        
        # Merkez widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout (yatay)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sol tarafta sidebar menü
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Sağ tarafta içerik alanı (StackedWidget)
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, stretch=1)
        
        # Sayfaları oluştur
        self.floor_plan_tab = FloorPlanTab(self.db)
        self.menu_management = MenuManagement(self.db)
        self.reports_tab = ReportsTab(self.db)
        
        self.content_stack.addWidget(self.floor_plan_tab)
        self.content_stack.addWidget(self.menu_management)
        self.content_stack.addWidget(self.reports_tab)
        
        # İlk sayfayı göster
        self.content_stack.setCurrentIndex(0)
        
        # Stil uygula
        self.apply_styles()
    
    def create_sidebar(self) -> QWidget:
        """Sol taraftaki menü sidebar'ını oluştur"""
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)
        
        # Başlık
        title = QLabel("Restoran Yönetimi")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: white; padding: 10px;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Masa Planı butonu
        btn_floor_plan = QPushButton("🪑 Masa Planı")
        btn_floor_plan.setMinimumHeight(50)
        btn_floor_plan.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
        self.style_menu_button(btn_floor_plan)
        layout.addWidget(btn_floor_plan)
        
        # Menü Yönetimi butonu
        btn_menu = QPushButton("📋 Menü Yönetimi")
        btn_menu.setMinimumHeight(50)
        btn_menu.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
        self.style_menu_button(btn_menu)
        layout.addWidget(btn_menu)
        
        # Ciro ve Kazanç butonu
        btn_reports = QPushButton("💰 Ciro ve Kazanç")
        btn_reports.setMinimumHeight(50)
        btn_reports.clicked.connect(lambda: self.content_stack.setCurrentIndex(2))
        self.style_menu_button(btn_reports)
        layout.addWidget(btn_reports)
        
        layout.addStretch()
        
        return sidebar
    
    def style_menu_button(self, button: QPushButton):
        """Menü butonlarına stil uygula"""
        button.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)
    
    def apply_styles(self):
        """Genel stilleri uygula"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
        """)

