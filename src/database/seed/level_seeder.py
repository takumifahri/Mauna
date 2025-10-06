from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

# Import dengan try-except untuk robustness
try:
    from src.models.kamus import Kamus
    from src.models.level import Level
    from src.models.sublevel import SubLevel
    from src.models.soal import Soal
    from src.database.seeder import BaseSeeder
except ImportError:
    # Fallback ke relative imports jika absolute gagal
    from ...models.kamus import Kamus
    from ...models.level import Level
    from ...models.sublevel import SubLevel
    from ...models.soal import Soal
    from ..seeder import BaseSeeder

class CompleteSeeder(BaseSeeder):
    """Seed Kamus, Levels, SubLevels, dan Soal dengan fixed IDs"""
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        """Run complete seeding process"""
        try:
            print("🌱 Starting complete seeding with fixed IDs...")
            
            # 1. Seed Kamus first (ID 1-30)
            self.seed_kamus()
            
            # 2. Seed Levels (ID 1-4)
            self.seed_levels()
            
            # 3. Seed SubLevels (ID 1-10)
            self.seed_sublevels()
            
            # 4. Seed Soal (ID 1-40)
            self.seed_soal()
            
            print("✅ Complete seeding finished successfully!")
            
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
            # ID 1
            {
                "name": "Beginner",
                "description": "Basic sign language concepts for beginners",
                "tujuan": "Learn fundamental sign language skills and basic vocabulary"
            },
            # ID 2
            {
                "name": "Elementary", 
                "description": "Elementary level sign language for building vocabulary",
                "tujuan": "Expand vocabulary and begin forming simple sentences"
            },
            # ID 3
            {
                "name": "Intermediate",
                "description": "Intermediate sign language with complex vocabulary", 
                "tujuan": "Form complete sentences and engage in basic conversations"
            },
            # ID 4
            {
                "name": "Advanced",
                "description": "Advanced sign language for fluent communication",
                "tujuan": "Achieve fluent conversation skills and cultural understanding"
            }
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
            # ID 1
            {
                "name": "Alphabet A-E",
                "description": "Learn to sign letters A through E",
                "tujuan": "Master the first 5 letters of the alphabet",
                "level_id": 1
            },
            # ID 2
            {
                "name": "Numbers 1-5", 
                "description": "Learn to sign numbers from 1 to 5",
                "tujuan": "Understand basic number signs",
                "level_id": 1
            },
            # ID 3
            {
                "name": "Basic Greetings",
                "description": "Common greeting phrases in sign language",
                "tujuan": "Communicate basic social interactions", 
                "level_id": 1
            },
            # ID 4
            {
                "name": "Family Members",
                "description": "Signs for family relationships",
                "tujuan": "Identify and sign family member names",
                "level_id": 1
            },
            
            # Elementary Level (level_id: 2)
            # ID 5
            {
                "name": "Colors",
                "description": "Learn signs for basic colors", 
                "tujuan": "Describe objects using colors",
                "level_id": 2
            },
            # ID 6
            {
                "name": "Animals",
                "description": "Signs for common animals",
                "tujuan": "Identify and describe different animals",
                "level_id": 2
            },
            # ID 7
            {
                "name": "Food & Drinks",
                "description": "Signs for common foods and beverages",
                "tujuan": "Communicate about meals and preferences",
                "level_id": 2
            },
            
            # Intermediate Level (level_id: 3)
            # ID 8
            {
                "name": "Weather",
                "description": "Weather conditions and seasonal signs",
                "tujuan": "Discuss weather and climate",
                "level_id": 3
            },
            # ID 9
            {
                "name": "Time Concepts",
                "description": "Signs for time, days, and temporal concepts",
                "tujuan": "Express temporal relationships",
                "level_id": 3
            },
            
            # Advanced Level (level_id: 4)
            # ID 10
            {
                "name": "Complex Grammar",
                "description": "Advanced grammatical structures in sign language",
                "tujuan": "Use sophisticated sentence structures",
                "level_id": 4
            }
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

    def seed_soal(self):
        """Seed Soal data dengan fixed IDs, dictionary_id, dan sublevel_id"""
        print("❓ Seeding Soal...")
        
        soal_data = [
            # Alphabet A-E SubLevel (sublevel_id: 1)
            {
                "question": "Bagaimana cara membuat isyarat untuk huruf 'A'?",
                "answer": "Kepalkan tangan dengan ibu jari di samping",
                "dictionary_id": 1,  # Kamus: A
                "sublevel_id": 1,    # SubLevel: Alphabet A-E
                "video_url": "https://example.com/quiz/letter_A.mp4"
            },
            {
                "question": "Tunjukkan isyarat untuk huruf 'B'",
                "answer": "Tangan terbuka dengan jari-jari rapat dan ibu jari menekuk",
                "dictionary_id": 2,  # Kamus: B
                "sublevel_id": 1,    # SubLevel: Alphabet A-E
                "video_url": "https://example.com/quiz/letter_B.mp4"
            },
            {
                "question": "Bagaimana isyarat huruf 'C'?",
                "answer": "Bentuk tangan seperti huruf C",
                "dictionary_id": 3,  # Kamus: C
                "sublevel_id": 1,    # SubLevel: Alphabet A-E
                "video_url": "https://example.com/quiz/letter_C.mp4"
            },
            {
                "question": "Praktikkan isyarat huruf 'D'",
                "answer": "Telunjuk tegak, jari lain menekuk, ibu jari menyentuh jari tengah",
                "dictionary_id": 4,  # Kamus: D
                "sublevel_id": 1,    # SubLevel: Alphabet A-E
                "video_url": "https://example.com/quiz/letter_D.mp4"
            },
            {
                "question": "Tunjukkan cara membuat isyarat huruf 'E'",
                "answer": "Semua jari menekuk menyentuh ibu jari",
                "dictionary_id": 5,  # Kamus: E
                "sublevel_id": 1,    # SubLevel: Alphabet A-E
                "video_url": "https://example.com/quiz/letter_E.mp4"
            },
            
            # Numbers 1-5 SubLevel (sublevel_id: 2)
            {
                "question": "Bagaimana cara menunjukkan angka '1' dalam bahasa isyarat?",
                "answer": "Telunjuk tegak ke atas",
                "dictionary_id": 6,  # Kamus: 1
                "sublevel_id": 2,    # SubLevel: Numbers 1-5
                "video_url": "https://example.com/quiz/number_1.mp4"
            },
            {
                "question": "Praktikkan isyarat untuk angka '2'",
                "answer": "Telunjuk dan jari tengah tegak",
                "dictionary_id": 7,  # Kamus: 2
                "sublevel_id": 2,    # SubLevel: Numbers 1-5
                "video_url": "https://example.com/quiz/number_2.mp4"
            },
            {
                "question": "Tunjukkan isyarat angka '3'",
                "answer": "Telunjuk, jari tengah, dan jari manis tegak",
                "dictionary_id": 8,  # Kamus: 3
                "sublevel_id": 2,    # SubLevel: Numbers 1-5
                "video_url": "https://example.com/quiz/number_3.mp4"
            },
            {
                "question": "Bagaimana cara membuat isyarat angka '4'?",
                "answer": "Empat jari tegak, ibu jari menekuk",
                "dictionary_id": 9,  # Kamus: 4
                "sublevel_id": 2,    # SubLevel: Numbers 1-5
                "video_url": "https://example.com/quiz/number_4.mp4"
            },
            {
                "question": "Praktikkan isyarat untuk angka '5'",
                "answer": "Semua jari terbuka dan tegak",
                "dictionary_id": 10, # Kamus: 5
                "sublevel_id": 2,    # SubLevel: Numbers 1-5
                "video_url": "https://example.com/quiz/number_5.mp4"
            },
            
            # Basic Greetings SubLevel (sublevel_id: 3)
            {
                "question": "Bagaimana cara mengucapkan 'Halo' dalam bahasa isyarat?",
                "answer": "Lambaikan tangan dengan telapak terbuka",
                "dictionary_id": 11, # Kamus: Halo
                "sublevel_id": 3,    # SubLevel: Basic Greetings
                "video_url": "https://example.com/quiz/hello.mp4"
            },
            {
                "question": "Tunjukkan isyarat untuk 'Selamat Pagi'",
                "answer": "Gabungkan isyarat 'baik' dan 'pagi'",
                "dictionary_id": 12, # Kamus: Selamat Pagi
                "sublevel_id": 3,    # SubLevel: Basic Greetings
                "video_url": "https://example.com/quiz/good_morning.mp4"
            },
            {
                "question": "Bagaimana cara mengucapkan 'Terima Kasih'?",
                "answer": "Sentuh dagu dengan ujung jari kemudian gerakkan ke depan",
                "dictionary_id": 13, # Kamus: Terima Kasih
                "sublevel_id": 3,    # SubLevel: Basic Greetings
                "video_url": "https://example.com/quiz/thank_you.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Maaf'",
                "answer": "Kepalkan tangan dan gosokkan di dada dengan gerakan melingkar",
                "dictionary_id": 14, # Kamus: Maaf
                "sublevel_id": 3,    # SubLevel: Basic Greetings
                "video_url": "https://example.com/quiz/sorry.mp4"
            },
            
            # Family Members SubLevel (sublevel_id: 4)
            {
                "question": "Bagaimana cara mengatakan 'Ayah' dalam bahasa isyarat?",
                "answer": "Sentuh dahi dengan ibu jari tangan terbuka",
                "dictionary_id": 15, # Kamus: Ayah
                "sublevel_id": 4,    # SubLevel: Family Members
                "video_url": "https://example.com/quiz/father.mp4"
            },
            {
                "question": "Tunjukkan isyarat untuk 'Ibu'",
                "answer": "Sentuh dagu dengan ibu jari tangan terbuka",
                "dictionary_id": 16, # Kamus: Ibu
                "sublevel_id": 4,    # SubLevel: Family Members
                "video_url": "https://example.com/quiz/mother.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Kakak'",
                "answer": "Isyarat saudara dengan tangan naik ke atas",
                "dictionary_id": 17, # Kamus: Kakak
                "sublevel_id": 4,    # SubLevel: Family Members
                "video_url": "https://example.com/quiz/older_sibling.mp4"
            },
            {
                "question": "Bagaimana cara mengisyaratkan 'Adik'?",
                "answer": "Isyarat saudara dengan tangan turun ke bawah",
                "dictionary_id": 18, # Kamus: Adik
                "sublevel_id": 4,    # SubLevel: Family Members
                "video_url": "https://example.com/quiz/younger_sibling.mp4"
            },
            
            # Colors SubLevel (sublevel_id: 5)
            {
                "question": "Bagaimana isyarat untuk warna 'Merah'?",
                "answer": "Sentuh bibir dengan telunjuk kemudian gerakkan ke bawah",
                "dictionary_id": 19, # Kamus: Merah
                "sublevel_id": 5,    # SubLevel: Colors
                "video_url": "https://example.com/quiz/red.mp4"
            },
            {
                "question": "Tunjukkan isyarat warna 'Biru'",
                "answer": "Goyangkan tangan dengan huruf B di samping tubuh",
                "dictionary_id": 20, # Kamus: Biru
                "sublevel_id": 5,    # SubLevel: Colors
                "video_url": "https://example.com/quiz/blue.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Hijau'",
                "answer": "Goyangkan tangan dengan huruf G di samping tubuh",
                "dictionary_id": 21, # Kamus: Hijau
                "sublevel_id": 5,    # SubLevel: Colors
                "video_url": "https://example.com/quiz/green.mp4"
            },
            {
                "question": "Bagaimana cara mengisyaratkan 'Kuning'?",
                "answer": "Goyangkan tangan dengan huruf Y di samping tubuh",
                "dictionary_id": 22, # Kamus: Kuning
                "sublevel_id": 5,    # SubLevel: Colors
                "video_url": "https://example.com/quiz/yellow.mp4"
            },
            
            # Animals SubLevel (sublevel_id: 6)
            {
                "question": "Bagaimana isyarat untuk 'Kucing'?",
                "answer": "Cubit pipi dengan telunjuk dan ibu jari beberapa kali",
                "dictionary_id": 23, # Kamus: Kucing
                "sublevel_id": 6,    # SubLevel: Animals
                "video_url": "https://example.com/quiz/cat.mp4"
            },
            {
                "question": "Tunjukkan isyarat 'Anjing'",
                "answer": "Tepuk paha kemudian jentikkan jari",
                "dictionary_id": 24, # Kamus: Anjing
                "sublevel_id": 6,    # SubLevel: Animals
                "video_url": "https://example.com/quiz/dog.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Burung'",
                "answer": "Buka tutup telunjuk dan ibu jari di dekat mulut",
                "dictionary_id": 25, # Kamus: Burung
                "sublevel_id": 6,    # SubLevel: Animals
                "video_url": "https://example.com/quiz/bird.mp4"
            },
            
            # Food & Drinks SubLevel (sublevel_id: 7)
            {
                "question": "Bagaimana isyarat 'Makan'?",
                "answer": "Gerakkan tangan ke mulut seolah memasukkan makanan",
                "dictionary_id": 26, # Kamus: Makan
                "sublevel_id": 7,    # SubLevel: Food & Drinks
                "video_url": "https://example.com/quiz/eat.mp4"
            },
            {
                "question": "Tunjukkan isyarat 'Minum'",
                "answer": "Angkat tangan seperti memegang gelas ke mulut",
                "dictionary_id": 27, # Kamus: Minum
                "sublevel_id": 7,    # SubLevel: Food & Drinks
                "video_url": "https://example.com/quiz/drink.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Nasi'",
                "answer": "Gerakkan tangan seolah mengambil nasi dengan sendok",
                "dictionary_id": 28, # Kamus: Nasi
                "sublevel_id": 7,    # SubLevel: Food & Drinks
                "video_url": "https://example.com/quiz/rice.mp4"
            },
            {
                "question": "Bagaimana cara mengisyaratkan 'Air'?",
                "answer": "Sentuh dagu dengan huruf W kemudian gerakkan ke bawah",
                "dictionary_id": 29, # Kamus: Air
                "sublevel_id": 7,    # SubLevel: Food & Drinks
                "video_url": "https://example.com/quiz/water.mp4"
            },
            
            # Weather SubLevel (sublevel_id: 8)
            {
                "question": "Bagaimana isyarat 'Hujan'?",
                "answer": "Gerakkan kedua tangan dari atas ke bawah seperti air jatuh",
                "dictionary_id": 30, # Kamus: Hujan
                "sublevel_id": 8,    # SubLevel: Weather
                "video_url": "https://example.com/quiz/rain.mp4"
            },
            {
                "question": "Tunjukkan isyarat 'Panas'",
                "answer": "Bentuk cakar di dekat mulut kemudian buka dengan ekspresi panas",
                "dictionary_id": 31, # Kamus: Panas
                "sublevel_id": 8,    # SubLevel: Weather
                "video_url": "https://example.com/quiz/hot.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Dingin'",
                "answer": "Kedua tangan mengepal bergetar di depan tubuh",
                "dictionary_id": 32, # Kamus: Dingin
                "sublevel_id": 8,    # SubLevel: Weather
                "video_url": "https://example.com/quiz/cold.mp4"
            },
            
            # Time Concepts SubLevel (sublevel_id: 9)
            {
                "question": "Bagaimana isyarat 'Hari'?",
                "answer": "Lingkarkan lengan dari timur ke barat meniru matahari",
                "dictionary_id": 33, # Kamus: Hari
                "sublevel_id": 9,    # SubLevel: Time Concepts
                "video_url": "https://example.com/quiz/day.mp4"
            },
            {
                "question": "Tunjukkan isyarat 'Malam'",
                "answer": "Lengkungkan tangan di atas tangan lain seperti matahari tenggelam",
                "dictionary_id": 34, # Kamus: Malam
                "sublevel_id": 9,    # SubLevel: Time Concepts
                "video_url": "https://example.com/quiz/night.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Besok'",
                "answer": "Gerakkan tangan ke depan dengan huruf A",
                "dictionary_id": 35, # Kamus: Besok
                "sublevel_id": 9,    # SubLevel: Time Concepts
                "video_url": "https://example.com/quiz/tomorrow.mp4"
            },
            
            # Complex Grammar SubLevel (sublevel_id: 10) - Tanpa kamus reference
            {
                "question": "Bagaimana struktur kalimat tanya dalam bahasa isyarat?",
                "answer": "Gunakan ekspresi wajah bertanya dan akhiri dengan tanda tanya",
                "dictionary_id": None,
                "sublevel_id": 10,   # SubLevel: Complex Grammar
                "video_url": "https://example.com/quiz/question_structure.mp4"
            },
            {
                "question": "Jelaskan penggunaan ruang dalam bahasa isyarat",
                "answer": "Ruang digunakan untuk menunjukkan hubungan antara objek dan orang",
                "dictionary_id": None,
                "sublevel_id": 10,   # SubLevel: Complex Grammar
                "video_url": "https://example.com/quiz/spatial_grammar.mp4"
            },
            {
                "question": "Bagaimana cara menggunakan classifier dalam bahasa isyarat?",
                "answer": "Classifier digunakan untuk menggambarkan bentuk, ukuran, dan gerakan objek",
                "dictionary_id": None,
                "sublevel_id": 10,   # SubLevel: Complex Grammar
                "video_url": "https://example.com/quiz/classifiers.mp4"
            },
            {
                "question": "Jelaskan pentingnya ekspresi wajah dalam bahasa isyarat",
                "answer": "Ekspresi wajah menunjukkan intonasi, emosi, dan struktur gramatikal",
                "dictionary_id": None,
                "sublevel_id": 10,   # SubLevel: Complex Grammar
                "video_url": "https://example.com/quiz/facial_expressions.mp4"
            }
        ]
        
        created_count = 0
        for data in soal_data:
            # Check if soal already exists
            existing = self.db.query(Soal).filter(
                Soal.question == data["question"],
                Soal.sublevel_id == data["sublevel_id"]
            ).first()
            
            if not existing:
                soal = Soal(**data)
                self.db.add(soal)
                created_count += 1
                print(f"  ✅ Created soal: {data['question'][:50]}... (SubLevel: {data['sublevel_id']})")
            else:
                print(f"  ⚠️ Soal already exists: {data['question'][:30]}...")
        
        self.db.commit()
        print(f"✅ Soal seeding completed. Created {created_count} questions.")

# Helper functions for quick setup
def seed_complete_data(db: Session):
    """Run complete seeder"""
    seeder = CompleteSeeder()
    seeder.db = db
    seeder.run()