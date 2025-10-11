# src/database/seed/soal_seeder.py

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import random

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
    from ..seeder import BaseSeeder

class SoalSeeder(BaseSeeder):
    """Seed Soal dengan auto-assignment foreign keys"""

    def __init__(self):
        super().__init__()

    def run(self):
        """Run soal seeding process"""
        try:
            print("🌱 Starting Soal seeding with auto foreign key assignment...")
            
            self.seed_soal()
            
            print("✅ Soal seeding finished successfully!")
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Soal seeding failed: {e}")

    def seed_soal(self):
        """Seed Soal data dengan format esai singkat"""
        print("❓ Seeding Soal...")
        
        soal_data = []

        # --- Sublevel 1: Alphabet A-E (sublevel_id: 1) ---
        sublevel_id_1 = 1
        soal_data.extend([
            # A
            {"question": "Bagaimana cara membuat isyarat untuk huruf 'A'?", "answer": "Kepalkan tangan dengan ibu jari di samping", "dictionary_id": 1, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/letter_A.mp4"},
            {"question": "Jelaskan isyarat huruf 'A'!", "answer": "Tangan dikepalkan dengan ibu jari di samping", "dictionary_id": 1, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/video/A.mp4"},
            # B
            {"question": "Tunjukkan isyarat untuk huruf 'B'", "answer": "Tangan terbuka dengan jari-jari rapat dan ibu jari menekuk", "dictionary_id": 2, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/letter_B.mp4"},
            {"question": "Jelaskan bagaimana isyarat huruf 'B' dibuat?", "answer": "Tangan terbuka dengan jari-jari rapat dan ibu jari menekuk", "dictionary_id": 2, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/video/B.mp4"},
            # C
            {"question": "Bagaimana isyarat huruf 'C'?", "answer": "Bentuk tangan seperti huruf C", "dictionary_id": 3, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/letter_C.mp4"},
            {"question": "Tuliskan deskripsi isyarat huruf 'C'!", "answer": "Bentuk tangan seperti huruf C", "dictionary_id": 3, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/video/C.mp4"},
            # D
            {"question": "Praktikkan isyarat huruf 'D'", "answer": "Telunjuk tegak, jari lain menekuk, ibu jari menyentuh jari tengah", "dictionary_id": 4, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/letter_D.mp4"},
            {"question": "Jelaskan isyarat huruf 'D'", "answer": "Telunjuk tegak, jari lain menekuk, ibu jari menyentuh jari tengah", "dictionary_id": 4, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/video/D.mp4"},
            # E
            {"question": "Tunjukkan cara membuat isyarat huruf 'E'", "answer": "Semua jari menekuk menyentuh ibu jari", "dictionary_id": 5, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/letter_E.mp4"},
            {"question": "Bagaimana isyarat huruf 'E' dibuat?", "answer": "Semua jari menekuk menyentuh ibu jari", "dictionary_id": 5, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/video/E.mp4"},
            # Tambahan
            {"question": "Deskripsikan isyarat tangan untuk 'A'.", "answer": "Kepalkan tangan dengan ibu jari di samping", "dictionary_id": 1, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/video/A_alt.mp4"},
            {"question": "Tuliskan langkah-langkah membuat isyarat 'B'.", "answer": "Tangan terbuka, jari-jari rapat, ibu jari ditekuk", "dictionary_id": 2, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/video/B_alt.mp4"},
            {"question": "Jelaskan isyarat tangan 'C'.", "answer": "Bentuk tangan menyerupai huruf C", "dictionary_id": 3, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/video/C_alt.mp4"},
            {"question": "Bagaimana cara membuat isyarat 'D'?", "answer": "Telunjuk tegak lurus, jari lain ditekuk", "dictionary_id": 4, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/video/D_alt.mp4"},
            {"question": "Deskripsikan isyarat untuk 'E'.", "answer": "Jari-jari ditekuk ke arah ibu jari", "dictionary_id": 5, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/video/E_alt.mp4"},
            {"question": "Isyarat 'A' adalah...", "answer": "Kepalan tangan", "dictionary_id": 1, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/letter_A_quiz.mp4"},
            {"question": "Bagaimana isyarat 'B'?", "answer": "Tangan terbuka dan jari lurus", "dictionary_id": 2, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/letter_B_quiz.mp4"},
            {"question": "Tuliskan cara membuat isyarat 'C'.", "answer": "Bentuk tangan melengkung", "dictionary_id": 3, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/letter_C_quiz.mp4"},
            {"question": "Isyarat 'D' adalah...", "answer": "Jari telunjuk ke atas", "dictionary_id": 4, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/letter_D_quiz.mp4"},
            {"question": "Tuliskan deskripsi isyarat 'E'.", "answer": "Jari-jari ditekuk ke dalam", "dictionary_id": 5, "sublevel_id": sublevel_id_1, "video_url": "https://example.com/quiz/letter_E_quiz.mp4"},
        ])

        # --- Sublevel 2: Numbers 1-5 (sublevel_id: 2) ---
        sublevel_id_2 = 2
        soal_data.extend([
            {"question": "Bagaimana cara menunjukkan angka '1' dalam bahasa isyarat?", "answer": "Telunjuk tegak ke atas", "dictionary_id": 6, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_1.mp4"},
            {"question": "Jelaskan isyarat untuk angka '1'.", "answer": "Jari telunjuk lurus ke atas", "dictionary_id": 6, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/video/1.mp4"},
            {"question": "Praktikkan isyarat untuk angka '2'", "answer": "Telunjuk dan jari tengah tegak", "dictionary_id": 7, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_2.mp4"},
            {"question": "Tuliskan deskripsi isyarat angka '2'", "answer": "Jari telunjuk dan jari tengah lurus ke atas", "dictionary_id": 7, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/video/2.mp4"},
            {"question": "Tunjukkan isyarat angka '3'", "answer": "Telunjuk, jari tengah, dan jari manis tegak", "dictionary_id": 8, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_3.mp4"},
            {"question": "Jelaskan isyarat untuk angka '3'.", "answer": "Tiga jari teratas lurus ke atas", "dictionary_id": 8, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/video/3.mp4"},
            {"question": "Bagaimana cara membuat isyarat angka '4'?", "answer": "Empat jari tegak, ibu jari menekuk", "dictionary_id": 9, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_4.mp4"},
            {"question": "Tuliskan deskripsi isyarat angka '4'", "answer": "Empat jari lurus ke atas, ibu jari ditekuk", "dictionary_id": 9, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/video/4.mp4"},
            {"question": "Praktikkan isyarat untuk angka '5'", "answer": "Semua jari terbuka dan tegak", "dictionary_id": 10, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_5.mp4"},
            {"question": "Jelaskan isyarat untuk angka '5'.", "answer": "Tangan terbuka dengan semua jari lurus ke atas", "dictionary_id": 10, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/video/5.mp4"},
            {"question": "Bagaimana isyarat '1' dibuat?", "answer": "Satu jari telunjuk tegak", "dictionary_id": 6, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_1_alt.mp4"},
            {"question": "Deskripsikan isyarat '2'.", "answer": "Dua jari (telunjuk dan tengah) tegak", "dictionary_id": 7, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_2_alt.mp4"},
            {"question": "Isyarat '3' menggunakan berapa jari?", "answer": "Tiga jari", "dictionary_id": 8, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_3_alt.mp4"},
            {"question": "Isyarat '4' dibuat dengan jari apa saja?", "answer": "Empat jari lurus, ibu jari ditekuk", "dictionary_id": 9, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_4_alt.mp4"},
            {"question": "Bagaimana isyarat untuk '5'?", "answer": "Lima jari lurus", "dictionary_id": 10, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_5_alt.mp4"},
            {"question": "Isyarat '1' digambarkan dengan...", "answer": "Jari telunjuk ke atas", "dictionary_id": 6, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_1_quiz.mp4"},
            {"question": "Isyarat '2' digambarkan dengan...", "answer": "Jari telunjuk dan tengah ke atas", "dictionary_id": 7, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_2_quiz.mp4"},
            {"question": "Isyarat '3' digambarkan dengan...", "answer": "Tiga jari teratas ke atas", "dictionary_id": 8, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_3_quiz.mp4"},
            {"question": "Isyarat '4' digambarkan dengan...", "answer": "Empat jari lurus", "dictionary_id": 9, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_4_quiz.mp4"},
            {"question": "Isyarat '5' digambarkan dengan...", "answer": "Tangan terbuka", "dictionary_id": 10, "sublevel_id": sublevel_id_2, "video_url": "https://example.com/quiz/number_5_quiz.mp4"},
        ])
        
        # --- Sublevel 3: Basic Greetings (sublevel_id: 3) ---
        sublevel_id_3 = 3
        soal_data.extend([
            {"question": "Bagaimana cara mengucapkan 'Halo' dalam bahasa isyarat?", "answer": "Lambaikan tangan dengan telapak terbuka", "dictionary_id": 11, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/hello.mp4"},
            {"question": "Jelaskan isyarat untuk 'Selamat Pagi'", "answer": "Gabungkan isyarat 'baik' dan 'pagi'", "dictionary_id": 12, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/good_morning.mp4"},
            {"question": "Bagaimana cara mengucapkan 'Terima Kasih'?", "answer": "Sentuh dagu dengan ujung jari kemudian gerakkan ke depan", "dictionary_id": 13, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/thank_you.mp4"},
            {"question": "Praktikkan isyarat 'Maaf'", "answer": "Kepalkan tangan dan gosokkan di dada dengan gerakan melingkar", "dictionary_id": 14, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/sorry.mp4"},
            {"question": "Isyarat 'Halo' digambarkan dengan gerakan...", "answer": "Melambaikan tangan", "dictionary_id": 11, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/video/hello.mp4"},
            {"question": "Isyarat 'Selamat Pagi' terdiri dari dua isyarat, yaitu...", "answer": "Baik dan Pagi", "dictionary_id": 12, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/video/good_morning.mp4"},
            {"question": "Isyarat 'Terima Kasih' menggunakan gerakan tangan dari...", "answer": "Dagu ke depan", "dictionary_id": 13, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/video/thank_you.mp4"},
            {"question": "Isyarat 'Maaf' dibuat dengan gerakan...", "answer": "Menggosok kepalan tangan di dada", "dictionary_id": 14, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/video/sorry.mp4"},
            {"question": "Jelaskan isyarat 'Halo'.", "answer": "Lambaikan tangan terbuka", "dictionary_id": 11, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/video/hello_alt.mp4"},
            {"question": "Bagaimana isyarat 'Selamat Pagi'?", "answer": "Kombinasi isyarat 'baik' dan 'pagi'", "dictionary_id": 12, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/video/good_morning_alt.mp4"},
            {"question": "Deskripsikan isyarat 'Terima Kasih'.", "answer": "Gerakan jari dari dagu ke depan", "dictionary_id": 13, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/video/thank_you_alt.mp4"},
            {"question": "Jelaskan isyarat 'Maaf'.", "answer": "Kepalan tangan digosok melingkar di dada", "dictionary_id": 14, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/video/sorry_alt.mp4"},
            {"question": "Tuliskan cara membuat isyarat 'Halo'.", "answer": "Lambaikan tangan", "dictionary_id": 11, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/hello_quiz.mp4"},
            {"question": "Bagaimana isyarat 'Terima Kasih'?", "answer": "Jari dari dagu ke depan", "dictionary_id": 13, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/thank_you_quiz.mp4"},
            {"question": "Tuliskan cara membuat isyarat 'Maaf'.", "answer": "Tangan mengepal di dada", "dictionary_id": 14, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/sorry_quiz.mp4"},
            {"question": "Jelaskan isyarat 'Selamat Pagi'.", "answer": "Isyarat 'baik' dan isyarat 'pagi'", "dictionary_id": 12, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/good_morning_quiz.mp4"},
            {"question": "Isyarat tangan 'Halo' adalah...", "answer": "Melambaikan tangan", "dictionary_id": 11, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/hello_quiz2.mp4"},
            {"question": "Isyarat 'Terima Kasih' dibuat dengan jari...", "answer": "Menyentuh dagu", "dictionary_id": 13, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/thank_you_quiz2.mp4"},
            {"question": "Isyarat 'Maaf' dibuat dengan gerakan tangan di...", "answer": "Depan dada", "dictionary_id": 14, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/sorry_quiz2.mp4"},
            {"question": "Isyarat 'Selamat Pagi' dibuat dengan dua kata.", "answer": "Ya", "dictionary_id": 12, "sublevel_id": sublevel_id_3, "video_url": "https://example.com/quiz/good_morning_quiz2.mp4"},
        ])
        
        # --- Sublevel 4: Family Members (sublevel_id: 4) ---
        sublevel_id_4 = 4
        soal_data.extend([
            {"question": "Bagaimana cara mengatakan 'Ayah' dalam bahasa isyarat?", "answer": "Sentuh dahi dengan ibu jari tangan terbuka", "dictionary_id": 15, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/father.mp4"},
            {"question": "Isyarat ini berarti siapa? (video: Ayah)", "answer": "Ayah", "dictionary_id": 15, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/video/father.mp4"},
            {"question": "Tunjukkan isyarat untuk 'Ibu'", "answer": "Sentuh dagu dengan ibu jari tangan terbuka", "dictionary_id": 16, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/mother.mp4"},
            {"question": "Isyarat ini berarti siapa? (video: Ibu)", "answer": "Ibu", "dictionary_id": 16, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/video/mother.mp4"},
            {"question": "Praktikkan isyarat 'Kakak'", "answer": "Isyarat saudara dengan tangan naik ke atas", "dictionary_id": 17, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/older_sibling.mp4"},
            {"question": "Isyarat ini berarti siapa? (video: Kakak)", "answer": "Kakak", "dictionary_id": 17, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/video/older_sibling.mp4"},
            {"question": "Bagaimana cara mengisyaratkan 'Adik'?", "answer": "Isyarat saudara dengan tangan turun ke bawah", "dictionary_id": 18, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/younger_sibling.mp4"},
            {"question": "Isyarat ini berarti siapa? (video: Adik)", "answer": "Adik", "dictionary_id": 18, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/video/younger_sibling.mp4"},
            {"question": "Jelaskan isyarat 'Ayah'.", "answer": "Sentuh dahi dengan ibu jari", "dictionary_id": 15, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/father_alt.mp4"},
            {"question": "Jelaskan isyarat 'Ibu'.", "answer": "Sentuh dagu dengan ibu jari", "dictionary_id": 16, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/mother_alt.mp4"},
            {"question": "Bagaimana isyarat 'Kakak'?", "answer": "Gerakan tangan saudara ke atas", "dictionary_id": 17, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/older_sibling_alt.mp4"},
            {"question": "Bagaimana isyarat 'Adik'?", "answer": "Gerakan tangan saudara ke bawah", "dictionary_id": 18, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/younger_sibling_alt.mp4"},
            {"question": "Isyarat 'Ayah' menggunakan tangan di...", "answer": "Dahi", "dictionary_id": 15, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/video/father_alt2.mp4"},
            {"question": "Isyarat 'Ibu' menggunakan tangan di...", "answer": "Dagu", "dictionary_id": 16, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/video/mother_alt2.mp4"},
            {"question": "Gerakan isyarat 'Kakak' menunjukkan...", "answer": "Saudara yang lebih tua", "dictionary_id": 17, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/video/older_sibling_alt2.mp4"},
            {"question": "Gerakan isyarat 'Adik' menunjukkan...", "answer": "Saudara yang lebih muda", "dictionary_id": 18, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/video/younger_sibling_alt2.mp4"},
            {"question": "Tebak isyarat ini (video: Ayah)", "answer": "Ayah", "dictionary_id": 15, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/video/father_quiz.mp4"},
            {"question": "Tebak isyarat ini (video: Adik)", "answer": "Adik", "dictionary_id": 18, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/video/younger_sibling_quiz.mp4"},
            {"question": "Isyarat untuk saudara yang lebih tua adalah...", "answer": "Kakak", "dictionary_id": 17, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/older_sibling_quiz2.mp4"},
            {"question": "Isyarat untuk saudara yang lebih muda adalah...", "answer": "Adik", "dictionary_id": 18, "sublevel_id": sublevel_id_4, "video_url": "https://example.com/quiz/younger_sibling_quiz2.mp4"},
        ])
        
        # --- Sublevel 5: Colors (sublevel_id: 5) ---
        sublevel_id_5 = 5
        soal_data.extend([
            {"question": "Bagaimana isyarat untuk warna 'Merah'?", "answer": "Sentuh bibir dengan telunjuk kemudian gerakkan ke bawah", "dictionary_id": 19, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/red.mp4"},
            {"question": "Isyarat ini berarti warna apa? (video: Merah)", "answer": "Merah", "dictionary_id": 19, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/video/red.mp4"},
            {"question": "Tunjukkan isyarat warna 'Biru'", "answer": "Goyangkan tangan dengan huruf B di samping tubuh", "dictionary_id": 20, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/blue.mp4"},
            {"question": "Isyarat ini berarti warna apa? (video: Biru)", "answer": "Biru", "dictionary_id": 20, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/video/blue.mp4"},
            {"question": "Praktikkan isyarat 'Hijau'", "answer": "Goyangkan tangan dengan huruf G di samping tubuh", "dictionary_id": 21, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/green.mp4"},
            {"question": "Isyarat ini berarti warna apa? (video: Hijau)", "answer": "Hijau", "dictionary_id": 21, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/video/green.mp4"},
            {"question": "Bagaimana cara mengisyaratkan 'Kuning'?", "answer": "Goyangkan tangan dengan huruf Y di samping tubuh", "dictionary_id": 22, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/yellow.mp4"},
            {"question": "Isyarat ini berarti warna apa? (video: Kuning)", "answer": "Kuning", "dictionary_id": 22, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/video/yellow.mp4"},
            {"question": "Jelaskan isyarat 'Merah'.", "answer": "Sentuh bibir dengan telunjuk dan gerakkan ke bawah", "dictionary_id": 19, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/red_alt.mp4"},
            {"question": "Isyarat 'Biru' menggunakan bentuk tangan...", "answer": "Huruf B", "dictionary_id": 20, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/blue_alt.mp4"},
            {"question": "Isyarat 'Hijau' menggunakan bentuk tangan...", "answer": "Huruf G", "dictionary_id": 21, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/green_alt.mp4"},
            {"question": "Isyarat 'Kuning' menggunakan bentuk tangan...", "answer": "Huruf Y", "dictionary_id": 22, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/yellow_alt.mp4"},
            {"question": "Tebak warna dari isyarat (video: Merah)", "answer": "Merah", "dictionary_id": 19, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/video/red_quiz.mp4"},
            {"question": "Tebak warna dari isyarat (video: Biru)", "answer": "Biru", "dictionary_id": 20, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/video/blue_quiz.mp4"},
            {"question": "Tebak warna dari isyarat (video: Hijau)", "answer": "Hijau", "dictionary_id": 21, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/video/green_quiz.mp4"},
            {"question": "Tebak warna dari isyarat (video: Kuning)", "answer": "Kuning", "dictionary_id": 22, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/video/yellow_quiz.mp4"},
            {"question": "Untuk mengisyaratkan 'Biru', tangan digoyangkan di...", "answer": "Samping tubuh", "dictionary_id": 20, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/video/blue_alt2.mp4"},
            {"question": "Isyarat 'Merah' melibatkan...", "answer": "Bibir dan tangan", "dictionary_id": 19, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/video/red_alt2.mp4"},
            {"question": "Isyarat 'Hijau' menggunakan gerakan tangan huruf...", "answer": "G", "dictionary_id": 21, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/video/green_alt2.mp4"},
            {"question": "Isyarat 'Kuning' menggunakan gerakan tangan huruf...", "answer": "Y", "dictionary_id": 22, "sublevel_id": sublevel_id_5, "video_url": "https://example.com/quiz/video/yellow_alt2.mp4"},
        ])
        
        # --- Sublevel 6: Animals (sublevel_id: 6) ---
        sublevel_id_6 = 6
        soal_data.extend([
            {"question": "Bagaimana isyarat untuk 'Kucing'?", "answer": "Cubit pipi dengan telunjuk dan ibu jari beberapa kali", "dictionary_id": 23, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/cat.mp4"},
            {"question": "Tunjukkan isyarat 'Anjing'", "answer": "Tepuk paha kemudian jentikkan jari", "dictionary_id": 24, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/dog.mp4"},
            {"question": "Praktikkan isyarat 'Burung'", "answer": "Buka tutup telunjuk dan ibu jari di dekat mulut", "dictionary_id": 25, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/bird.mp4"},
            {"question": "Isyarat ini berarti hewan apa? (video: Kucing)", "answer": "Kucing", "dictionary_id": 23, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/cat.mp4"},
            {"question": "Isyarat ini berarti hewan apa? (video: Anjing)", "answer": "Anjing", "dictionary_id": 24, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/dog.mp4"},
            {"question": "Isyarat ini berarti hewan apa? (video: Burung)", "answer": "Burung", "dictionary_id": 25, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/bird.mp4"},
            {"question": "Gerakan mencubit pipi adalah isyarat untuk...", "answer": "Kucing", "dictionary_id": 23, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/cat_alt.mp4"},
            {"question": "Isyarat 'Anjing' melibatkan...", "answer": "Menepuk paha", "dictionary_id": 24, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/dog_alt.mp4"},
            {"question": "Isyarat 'Burung' melibatkan...", "answer": "Buka tutup jari di dekat mulut", "dictionary_id": 25, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/bird_alt.mp4"},
            {"question": "Tebak hewan dari isyarat (video: Kucing)", "answer": "Kucing", "dictionary_id": 23, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/cat_quiz.mp4"},
            {"question": "Tebak hewan dari isyarat (video: Anjing)", "answer": "Anjing", "dictionary_id": 24, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/dog_quiz.mp4"},
            {"question": "Tebak hewan dari isyarat (video: Burung)", "answer": "Burung", "dictionary_id": 25, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/bird_quiz.mp4"},
            {"question": "Pilih isyarat untuk 'Kucing'", "answer": "Cubit pipi", "dictionary_id": 23, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/cat_quiz2.mp4"},
            {"question": "Pilih isyarat untuk 'Anjing'", "answer": "Tepuk paha", "dictionary_id": 24, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/dog_quiz2.mp4"},
            {"question": "Pilih isyarat untuk 'Burung'", "answer": "Buka tutup jari di mulut", "dictionary_id": 25, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/bird_quiz2.mp4"},
            {"question": "Tangan mengepal di dekat mulut adalah isyarat untuk hewan apa?", "answer": "Burung", "dictionary_id": 25, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/bird_alt2.mp4"},
            {"question": "Isyarat 'Anjing' dimulai dengan gerakan tangan di...", "answer": "Paha", "dictionary_id": 24, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/dog_alt2.mp4"},
            {"question": "Hewan yang diisyaratkan dengan mencubit pipi adalah...", "answer": "Kucing", "dictionary_id": 23, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/cat_alt2.mp4"},
            {"question": "Mana isyarat yang benar untuk 'Anjing'?", "answer": "Tepuk paha", "dictionary_id": 24, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/dog_alt3.mp4"},
            {"question": "Tebak hewan dari isyarat (video: Burung)", "answer": "Burung", "dictionary_id": 25, "sublevel_id": sublevel_id_6, "video_url": "https://example.com/quiz/video/bird_alt3.mp4"},
        ])
        
        # --- Sublevel 7: Food & Drinks (sublevel_id: 7) ---
        sublevel_id_7 = 7
        soal_data.extend([
            {"question": "Bagaimana isyarat 'Makan'?", "answer": "Gerakkan tangan ke mulut seolah memasukkan makanan", "dictionary_id": 26, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/eat.mp4"},
            {"question": "Tunjukkan isyarat 'Minum'", "answer": "Angkat tangan seperti memegang gelas ke mulut", "dictionary_id": 27, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/drink.mp4"},
            {"question": "Praktikkan isyarat 'Nasi'", "answer": "Gerakkan tangan seolah mengambil nasi dengan sendok", "dictionary_id": 28, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/rice.mp4"},
            {"question": "Bagaimana cara mengisyaratkan 'Air'?", "answer": "Sentuh dagu dengan huruf W kemudian gerakkan ke bawah", "dictionary_id": 29, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/water.mp4"},
            {"question": "Isyarat ini berarti apa? (video: Makan)", "answer": "Makan", "dictionary_id": 26, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/video/eat.mp4"},
            {"question": "Isyarat ini berarti apa? (video: Minum)", "answer": "Minum", "dictionary_id": 27, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/video/drink.mp4"},
            {"question": "Isyarat ini berarti apa? (video: Nasi)", "answer": "Nasi", "dictionary_id": 28, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/video/rice.mp4"},
            {"question": "Isyarat ini berarti apa? (video: Air)", "answer": "Air", "dictionary_id": 29, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/video/water.mp4"},
            {"question": "Gerakan tangan ke mulut adalah isyarat untuk...", "answer": "Makan", "dictionary_id": 26, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/video/eat_alt.mp4"},
            {"question": "Isyarat 'Minum' melibatkan gerakan tangan seperti...", "answer": "Memegang gelas", "dictionary_id": 27, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/video/drink_alt.mp4"},
            {"question": "Isyarat 'Air' menggunakan huruf apa di dagu?", "answer": "W", "dictionary_id": 29, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/video/water_alt.mp4"},
            {"question": "Pilih isyarat untuk 'Makan'", "answer": "Gerakkan tangan ke mulut", "dictionary_id": 26, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/eat_quiz.mp4"},
            {"question": "Pilih isyarat untuk 'Minum'", "answer": "Angkat tangan seperti memegang gelas", "dictionary_id": 27, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/drink_quiz.mp4"},
            {"question": "Pilih isyarat untuk 'Nasi'", "answer": "Gerakkan tangan seolah mengambil nasi", "dictionary_id": 28, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/rice_quiz.mp4"},
            {"question": "Pilih isyarat untuk 'Air'", "answer": "Sentuh dagu dengan huruf W", "dictionary_id": 29, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/water_quiz.mp4"},
            {"question": "Manakah isyarat 'Nasi'?", "answer": "Gerakkan tangan seolah mengambil nasi", "dictionary_id": 28, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/video/rice_alt.mp4"},
            {"question": "Tebak isyarat ini (video: Minum)", "answer": "Minum", "dictionary_id": 27, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/video/drink_quiz_2.mp4"},
            {"question": "Tebak isyarat ini (video: Makan)", "answer": "Makan", "dictionary_id": 26, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/video/eat_quiz_2.mp4"},
            {"question": "Tebak isyarat ini (video: Air)", "answer": "Air", "dictionary_id": 29, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/video/water_quiz_2.mp4"},
            {"question": "Manakah isyarat yang benar untuk 'Makan'?", "answer": "Gerakan tangan ke mulut", "dictionary_id": 26, "sublevel_id": sublevel_id_7, "video_url": "https://example.com/quiz/video/eat_alt2.mp4"},
        ])
        
        # --- Sublevel 8: Weather (sublevel_id: 8) ---
        sublevel_id_8 = 8
        soal_data.extend([
            {"question": "Bagaimana isyarat 'Hujan'?", "answer": "Gerakkan kedua tangan dari atas ke bawah seperti air jatuh", "dictionary_id": 30, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/rain.mp4"},
            {"question": "Tunjukkan isyarat 'Panas'", "answer": "Bentuk cakar di dekat mulut kemudian buka dengan ekspresi panas", "dictionary_id": 31, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/hot.mp4"},
            {"question": "Praktikkan isyarat 'Dingin'", "answer": "Kedua tangan mengepal bergetar di depan tubuh", "dictionary_id": 32, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/cold.mp4"},
            {"question": "Isyarat ini berarti cuaca apa? (video: Hujan)", "answer": "Hujan", "dictionary_id": 30, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/rain.mp4"},
            {"question": "Isyarat ini berarti cuaca apa? (video: Panas)", "answer": "Panas", "dictionary_id": 31, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/hot.mp4"},
            {"question": "Isyarat ini berarti cuaca apa? (video: Dingin)", "answer": "Dingin", "dictionary_id": 32, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/cold.mp4"},
            {"question": "Isyarat 'Hujan' dibuat dengan gerakan...", "answer": "Kedua tangan dari atas ke bawah", "dictionary_id": 30, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/rain_alt.mp4"},
            {"question": "Isyarat 'Panas' melibatkan bentuk...", "answer": "Cakar", "dictionary_id": 31, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/hot_alt.mp4"},
            {"question": "Isyarat 'Dingin' ditunjukkan dengan...", "answer": "Tangan mengepal bergetar", "dictionary_id": 32, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/cold_alt.mp4"},
            {"question": "Pilih isyarat 'Dingin'", "answer": "Tangan bergetar", "dictionary_id": 32, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/cold_quiz.mp4"},
            {"question": "Pilih isyarat 'Hujan'", "answer": "Tangan turun dari atas", "dictionary_id": 30, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/rain_quiz.mp4"},
            {"question": "Pilih isyarat 'Panas'", "answer": "Bentuk cakar", "dictionary_id": 31, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/hot_quiz.mp4"},
            {"question": "Tebak cuaca dari isyarat (video: Dingin)", "answer": "Dingin", "dictionary_id": 32, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/cold_quiz_2.mp4"},
            {"question": "Tebak cuaca dari isyarat (video: Hujan)", "answer": "Hujan", "dictionary_id": 30, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/rain_quiz_2.mp4"},
            {"question": "Tebak cuaca dari isyarat (video: Panas)", "answer": "Panas", "dictionary_id": 31, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/hot_quiz_2.mp4"},
            {"question": "Isyarat 'Dingin' menggambarkan...", "answer": "Rasa dingin", "dictionary_id": 32, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/cold_alt2.mp4"},
            {"question": "Isyarat 'Panas' menggambarkan...", "answer": "Suhu tinggi", "dictionary_id": 31, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/hot_alt2.mp4"},
            {"question": "Isyarat 'Hujan' menggambarkan...", "answer": "Tetesan air", "dictionary_id": 30, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/rain_alt2.mp4"},
            {"question": "Gerakan melingkar di depan mulut adalah isyarat untuk cuaca...", "answer": "Panas", "dictionary_id": 31, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/hot_alt3.mp4"},
            {"question": "Isyarat 'Dingin' menggunakan tangan yang...", "answer": "Mengepal dan bergetar", "dictionary_id": 32, "sublevel_id": sublevel_id_8, "video_url": "https://example.com/quiz/video/cold_alt3.mp4"},
        ])
        
        # --- Sublevel 9: Time Concepts (sublevel_id: 9) ---
        sublevel_id_9 = 9
        soal_data.extend([
            {"question": "Bagaimana isyarat 'Hari'?", "answer": "Lingkarkan lengan dari timur ke barat meniru matahari", "dictionary_id": 33, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/day.mp4"},
            {"question": "Tunjukkan isyarat 'Malam'", "answer": "Lengkungkan tangan di atas tangan lain seperti matahari tenggelam", "dictionary_id": 34, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/night.mp4"},
            {"question": "Praktikkan isyarat 'Besok'", "answer": "Gerakkan tangan ke depan dengan huruf A", "dictionary_id": 35, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/tomorrow.mp4"},
            {"question": "Isyarat ini berarti konsep waktu apa? (video: Hari)", "answer": "Hari", "dictionary_id": 33, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/day.mp4"},
            {"question": "Isyarat ini berarti konsep waktu apa? (video: Malam)", "answer": "Malam", "dictionary_id": 34, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/night.mp4"},
            {"question": "Isyarat ini berarti konsep waktu apa? (video: Besok)", "answer": "Besok", "dictionary_id": 35, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/tomorrow.mp4"},
            {"question": "Gerakan melingkar meniru matahari adalah isyarat untuk...", "answer": "Hari", "dictionary_id": 33, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/day_alt.mp4"},
            {"question": "Isyarat 'Malam' menggambarkan...", "answer": "Matahari tenggelam", "dictionary_id": 34, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/night_alt.mp4"},
            {"question": "Isyarat 'Besok' menggunakan huruf...", "answer": "A", "dictionary_id": 35, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/tomorrow_alt.mp4"},
            {"question": "Pilih isyarat untuk 'Hari'", "answer": "Gerakan melingkar lengan", "dictionary_id": 33, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/day_quiz.mp4"},
            {"question": "Pilih isyarat untuk 'Malam'", "answer": "Lengkungkan tangan di atas", "dictionary_id": 34, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/night_quiz.mp4"},
            {"question": "Pilih isyarat untuk 'Besok'", "answer": "Gerakkan tangan ke depan dengan huruf A", "dictionary_id": 35, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/tomorrow_quiz.mp4"},
            {"question": "Tebak konsep waktu dari isyarat (video: Hari)", "answer": "Hari", "dictionary_id": 33, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/day_quiz_2.mp4"},
            {"question": "Tebak konsep waktu dari isyarat (video: Malam)", "answer": "Malam", "dictionary_id": 34, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/night_quiz_2.mp4"},
            {"question": "Tebak konsep waktu dari isyarat (video: Besok)", "answer": "Besok", "dictionary_id": 35, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/tomorrow_quiz_2.mp4"},
            {"question": "Isyarat 'Hari' menggunakan gerakan tangan yang...", "answer": "Melingkar", "dictionary_id": 33, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/day_alt2.mp4"},
            {"question": "Isyarat 'Malam' menggambarkan...", "answer": "Terbenamnya matahari", "dictionary_id": 34, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/night_alt2.mp4"},
            {"question": "Gerakan tangan ke depan dengan huruf 'A' adalah isyarat untuk...", "answer": "Besok", "dictionary_id": 35, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/tomorrow_alt2.mp4"},
            {"question": "Manakah yang benar untuk isyarat 'Hari'?", "answer": "Gerakan melingkar", "dictionary_id": 33, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/day_alt3.mp4"},
            {"question": "Isyarat 'Malam' menggunakan tangan yang...", "answer": "Membentuk lengkungan", "dictionary_id": 34, "sublevel_id": sublevel_id_9, "video_url": "https://example.com/quiz/video/night_alt3.mp4"},
        ])
        
        # --- Sublevel 10: Complex Grammar (sublevel_id: 10) ---
        sublevel_id_10 = 10
        soal_data.extend([
            {"question": "Bagaimana struktur kalimat tanya dalam bahasa isyarat?", "answer": "Gunakan ekspresi wajah bertanya", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/question_structure.mp4"},
            {"question": "Jelaskan penggunaan ruang dalam bahasa isyarat", "answer": "Ruang digunakan untuk menunjukkan hubungan antara objek dan orang", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/spatial_grammar.mp4"},
            {"question": "Bagaimana cara menggunakan classifier dalam bahasa isyarat?", "answer": "Classifier digunakan untuk menggambarkan bentuk, ukuran, dan gerakan objek", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/classifiers.mp4"},
            {"question": "Jelaskan pentingnya ekspresi wajah dalam bahasa isyarat", "answer": "Ekspresi wajah menunjukkan intonasi, emosi, dan struktur gramatikal", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/facial_expressions.mp4"},
            {"question": "Untuk menunjukkan pertanyaan, ekspresi wajah harus...", "answer": "Bertanya", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/question_structure_alt.mp4"},
            {"question": "Ruang di depan tubuh digunakan untuk...", "answer": "Menunjukkan hubungan spasial", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/spatial_grammar_alt.mp4"},
            {"question": "Classifier digunakan untuk menjelaskan...", "answer": "Bentuk objek", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/classifiers_alt.mp4"},
            {"question": "Apa peran ekspresi wajah dalam gramatikal bahasa isyarat?", "answer": "Mengubah makna kalimat", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/facial_expressions_alt.mp4"},
            {"question": "Yang mana bagian dari gramatikal bahasa isyarat?", "answer": "Ekspresi wajah", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/grammar_quiz.mp4"},
            {"question": "Kalimat tanya dalam bahasa isyarat diakhiri dengan...", "answer": "Ekspresi wajah bertanya", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/question_quiz.mp4"},
            {"question": "Konsep ruang dalam bahasa isyarat disebut...", "answer": "Spasial", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/spatial_quiz.mp4"},
            {"question": "Classifier adalah isyarat yang menggambarkan...", "answer": "Sifat objek", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/classifier_quiz.mp4"},
            {"question": "Ekspresi wajah dalam bahasa isyarat berfungsi sebagai...", "answer": "Intonasi", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/facial_quiz.mp4"},
            {"question": "Pentingnya ekspresi wajah dalam bahasa isyarat adalah...", "answer": "Menunjukkan intonasi", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/facial_quiz2.mp4"},
            {"question": "Untuk menunjukkan sebuah pertanyaan, pengguna harus...", "answer": "Menggunakan ekspresi wajah bertanya", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/question_quiz2.mp4"},
            {"question": "Classifier membantu untuk menjelaskan...", "answer": "Bentuk dan ukuran", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/classifier_quiz2.mp4"},
            {"question": "Yang mana yang termasuk elemen gramatikal bahasa isyarat?", "answer": "Ruang dan ekspresi wajah", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/grammar_quiz2.mp4"},
            {"question": "Elemen penting dalam bahasa isyarat adalah...", "answer": "Ekspresi wajah dan gerakan", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/grammar_quiz3.mp4"},
            {"question": "Isyarat tanda tanya dalam bahasa isyarat adalah...", "answer": "Ekspresi wajah bertanya", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/question_quiz3.mp4"},
            {"question": "Ruang isyarat adalah...", "answer": "Area di depan tubuh", "dictionary_id": 1, "sublevel_id": sublevel_id_10, "video_url": "https://example.com/quiz/spatial_quiz2.mp4"},
        ])
        
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