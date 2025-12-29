"""
MongoDB veritabanı bağlantısı ve işlemleri
"""
from pymongo import MongoClient
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """MongoDB veritabanı sınıfı"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017/", db_name: str = "restoran_db"):
        """
        Veritabanı bağlantısını başlat
        
        Args:
            connection_string: MongoDB bağlantı dizesi
            db_name: Veritabanı adı
        """
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[db_name]
            self.tables = self.db["tables"]
            self.products = self.db["products"]
            self.orders = self.db["orders"]
            logger.info(f"MongoDB bağlantısı başarılı: {db_name}")
        except Exception as e:
            logger.error(f"MongoDB bağlantı hatası: {e}")
            raise
    
    def seed_database(self):
        """Veritabanını 10 masa ve 30 ürün ile başlangıç verileriyle doldur"""
        
        # Mevcut verileri kontrol et
        if self.tables.count_documents({}) > 0 or self.products.count_documents({}) > 0:
            logger.info("Veritabanı zaten dolu, seeding atlanıyor")
            return
        
        # 10 masa oluştur
        tables_data = [
            {"table_number": i, "status": "Boş", "current_order": []}
            for i in range(1, 11)
        ]
        self.tables.insert_many(tables_data)
        logger.info("10 masa oluşturuldu")
        
        # 30 ürün oluştur (çeşitli kategorilerde)
        products_data = [
            # İçecekler
            {"name": "Türk Kahvesi", "price": 25.0, "category": "İçecekler"},
            {"name": "Espresso", "price": 20.0, "category": "İçecekler"},
            {"name": "Americano", "price": 22.0, "category": "İçecekler"},
            {"name": "Cappuccino", "price": 28.0, "category": "İçecekler"},
            {"name": "Latte", "price": 30.0, "category": "İçecekler"},
            {"name": "Çay", "price": 15.0, "category": "İçecekler"},
            {"name": "Taze Sıkılmış Portakal Suyu", "price": 35.0, "category": "İçecekler"},
            {"name": "Ayran", "price": 12.0, "category": "İçecekler"},
            {"name": "Kola", "price": 18.0, "category": "İçecekler"},
            {"name": "Fanta", "price": 18.0, "category": "İçecekler"},
            
            # Kahvaltı
            {"name": "Kahvaltı Tabağı", "price": 85.0, "category": "Kahvaltı"},
            {"name": "Menemen", "price": 65.0, "category": "Kahvaltı"},
            {"name": "Omlet", "price": 55.0, "category": "Kahvaltı"},
            {"name": "Sucuklu Yumurta", "price": 60.0, "category": "Kahvaltı"},
            {"name": "Tost", "price": 35.0, "category": "Kahvaltı"},
            
            # Ana Yemekler
            {"name": "Hamburger", "price": 120.0, "category": "Ana Yemekler"},
            {"name": "Cheeseburger", "price": 130.0, "category": "Ana Yemekler"},
            {"name": "Pizza Margherita", "price": 90.0, "category": "Ana Yemekler"},
            {"name": "Pizza Pepperoni", "price": 110.0, "category": "Ana Yemekler"},
            {"name": "Döner", "price": 80.0, "category": "Ana Yemekler"},
            {"name": "Lahmacun", "price": 45.0, "category": "Ana Yemekler"},
            {"name": "Köfte", "price": 95.0, "category": "Ana Yemekler"},
            {"name": "Tavuk Şiş", "price": 100.0, "category": "Ana Yemekler"},
            {"name": "Izgara Balık", "price": 150.0, "category": "Ana Yemekler"},
            
            # Tatlılar
            {"name": "Baklava", "price": 50.0, "category": "Tatlılar"},
            {"name": "Künefe", "price": 55.0, "category": "Tatlılar"},
            {"name": "Sütlaç", "price": 30.0, "category": "Tatlılar"},
            {"name": "Dondurma", "price": 35.0, "category": "Tatlılar"},
            {"name": "Cheesecake", "price": 45.0, "category": "Tatlılar"},
            {"name": "Tiramisu", "price": 50.0, "category": "Tatlılar"},
        ]
        
        self.products.insert_many(products_data)
        logger.info("30 ürün oluşturuldu")
    
    # Tablo işlemleri
    def get_all_tables(self) -> List[Dict]:
        """Tüm masaları getir"""
        return list(self.tables.find().sort("table_number", 1))
    
    def get_table(self, table_number: int) -> Optional[Dict]:
        """Belirli bir masayı getir"""
        return self.tables.find_one({"table_number": table_number})
    
    def add_table(self) -> int:
        """Yeni masa ekle (bir sonraki numarayı otomatik atar)"""
        max_table = self.tables.find_one(sort=[("table_number", -1)])
        next_number = (max_table["table_number"] + 1) if max_table else 1
        
        self.tables.insert_one({
            "table_number": next_number,
            "status": "Boş",
            "current_order": []
        })
        logger.info(f"Masa {next_number} eklendi")
        return next_number
    
    def delete_table(self, table_number: int) -> bool:
        """Masayı sil (sadece boşsa)"""
        table = self.get_table(table_number)
        if not table:
            return False
        
        if table["status"] == "Dolu":
            raise ValueError("Dolu masa silinemez!")
        
        self.tables.delete_one({"table_number": table_number})
        logger.info(f"Masa {table_number} silindi")
        return True
    
    def update_table_status(self, table_number: int, status: str):
        """Masa durumunu güncelle"""
        self.tables.update_one(
            {"table_number": table_number},
            {"$set": {"status": status}}
        )
    
    def save_order_to_table(self, table_number: int, order_items: List[Dict]):
        """Siparişi masaya kaydet"""
        self.tables.update_one(
            {"table_number": table_number},
            {"$set": {"current_order": order_items, "status": "Dolu"}}
        )
    
    def close_order(self, table_number: int, total: float):
        """Siparişi kapat ve arşivle"""
        table = self.get_table(table_number)
        if not table:
            return
        
        # Order'ı arşivle
        from datetime import datetime
        self.orders.insert_one({
            "table_number": table_number,
            "items": table["current_order"],
            "total": total,
            "date": datetime.now(),
            "status": "Tamamlandı"
        })
        
        # Masayı temizle
        self.tables.update_one(
            {"table_number": table_number},
            {"$set": {"current_order": [], "status": "Boş"}}
        )
        logger.info(f"Masa {table_number} kapatıldı, toplam: {total} TL")
    
    # Ürün işlemleri
    def get_all_products(self) -> List[Dict]:
        """Tüm ürünleri getir"""
        return list(self.products.find().sort("name", 1))
    
    def get_products_by_category(self) -> Dict[str, List[Dict]]:
        """Ürünleri kategoriye göre grupla"""
        products = self.get_all_products()
        categorized = {}
        for product in products:
            category = product.get("category", "Diğer")
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(product)
        return categorized
    
    def add_product(self, name: str, price: float, category: str):
        """Yeni ürün ekle"""
        self.products.insert_one({
            "name": name,
            "price": price,
            "category": category
        })
        logger.info(f"Ürün eklendi: {name}")
    
    def delete_product(self, product_id):
        """Ürün sil"""
        self.products.delete_one({"_id": product_id})
        logger.info(f"Ürün silindi: {product_id}")
    
    # Rapor ve analiz işlemleri
    def get_all_orders(self) -> List[Dict]:
        """Tüm tamamlanmış siparişleri getir"""
        return list(self.orders.find({"status": "Tamamlandı"}).sort("date", -1))
    
    def get_total_revenue(self) -> float:
        """Toplam ciroyu hesapla"""
        pipeline = [
            {"$match": {"status": "Tamamlandı"}},
            {"$group": {"_id": None, "total": {"$sum": "$total"}}}
        ]
        result = list(self.orders.aggregate(pipeline))
        return result[0]["total"] if result else 0.0
    
    def get_revenue_by_period(self, start_date=None, end_date=None) -> float:
        """Belirli bir dönem için ciroyu hesapla"""
        match_query = {"status": "Tamamlandı"}
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            match_query["date"] = date_query
        
        pipeline = [
            {"$match": match_query},
            {"$group": {"_id": None, "total": {"$sum": "$total"}}}
        ]
        result = list(self.orders.aggregate(pipeline))
        return result[0]["total"] if result else 0.0
    
    def get_today_revenue(self) -> float:
        """Bugünkü ciroyu hesapla"""
        from datetime import datetime, timedelta
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        return self.get_revenue_by_period(today_start, today_end)
    
    def get_this_month_revenue(self) -> float:
        """Bu ayki ciroyu hesapla"""
        from datetime import datetime
        today = datetime.now()
        month_start = datetime(today.year, today.month, 1)
        return self.get_revenue_by_period(month_start, datetime.now())
    
    def get_order_count(self) -> int:
        """Toplam sipariş sayısını getir"""
        return self.orders.count_documents({"status": "Tamamlandı"})
    
    def get_today_order_count(self) -> int:
        """Bugünkü sipariş sayısını getir"""
        from datetime import datetime, timedelta
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        return self.orders.count_documents({
            "status": "Tamamlandı",
            "date": {"$gte": today_start, "$lt": today_end}
        })

