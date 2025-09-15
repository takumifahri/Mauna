# Mauna — Sistem Pembelajaran Interaktif Bahasa Isyarat Berbasis Machine Learning

Deskripsi singkat
- Mauna adalah aplikasi pembelajaran bahasa isyarat dengan inferensi real-time dan modul latihan.

Direktori yang disarankan (struktur & tujuan)
- .venv/                — virtual environment (tidak dimasukkan ke VCS)
- data/                 — dataset mentah, anotasi, dan contoh dataset
- notebooks/            — eksperimen dan analisis Jupyter
- src/                  — kode sumber aplikasi
    - src/preprocessing.py   — pembersihan & augmentasi data
    - src/dataset.py         — pembuat dataset (PyTorch/TensorFlow)
    - src/model.py           — arsitektur model & utilitas
    - src/train.py           — skrip pelatihan
    - src/infer.py           — inferensi webcam / demo
    - src/app/                — frontend (Streamlit / FastAPI / Flask)
- app/                  — (opsional) paket aplikasi / UI yang dibangun
- model/                — model terlatih / checkpoints
- output/               — hasil pelatihan, log, dan metric
- tests/                — tes unit
- requirements.txt      — daftar dependensi ([requirements.txt](requirements.txt))
- Dockerfile            — image dasar untuk pengemasan ([Dockerfile](Dockerfile))
- .gitignore            — file/dir yang diabaikan ([.gitignore](.gitignore))

Panduan singkat (Windows)
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
