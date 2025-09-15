# Mauna — Sistem Pembelajaran Interaktif Bahasa Isyarat Berbasis Machine Learning

Deskripsi singkat
- Mauna adalah aplikasi pembelajaran bahasa isyarat dengan inferensi real-time dan modul latihan.

| Path                 | Tujuan singkat
--------------------------------------------------
| .venv/               | Virtual environment (jangan commit ke VCS)
| data/                | Dataset mentah, anotasi, contoh (lihat data/README.md)
| notebooks/           | Jupyter notebooks — eksperimen & analisis
| src/                 | Kode sumber utama
|   ├─ preprocessing.py| Pembersihan & augmentasi data
|   ├─ dataset.py      | Pembuat dataset (PyTorch / TensorFlow)
|   ├─ model.py        | Arsitektur model & utilitas
|   ├─ train.py        | Skrip pelatihan
|   ├─ infer.py        | Skrip inferensi (webcam / demo)
|   └─ app/            | Backend / UI (FastAPI / Streamlit / Flask)
| app/                 | Paket aplikasi / UI yang dibangun (opsional)
| model/               | Model terlatih / checkpoints (gunakan subfolder bertimestamp)
| output/              | Hasil pelatihan: logs, metrics, artifacts
| tests/               | Unit & integration tests
| requirements.txt     | Daftar dependensi (pip install -r requirements.txt)
| Dockerfile           | Instruksi Docker untuk build image
| .gitignore           | File / direktori yang diabaikan oleh Git
--------------------------------------------------ndows)
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
