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
            self.seed_alphabet_soal()
            self.seed_numbers_soal()
            self.seed_greetings_soal()
            self.seed_family_soal()
            self.seed_colors_soal()
            self.seed_animals_soal()
            self.seed_food_soal()
            self.seed_weather_soal()
            self.seed_time_soal()
            self.seed_grammar_soal()
            
            print("✅ Soal seeding finished successfully!")
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Soal seeding failed: {e}")

    def get_sublevel_by_name(self, sublevel_name: str, level_name: str = None):
        """Get sublevel by name and optional level name"""
        query = self.db.query(SubLevel).filter(SubLevel.name == sublevel_name)
        
        if level_name:
            query = query.join(Level).filter(Level.name == level_name)
        
        return query.first()

    def get_kamus_by_word(self, word_text: str):
        """Get kamus by word text"""
        return self.db.query(Kamus).filter(Kamus.word_text == word_text).first()

    def create_soal_if_not_exists(self, question: str, answer: str, kamus_word: str = None, 
                                 sublevel_name: str = None, level_name: str = None, 
                                 video_url: str = None, image_url: str = None):
        """Create soal if it doesn't exist with auto foreign key assignment"""
        
        # Check if soal already exists
        existing = self.db.query(Soal).filter(Soal.question == question).first()
        if existing:
            print(f"  ⚠️ Soal already exists: {question[:50]}...")
            return existing

        # Get sublevel
        if not sublevel_name:
            print(f"  ❌ SubLevel name is required")
            return None
            
        sublevel = self.get_sublevel_by_name(sublevel_name, level_name)
        if not sublevel:
            print(f"  ❌ SubLevel '{sublevel_name}' not found")
            return None

        # Get kamus (optional)
        kamus = None
        if kamus_word:
            kamus = self.get_kamus_by_word(kamus_word)
            if not kamus:
                print(f"  ❌ Kamus '{kamus_word}' not found")

        # Create soal
        soal_data = {
            "question": question,
            "answer": answer,
            "sublevel_id": sublevel.id,
            "dictionary_id": kamus.id if kamus else None,
            "video_url": video_url,
            "image_url": image_url
        }

        soal = Soal(**soal_data)
        self.db.add(soal)
        
        kamus_info = f" (Kamus: {kamus_word})" if kamus_word else ""
        print(f"  ✅ Created soal: {question[:50]}... → {sublevel_name}{kamus_info}")
        
        return soal

    def seed_alphabet_soal(self):
        """Seed soal untuk Alphabet A-E"""
        print("🔤 Seeding Alphabet Soal...")
        
        alphabet_soal = [
            {
                "question": "Bagaimana cara membuat isyarat untuk huruf 'A'?",
                "answer": "Kepalkan tangan dengan ibu jari di samping",
                "kamus_word": "A",
                "sublevel_name": "Alphabet A-E",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/letter_A.mp4"
            },
            {
                "question": "Tunjukkan isyarat untuk huruf 'B'",
                "answer": "Tangan terbuka dengan jari-jari rapat dan ibu jari menekuk",
                "kamus_word": "B",
                "sublevel_name": "Alphabet A-E",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/letter_B.mp4"
            },
            {
                "question": "Bagaimana isyarat huruf 'C'?",
                "answer": "Bentuk tangan seperti huruf C",
                "kamus_word": "C",
                "sublevel_name": "Alphabet A-E",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/letter_C.mp4"
            },
            {
                "question": "Praktikkan isyarat huruf 'D'",
                "answer": "Telunjuk tegak, jari lain menekuk, ibu jari menyentuh jari tengah",
                "kamus_word": "D",
                "sublevel_name": "Alphabet A-E",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/letter_D.mp4"
            },
            {
                "question": "Tunjukkan cara membuat isyarat huruf 'E'",
                "answer": "Semua jari menekuk menyentuh ibu jari",
                "kamus_word": "E",
                "sublevel_name": "Alphabet A-E",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/letter_E.mp4"
            }
        ]
        
        for soal_data in alphabet_soal:
            self.create_soal_if_not_exists(**soal_data)
        
        self.db.commit()

    def seed_numbers_soal(self):
        """Seed soal untuk Numbers 1-5"""
        print("🔢 Seeding Numbers Soal...")
        
        numbers_soal = [
            {
                "question": "Bagaimana cara menunjukkan angka '1' dalam bahasa isyarat?",
                "answer": "Telunjuk tegak ke atas",
                "kamus_word": "1",
                "sublevel_name": "Numbers 1-5",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/number_1.mp4"
            },
            {
                "question": "Praktikkan isyarat untuk angka '2'",
                "answer": "Telunjuk dan jari tengah tegak",
                "kamus_word": "2",
                "sublevel_name": "Numbers 1-5",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/number_2.mp4"
            },
            {
                "question": "Tunjukkan isyarat angka '3'",
                "answer": "Telunjuk, jari tengah, dan jari manis tegak",
                "kamus_word": "3",
                "sublevel_name": "Numbers 1-5",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/number_3.mp4"
            },
            {
                "question": "Bagaimana cara membuat isyarat angka '4'?",
                "answer": "Empat jari tegak, ibu jari menekuk",
                "kamus_word": "4",
                "sublevel_name": "Numbers 1-5",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/number_4.mp4"
            },
            {
                "question": "Praktikkan isyarat untuk angka '5'",
                "answer": "Semua jari terbuka dan tegak",
                "kamus_word": "5",
                "sublevel_name": "Numbers 1-5",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/number_5.mp4"
            }
        ]
        
        for soal_data in numbers_soal:
            self.create_soal_if_not_exists(**soal_data)
        
        self.db.commit()

    def seed_greetings_soal(self):
        """Seed soal untuk Basic Greetings"""
        print("👋 Seeding Greetings Soal...")
        
        greetings_soal = [
            {
                "question": "Bagaimana cara mengucapkan 'Halo' dalam bahasa isyarat?",
                "answer": "Lambaikan tangan dengan telapak terbuka",
                "kamus_word": "Halo",
                "sublevel_name": "Basic Greetings",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/hello.mp4"
            },
            {
                "question": "Tunjukkan isyarat untuk 'Selamat Pagi'",
                "answer": "Gabungkan isyarat 'baik' dan 'pagi'",
                "kamus_word": "Selamat Pagi",
                "sublevel_name": "Basic Greetings",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/good_morning.mp4"
            },
            {
                "question": "Bagaimana cara mengucapkan 'Terima Kasih'?",
                "answer": "Sentuh dagu dengan ujung jari kemudian gerakkan ke depan",
                "kamus_word": "Terima Kasih",
                "sublevel_name": "Basic Greetings",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/thank_you.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Maaf'",
                "answer": "Kepalkan tangan dan gosokkan di dada dengan gerakan melingkar",
                "kamus_word": "Maaf",
                "sublevel_name": "Basic Greetings",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/sorry.mp4"
            }
        ]
        
        for soal_data in greetings_soal:
            self.create_soal_if_not_exists(**soal_data)
        
        self.db.commit()

    def seed_family_soal(self):
        """Seed soal untuk Family Members"""
        print("👨‍👩‍👧‍👦 Seeding Family Soal...")
        
        family_soal = [
            {
                "question": "Bagaimana cara mengatakan 'Ayah' dalam bahasa isyarat?",
                "answer": "Sentuh dahi dengan ibu jari tangan terbuka",
                "kamus_word": "Ayah",
                "sublevel_name": "Family Members",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/father.mp4"
            },
            {
                "question": "Tunjukkan isyarat untuk 'Ibu'",
                "answer": "Sentuh dagu dengan ibu jari tangan terbuka",
                "kamus_word": "Ibu",
                "sublevel_name": "Family Members",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/mother.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Kakak'",
                "answer": "Isyarat saudara dengan tangan naik ke atas",
                "kamus_word": "Kakak",
                "sublevel_name": "Family Members",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/older_sibling.mp4"
            },
            {
                "question": "Bagaimana cara mengisyaratkan 'Adik'?",
                "answer": "Isyarat saudara dengan tangan turun ke bawah",
                "kamus_word": "Adik",
                "sublevel_name": "Family Members",
                "level_name": "Beginner",
                "video_url": "https://example.com/quiz/younger_sibling.mp4"
            }
        ]
        
        for soal_data in family_soal:
            self.create_soal_if_not_exists(**soal_data)
        
        self.db.commit()

    def seed_colors_soal(self):
        """Seed soal untuk Colors"""
        print("🎨 Seeding Colors Soal...")
        
        colors_soal = [
            {
                "question": "Bagaimana isyarat untuk warna 'Merah'?",
                "answer": "Sentuh bibir dengan telunjuk kemudian gerakkan ke bawah",
                "kamus_word": "Merah",
                "sublevel_name": "Colors",
                "level_name": "Elementary",
                "video_url": "https://example.com/quiz/red.mp4"
            },
            {
                "question": "Tunjukkan isyarat warna 'Biru'",
                "answer": "Goyangkan tangan dengan huruf B di samping tubuh",
                "kamus_word": "Biru",
                "sublevel_name": "Colors",
                "level_name": "Elementary",
                "video_url": "https://example.com/quiz/blue.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Hijau'",
                "answer": "Goyangkan tangan dengan huruf G di samping tubuh",
                "kamus_word": "Hijau",
                "sublevel_name": "Colors",
                "level_name": "Elementary",
                "video_url": "https://example.com/quiz/green.mp4"
            },
            {
                "question": "Bagaimana cara mengisyaratkan 'Kuning'?",
                "answer": "Goyangkan tangan dengan huruf Y di samping tubuh",
                "kamus_word": "Kuning",
                "sublevel_name": "Colors",
                "level_name": "Elementary",
                "video_url": "https://example.com/quiz/yellow.mp4"
            }
        ]
        
        for soal_data in colors_soal:
            self.create_soal_if_not_exists(**soal_data)
        
        self.db.commit()

    def seed_animals_soal(self):
        """Seed soal untuk Animals"""
        print("🐱 Seeding Animals Soal...")
        
        animals_soal = [
            {
                "question": "Bagaimana isyarat untuk 'Kucing'?",
                "answer": "Cubit pipi dengan telunjuk dan ibu jari beberapa kali",
                "kamus_word": "Kucing",
                "sublevel_name": "Animals",
                "level_name": "Elementary",
                "video_url": "https://example.com/quiz/cat.mp4"
            },
            {
                "question": "Tunjukkan isyarat 'Anjing'",
                "answer": "Tepuk paha kemudian jentikkan jari",
                "kamus_word": "Anjing",
                "sublevel_name": "Animals",
                "level_name": "Elementary",
                "video_url": "https://example.com/quiz/dog.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Burung'",
                "answer": "Buka tutup telunjuk dan ibu jari di dekat mulut",
                "kamus_word": "Burung",
                "sublevel_name": "Animals",
                "level_name": "Elementary",
                "video_url": "https://example.com/quiz/bird.mp4"
            }
        ]
        
        for soal_data in animals_soal:
            self.create_soal_if_not_exists(**soal_data)
        
        self.db.commit()

    def seed_food_soal(self):
        """Seed soal untuk Food & Drinks"""
        print("🍽️ Seeding Food Soal...")
        
        food_soal = [
            {
                "question": "Bagaimana isyarat 'Makan'?",
                "answer": "Gerakkan tangan ke mulut seolah memasukkan makanan",
                "kamus_word": "Makan",
                "sublevel_name": "Food & Drinks",
                "level_name": "Elementary",
                "video_url": "https://example.com/quiz/eat.mp4"
            },
            {
                "question": "Tunjukkan isyarat 'Minum'",
                "answer": "Angkat tangan seperti memegang gelas ke mulut",
                "kamus_word": "Minum",
                "sublevel_name": "Food & Drinks",
                "level_name": "Elementary",
                "video_url": "https://example.com/quiz/drink.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Nasi'",
                "answer": "Gerakkan tangan seolah mengambil nasi dengan sendok",
                "kamus_word": "Nasi",
                "sublevel_name": "Food & Drinks",
                "level_name": "Elementary",
                "video_url": "https://example.com/quiz/rice.mp4"
            },
            {
                "question": "Bagaimana cara mengisyaratkan 'Air'?",
                "answer": "Sentuh dagu dengan huruf W kemudian gerakkan ke bawah",
                "kamus_word": "Air",
                "sublevel_name": "Food & Drinks",
                "level_name": "Elementary",
                "video_url": "https://example.com/quiz/water.mp4"
            }
        ]
        
        for soal_data in food_soal:
            self.create_soal_if_not_exists(**soal_data)
        
        self.db.commit()

    def seed_weather_soal(self):
        """Seed soal untuk Weather"""
        print("🌤️ Seeding Weather Soal...")
        
        weather_soal = [
            {
                "question": "Bagaimana isyarat 'Hujan'?",
                "answer": "Gerakkan kedua tangan dari atas ke bawah seperti air jatuh",
                "kamus_word": "Hujan",
                "sublevel_name": "Weather",
                "level_name": "Intermediate",
                "video_url": "https://example.com/quiz/rain.mp4"
            },
            {
                "question": "Tunjukkan isyarat 'Panas'",
                "answer": "Bentuk cakar di dekat mulut kemudian buka dengan ekspresi panas",
                "kamus_word": "Panas",
                "sublevel_name": "Weather",
                "level_name": "Intermediate",
                "video_url": "https://example.com/quiz/hot.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Dingin'",
                "answer": "Kedua tangan mengepal bergetar di depan tubuh",
                "kamus_word": "Dingin",
                "sublevel_name": "Weather",
                "level_name": "Intermediate",
                "video_url": "https://example.com/quiz/cold.mp4"
            }
        ]
        
        for soal_data in weather_soal:
            self.create_soal_if_not_exists(**soal_data)
        
        self.db.commit()

    def seed_time_soal(self):
        """Seed soal untuk Time Concepts"""
        print("⏰ Seeding Time Soal...")
        
        time_soal = [
            {
                "question": "Bagaimana isyarat 'Hari'?",
                "answer": "Lingkarkan lengan dari timur ke barat meniru matahari",
                "kamus_word": "Hari",
                "sublevel_name": "Time Concepts",
                "level_name": "Intermediate",
                "video_url": "https://example.com/quiz/day.mp4"
            },
            {
                "question": "Tunjukkan isyarat 'Malam'",
                "answer": "Lengkungkan tangan di atas tangan lain seperti matahari tenggelam",
                "kamus_word": "Malam",
                "sublevel_name": "Time Concepts",
                "level_name": "Intermediate",
                "video_url": "https://example.com/quiz/night.mp4"
            },
            {
                "question": "Praktikkan isyarat 'Besok'",
                "answer": "Gerakkan tangan ke depan dengan huruf A",
                "kamus_word": "Besok",
                "sublevel_name": "Time Concepts",
                "level_name": "Intermediate",
                "video_url": "https://example.com/quiz/tomorrow.mp4"
            }
        ]
        
        for soal_data in time_soal:
            self.create_soal_if_not_exists(**soal_data)
        
        self.db.commit()

    def seed_grammar_soal(self):
        """Seed soal untuk Complex Grammar (tanpa kamus reference)"""
        print("📖 Seeding Grammar Soal...")
        
        grammar_soal = [
            {
                "question": "Bagaimana struktur kalimat tanya dalam bahasa isyarat?",
                "answer": "Gunakan ekspresi wajah bertanya dan akhiri dengan tanda tanya",
                "kamus_word": None,  # Tidak ada kamus reference
                "sublevel_name": "Complex Grammar",
                "level_name": "Advanced",
                "video_url": "https://example.com/quiz/question_structure.mp4"
            },
            {
                "question": "Jelaskan penggunaan ruang dalam bahasa isyarat",
                "answer": "Ruang digunakan untuk menunjukkan hubungan antara objek dan orang",
                "kamus_word": None,
                "sublevel_name": "Complex Grammar",
                "level_name": "Advanced",
                "video_url": "https://example.com/quiz/spatial_grammar.mp4"
            },
            {
                "question": "Bagaimana cara menggunakan classifier dalam bahasa isyarat?",
                "answer": "Classifier digunakan untuk menggambarkan bentuk, ukuran, dan gerakan objek",
                "kamus_word": None,
                "sublevel_name": "Complex Grammar",
                "level_name": "Advanced",
                "video_url": "https://example.com/quiz/classifiers.mp4"
            },
            {
                "question": "Jelaskan pentingnya ekspresi wajah dalam bahasa isyarat",
                "answer": "Ekspresi wajah menunjukkan intonasi, emosi, dan struktur gramatikal",
                "kamus_word": None,
                "sublevel_name": "Complex Grammar",
                "level_name": "Advanced",
                "video_url": "https://example.com/quiz/facial_expressions.mp4"
            }
        ]
        
        for soal_data in grammar_soal:
            self.create_soal_if_not_exists(**soal_data)
        
        self.db.commit()

    def seed_custom_soal(self, soal_list: List[Dict[str, Any]]):
        """Seed custom soal list"""
        print("🔧 Seeding Custom Soal...")
        
        for soal_data in soal_list:
            self.create_soal_if_not_exists(**soal_data)
        
        self.db.commit()

# Helper functions untuk quick usage
def seed_soal_by_category(category: str):
    """Seed soal by specific category"""
    seeder = SoalSeeder()
    
    category_methods = {
        "alphabet": seeder.seed_alphabet_soal,
        "numbers": seeder.seed_numbers_soal,
        "greetings": seeder.seed_greetings_soal,
        "family": seeder.seed_family_soal,
        "colors": seeder.seed_colors_soal,
        "animals": seeder.seed_animals_soal,
        "food": seeder.seed_food_soal,
        "weather": seeder.seed_weather_soal,
        "time": seeder.seed_time_soal,
        "grammar": seeder.seed_grammar_soal
    }
    
    if category in category_methods:
        print(f"🎯 Seeding {category} soal...")
        category_methods[category]()
        print(f"✅ {category} soal seeding completed")
    else:
        print(f"❌ Category '{category}' not found")
        print(f"Available categories: {list(category_methods.keys())}")
    
    seeder.close()

def seed_all_soal():
    """Seed all soal categories"""
    seeder = SoalSeeder()
    seeder.run()
    seeder.close()

def add_custom_soal(question: str, answer: str, kamus_word: str = None,
                   sublevel_name: str = None, level_name: str = None,
                   video_url: str = None, image_url: str = None):
    """Add single custom soal"""
    seeder = SoalSeeder()
    
    result = seeder.create_soal_if_not_exists(
        question=question,
        answer=answer,
        kamus_word=kamus_word,
        sublevel_name=sublevel_name,
        level_name=level_name,
        video_url=video_url,
        image_url=image_url
    )
    
    seeder.db.commit()
    seeder.close()
    
    return result

# Example usage untuk manual testing
def example_usage():
    """Example of how to use the seeder"""
    
    # Seed all soal
    seed_all_soal()
    
    # Seed specific category
    seed_soal_by_category("alphabet")
    
    # Add custom soal
    add_custom_soal(
        question="Bagaimana cara mengisyaratkan 'Saya'?",
        answer="Tunjuk diri sendiri dengan telunjuk",
        kamus_word="Saya",  # Pastikan ada di kamus
        sublevel_name="Basic Greetings",
        level_name="Beginner",
        video_url="https://example.com/quiz/saya.mp4"
    )
    
    # Seed custom list
    custom_soal = [
        {
            "question": "Test question 1",
            "answer": "Test answer 1",
            "kamus_word": "Halo",
            "sublevel_name": "Basic Greetings",
            "level_name": "Beginner"
        },
        {
            "question": "Test question 2",
            "answer": "Test answer 2",
            "kamus_word": None,  # No kamus reference
            "sublevel_name": "Complex Grammar",
            "level_name": "Advanced"
        }
    ]
    
    seeder = SoalSeeder()
    seeder.seed_custom_soal(custom_soal)
    seeder.close()