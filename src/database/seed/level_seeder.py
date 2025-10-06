from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

# Import dengan try-except untuk robustness
try:
    from src.models.kamus import Kamus
    from src.models.level import Level
    from src.models.sublevel import SubLevel
    from src.database.seeder import BaseSeeder
except ImportError:
    # Fallback ke relative imports jika absolute gagal
    from ...models.kamus import Kamus
    from ...models.level import Level
    from ...models.sublevel import SubLevel
    from ..seeder import BaseSeeder

class CompleteSeeder(BaseSeeder):
    """Seed Kamus, Levels, dan SubLevels saja (tanpa Soal)"""
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        """Run complete seeding process tanpa soal"""
        try:
            print("🌱 Starting complete seeding (Kamus, Levels, SubLevels)...")
            
            # 1. Seed Kamus first (ID 1-35)
            self.seed_kamus()
            
            # 2. Seed Levels (ID 1-4)
            self.seed_levels()
            
            # 3. Seed SubLevels (ID 1-10)
            self.seed_sublevels()
            
            print("✅ Complete seeding finished successfully!")
            print("ℹ️ Note: Run SoalSeeder separately for question seeding")
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Complete seeding failed: {e}")

    def seed_kamus(self):
        """Seed Kamus (Dictionary) data dengan fixed IDs"""
        print("📚 Seeding Kamus...")
        
        kamus_data = [
            # ID 1-5: Alphabet
            {"word_text": "A", "definition": "Huruf pertama dalam alfabet bahasa isyarat", "video_url": "https://example.com/video/A.mp4"},
            {"word_text": "B", "definition": "Huruf kedua dalam alfabet bahasa isyarat", "video_url": "https://example.com/video/B.mp4"},
            {"word_text": "C", "definition": "Huruf ketiga dalam alfabet bahasa isyarat", "video_url": "https://example.com/video/C.mp4"},
            {"word_text": "D", "definition": "Huruf keempat dalam alfabet bahasa isyarat", "video_url": "https://example.com/video/D.mp4"},
            {"word_text": "E", "definition": "Huruf kelima dalam alfabet bahasa isyarat", "video_url": "https://example.com/video/E.mp4"},
            
            # ID 6-10: Numbers
            {"word_text": "1", "definition": "Angka satu dalam bahasa isyarat", "video_url": "https://example.com/video/1.mp4"},
            {"word_text": "2", "definition": "Angka dua dalam bahasa isyarat", "video_url": "https://example.com/video/2.mp4"},
            {"word_text": "3", "definition": "Angka tiga dalam bahasa isyarat", "video_url": "https://example.com/video/3.mp4"},
            {"word_text": "4", "definition": "Angka empat dalam bahasa isyarat", "video_url": "https://example.com/video/4.mp4"},
            {"word_text": "5", "definition": "Angka lima dalam bahasa isyarat", "video_url": "https://example.com/video/5.mp4"},
            
            # ID 11-14: Greetings
            {"word_text": "Halo", "definition": "Sapaan ramah dalam bahasa isyarat", "video_url": "https://example.com/video/hello.mp4"},
            {"word_text": "Selamat Pagi", "definition": "Sapaan di pagi hari", "video_url": "https://example.com/video/good_morning.mp4"},
            {"word_text": "Terima Kasih", "definition": "Ungkapan rasa syukur", "video_url": "https://example.com/video/thank_you.mp4"},
            {"word_text": "Maaf", "definition": "Ungkapan permintaan maaf", "video_url": "https://example.com/video/sorry.mp4"},
            
            # ID 15-18: Family
            {"word_text": "Ayah", "definition": "Orang tua laki-laki", "video_url": "https://example.com/video/father.mp4"},
            {"word_text": "Ibu", "definition": "Orang tua perempuan", "video_url": "https://example.com/video/mother.mp4"},
            {"word_text": "Kakak", "definition": "Saudara yang lebih tua", "video_url": "https://example.com/video/older_sibling.mp4"},
            {"word_text": "Adik", "definition": "Saudara yang lebih muda", "video_url": "https://example.com/video/younger_sibling.mp4"},
            
            # ID 19-22: Colors
            {"word_text": "Merah", "definition": "Warna merah", "video_url": "https://example.com/video/red.mp4"},
            {"word_text": "Biru", "definition": "Warna biru", "video_url": "https://example.com/video/blue.mp4"},
            {"word_text": "Hijau", "definition": "Warna hijau", "video_url": "https://example.com/video/green.mp4"},
            {"word_text": "Kuning", "definition": "Warna kuning", "video_url": "https://example.com/video/yellow.mp4"},
            
            # ID 23-25: Animals
            {"word_text": "Kucing", "definition": "Hewan peliharaan berbulu", "video_url": "https://example.com/video/cat.mp4"},
            {"word_text": "Anjing", "definition": "Hewan peliharaan setia", "video_url": "https://example.com/video/dog.mp4"},
            {"word_text": "Burung", "definition": "Hewan yang bisa terbang", "video_url": "https://example.com/video/bird.mp4"},
            
            # ID 26-29: Food
            {"word_text": "Makan", "definition": "Aktivitas mengonsumsi makanan", "video_url": "https://example.com/video/eat.mp4"},
            {"word_text": "Minum", "definition": "Aktivitas mengonsumsi minuman", "video_url": "https://example.com/video/drink.mp4"},
            {"word_text": "Nasi", "definition": "Makanan pokok", "video_url": "https://example.com/video/rice.mp4"},
            {"word_text": "Air", "definition": "Minuman utama", "video_url": "https://example.com/video/water.mp4"},
            
            # ID 30-35: Weather & Time
            {"word_text": "Hujan", "definition": "Cuaca dengan air turun dari langit", "video_url": "https://example.com/video/rain.mp4"},
            {"word_text": "Panas", "definition": "Cuaca dengan suhu tinggi", "video_url": "https://example.com/video/hot.mp4"},
            {"word_text": "Dingin", "definition": "Cuaca dengan suhu rendah", "video_url": "https://example.com/video/cold.mp4"},
            {"word_text": "Hari", "definition": "Satuan waktu 24 jam", "video_url": "https://example.com/video/day.mp4"},
            {"word_text": "Malam", "definition": "Waktu setelah matahari tenggelam", "video_url": "https://example.com/video/night.mp4"},
            {"word_text": "Besok", "definition": "Hari setelah hari ini", "video_url": "https://example.com/video/tomorrow.mp4"},
        ]
        
        created_count = 0
        for data in kamus_data:
            existing = self.db.query(Kamus).filter(Kamus.word_text == data["word_text"]).first()
            if not existing:
                kamus = Kamus(**data)
                self.db.add(kamus)
                created_count += 1
                print(f"  ✅ Created kamus: {data['word_text']}")
            else:
                print(f"  ⚠️ Kamus already exists: {data['word_text']}")
        
        self.db.commit()
        print(f"✅ Kamus seeding completed. Created {created_count} entries.")

    def seed_levels(self):
        """Seed Level data dengan fixed IDs"""
        print("📊 Seeding Levels...")
        
        levels_data = [
            {"name": "Beginner", "description": "Basic sign language concepts for beginners", "tujuan": "Learn fundamental sign language skills and basic vocabulary"},
            {"name": "Elementary", "description": "Elementary level sign language for building vocabulary", "tujuan": "Expand vocabulary and begin forming simple sentences"},
            {"name": "Intermediate", "description": "Intermediate sign language with complex vocabulary", "tujuan": "Form complete sentences and engage in basic conversations"},
            {"name": "Advanced", "description": "Advanced sign language for fluent communication", "tujuan": "Achieve fluent conversation skills and cultural understanding"}
        ]
        
        created_count = 0
        for data in levels_data:
            existing = self.db.query(Level).filter(Level.name == data["name"]).first()
            if not existing:
                level = Level(**data)
                self.db.add(level)
                created_count += 1
                print(f"  ✅ Created level: {data['name']}")
            else:
                print(f"  ⚠️ Level already exists: {data['name']}")
        
        self.db.commit()
        print(f"✅ Level seeding completed. Created {created_count} levels.")

    def seed_sublevels(self):
        """Seed SubLevel data dengan fixed IDs dan level_id"""
        print("📋 Seeding SubLevels...")
        
        sublevels_data = [
            # Beginner Level (level_id: 1)
            {"name": "Alphabet A-E", "description": "Learn to sign letters A through E", "tujuan": "Master the first 5 letters of the alphabet", "level_id": 1},
            {"name": "Numbers 1-5", "description": "Learn to sign numbers from 1 to 5", "tujuan": "Understand basic number signs", "level_id": 1},
            {"name": "Basic Greetings", "description": "Common greeting phrases in sign language", "tujuan": "Communicate basic social interactions", "level_id": 1},
            {"name": "Family Members", "description": "Signs for family relationships", "tujuan": "Identify and sign family member names", "level_id": 1},
            
            # Elementary Level (level_id: 2)
            {"name": "Colors", "description": "Learn signs for basic colors", "tujuan": "Describe objects using colors", "level_id": 2},
            {"name": "Animals", "description": "Signs for common animals", "tujuan": "Identify and describe different animals", "level_id": 2},
            {"name": "Food & Drinks", "description": "Signs for common foods and beverages", "tujuan": "Communicate about meals and preferences", "level_id": 2},
            
            # Intermediate Level (level_id: 3)
            {"name": "Weather", "description": "Weather conditions and seasonal signs", "tujuan": "Discuss weather and climate", "level_id": 3},
            {"name": "Time Concepts", "description": "Signs for time, days, and temporal concepts", "tujuan": "Express temporal relationships", "level_id": 3},
            
            # Advanced Level (level_id: 4)
            {"name": "Complex Grammar", "description": "Advanced grammatical structures in sign language", "tujuan": "Use sophisticated sentence structures", "level_id": 4}
        ]
        
        created_count = 0
        for data in sublevels_data:
            existing = self.db.query(SubLevel).filter(
                SubLevel.name == data["name"],
                SubLevel.level_id == data["level_id"]
            ).first()
            
            if not existing:
                sublevel = SubLevel(**data)
                self.db.add(sublevel)
                created_count += 1
                print(f"  ✅ Created sublevel: {data['name']} (Level ID: {data['level_id']})")
            else:
                print(f"  ⚠️ SubLevel already exists: {data['name']}")
        
        self.db.commit()
        print(f"✅ SubLevel seeding completed. Created {created_count} sublevels.")