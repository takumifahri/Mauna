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

class SoalSeeder(BaseSeeder):
    """Seed Soal dengan auto-assignment foreign keys"""
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        """Run soal seeding process"""
        try:
            print("🌱 Starting Soal seeding with auto foreign key assignment...")
            
            # Seed all soal by category
            self.seed_soal()
            
            print("✅ Soal seeding finished successfully!")
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Soal seeding failed: {e}")
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
            
            # Complex Grammar SubLevel (sublevel_id: 10) - Gunakan dictionary_id 1 sebagai default
            {
                "question": "Bagaimana struktur kalimat tanya dalam bahasa isyarat?",
                "answer": "Gunakan ekspresi wajah bertanya dan akhiri dengan tanda tanya",
                "dictionary_id": 1,  # Default ke dictionary_id 1 (A)
                "sublevel_id": 10,   # SubLevel: Complex Grammar
                "video_url": "https://example.com/quiz/question_structure.mp4"
            },
            {
                "question": "Jelaskan penggunaan ruang dalam bahasa isyarat",
                "answer": "Ruang digunakan untuk menunjukkan hubungan antara objek dan orang",
                "dictionary_id": 1,  # Default ke dictionary_id 1 (A)
                "sublevel_id": 10,   # SubLevel: Complex Grammar
                "video_url": "https://example.com/quiz/spatial_grammar.mp4"
            },
            {
                "question": "Bagaimana cara menggunakan classifier dalam bahasa isyarat?",
                "answer": "Classifier digunakan untuk menggambarkan bentuk, ukuran, dan gerakan objek",
                "dictionary_id": 1,  # Default ke dictionary_id 1 (A)
                "sublevel_id": 10,   # SubLevel: Complex Grammar
                "video_url": "https://example.com/quiz/classifiers.mp4"
            },
            {
                "question": "Jelaskan pentingnya ekspresi wajah dalam bahasa isyarat",
                "answer": "Ekspresi wajah menunjukkan intonasi, emosi, dan struktur gramatikal",
                "dictionary_id": 1,  # Default ke dictionary_id 1 (A)
                "sublevel_id": 10,   # SubLevel: Complex Grammar
                "video_url": "https://example.com/quiz/facial_expressions.mp4"
            }
        ]

        for data in soal_data:
            # Check if soal already exists
            existing = self.db.query(Soal).filter(Soal.question == data["question"]).first()
            if existing:
                print(f"  ⚠️ Soal already exists: {data['question'][:50]}...")
                continue

            # Create new soal
            soal = Soal(**data)
            self.db.add(soal)
            print(f"  ✅ Created soal: {data['question'][:50]}...")

        self.db.commit()
        print("  💾 Soal data committed to database")
