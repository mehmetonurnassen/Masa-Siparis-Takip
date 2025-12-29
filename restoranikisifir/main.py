"""
Restoran Yönetim Sistemi - Ana Giriş Noktası
"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from database import Database
from main_window import MainWindow
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Ana fonksiyon"""
    # PyQt5 uygulaması oluştur
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern görünüm için
    
    try:
        # Veritabanı bağlantısı
        logger.info("Veritabanına bağlanılıyor...")
        db = Database()
        
        # Veritabanını seed et (eğer boşsa)
        logger.info("Veritabanı kontrol ediliyor...")
        db.seed_database()
        
        # Ana pencereyi oluştur ve göster
        logger.info("Uygulama başlatılıyor...")
        window = MainWindow(db)
        window.show()
        
        # Uygulamayı çalıştır
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Uygulama başlatılırken hata oluştu: {e}")
        
        # Kullanıcıya hata mesajı göster
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Hata")
        msg.setText("Uygulama başlatılamadı!")
        msg.setInformativeText(
            f"Lütfen MongoDB'nin çalıştığından emin olun.\n\n"
            f"Hata: {str(e)}\n\n"
            f"MongoDB'yi başlatmak için:\n"
            f"Windows: 'mongod' komutunu çalıştırın\n"
            f"Linux/Mac: 'sudo systemctl start mongod' veya 'brew services start mongodb-community'"
        )
        msg.exec_()
        sys.exit(1)


if __name__ == "__main__":
    main()

