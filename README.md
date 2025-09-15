# Mauna — Sistem Pembelajaran Interaktif Bahasa Isyarat Berbasis Machine Learning

Deskripsi singkat
- Mauna adalah aplikasi pembelajaran bahasa isyarat dengan inferensi real-time dan modul latihan.
```
==================================================
| Path                 | Tujuan singkat
--------------------------------------------------
| .venv/               | Virtual environment (jangan commit ke VCS)
| data/                | Dataset mentah, anotasi, contoh (opsional)
| notebooks/           | Jupyter notebooks — eksperimen & analisis (opsional)
| src/                 | Kode sumber utama (rincian di bawah)
| model/               | Model terlatih / checkpoints / artefak
| output/              | Hasil pelatihan: logs, metrics, artifacts
| tests/               | Unit & integration tests
| requirements.txt     | Daftar dependensi (pip install -r requirements.txt) — [requirements.txt](requirements.txt)
| Dockerfile           | Instruksi Docker untuk build image — [Dockerfile](Dockerfile)
| .gitignore           | File / direktori yang diabaikan oleh Git — [.gitignore](.gitignore)
--------------------------------------------------

src (struktur sesuai folder Anda)
--------------------------------------------------
```
```
src
│
├── app/
│   └── main.py               # Entry point app / server — [src/app/main.py](src/app/main.py)
│
├── database/
│   ├── connection.py         # Koneksi DB — [src/database/connection.py](src/database/connection.py)
│   └── seed/                 # Seeder / data awal
│
├── handler/                  # Handler / service layer
├── routes/                   # Routing API & grup route
└── utils/                    # Utilitas: helper, validator, dll
--------------------------------------------------

model (yang ada di repo)
--------------------------------------------------
model/
├── output/                   # model outputs / artifacts — [model/output](model/output)
└── test/                     # contoh/tes model — [model/test](model/test)
--------------------------------------------------
```
Catatan:
- Jika ada file / folder tambahan yang ingin dimasukkan ke README (mis. data/, notebooks/), beritahu saya agar saya tambahkan.
1. Buat dan aktifkan virtual environment:
   python -m venv .venv
   .venv\Scripts\activate

2. Pasang dependensi:
   pip install -r requirements.txt

3. Menjalankan API / app (contoh FastAPI):
   uvicorn src.app.main:app --reload  --port 8000

4. Menjalankan demo inferensi (mis. webcam):
   python src/infer.py --model model/best.ckpt --camera 0

Konvensi & tips
- Simpan model terlatih di folder model/ dengan timestamped subfolder.
- Letakkan dataset kecil untuk demo di data/demo/ agar mudah diuji oleh juri.
- Dokumentasikan format dataset di data/README.md.

Kontribusi
- Fork, buat branch fitur, sertakan test di tests/ dan buka pull request.

Lisensi
- Tambahkan file LICENSE (mis. MIT) di root repo.

Kontak
- Tim Mauna — deskripsi singkat kontak / channel komunikasi (mis. email/team chat) untuk koordinasi kompetisi.

Catatan akhir
- Fokus pada pengalaman pembelajaran interaktif dan kecepatan inferensi untuk penggunaan real-time.
- Sediakan dataset demo kecil agar juri dapat mencoba aplikasi tanpa instalasi besar.
