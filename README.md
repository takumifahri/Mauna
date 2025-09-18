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

# Mauna — Dokumentasi Singkat (Read.md)

Ringkasan  
Mauna adalah API FastAPI untuk aplikasi pembelajaran bahasa isyarat. Repo ini menyediakan auth (JWT), middleware (CORS, rate-limit, JWT check), database (SQLAlchemy + databases), migration (alembic), dan seeder.

Quick start
1. Buat virtualenv dan aktifkan:
   - windows: python -m venv .venv && .venv\Scripts\activate
2. Pasang dependensi:
   - pip install -r requirements.txt
3. Siapkan environment (.env) di root. Minimal:
   - DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_NAME, DATABASE_USERNAME, DATABASE_PASSWORD
   - SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
   - ENVIRONMENT (development|production), RATE_LIMIT, ALLOWED_ORIGINS
4. Jalankan migrasi / seed:
   - python cli.py migrate:create "initial"  (opsional)
   - python cli.py migrate (atau gunakan alembic langsung)
   - python cli.py db:seed
5. Jalankan server:
   - uvicorn src.app.main:app --reload

Struktur rute penting
- Public / testing:
  - GET /              -> root testing (didaftarkan oleh test_router)
  - GET /test
  - GET /health
- API prefix:
  - Semua endpoint API berada di bawah /api
  - Auth:
    - POST /api/auth/register  -> register (body: RegisterRequest)
    - POST /api/auth/login     -> login (body: LoginRequest) → respon: access_token
    - POST /api/auth/refresh   -> refresh token (body: RefreshTokenRequest)
    - POST /api/auth/logout    -> logout (Bearer token required)
    - GET  /api/auth/profile   -> ambil profile (Bearer token)
    - GET  /api/auth/verify    -> cek token valid (Bearer token)

Middleware & keamanan
- setup_middleware(app, rate_limit, cors_origins, environment)
  - JWTAuthMiddleware: memvalidasi header Authorization Bearer <token> untuk path terproteksi.
  - RateLimitMiddleware: default hitungan per-klien (user:{id} jika terautentikasi, atau ip:{ip}) — set RATE_LIMIT di .env.
    - Implementasi saat ini memakai in-memory store (tidak cocok untuk multi‑worker). Untuk production gunakan Redis.
  - Enhanced CORS: konfigurasi via ALLOWED_ORIGINS. Pada development default = "*".
- Token JWT
  - Dibuat oleh AuthHandler.create_access_token dengan payload minimal: {"sub": "<user_id>"}
  - Simpan token di Authorization header: Authorization: Bearer <token>

Database & migrations
- Config: src/database/db.py (DatabaseConfig)
- Alembic: folder alembic/, env.py mengimpor metadata dari src.database.db.Base
- Seeder: src/database/seeder.py — run via python cli.py db:seed

Tips debugging
- Error "attempted relative import beyond top-level package": gunakan absolute import `from src...` dan jalankan uvicorn dari root project.
- Jika rate-limit tampak tidak sinkron saat --reload / multiple workers: gunakan Redis atau disable RateLimitMiddleware sementara.
- Jika Pylance menandai Column[...] dalam kondisi boolean: gunakan bool(column_prop) atau ambil nilai aktual dari instance setelah refresh dari DB.

Contoh singkat: register + login (curl)
- Register:
  curl -X POST http://127.0.0.1:8000/api/auth/register -H "Content-Type: application/json" -d '{"username":"user1","email":"u@example.com","password":"Password123","first_name":"A","last_name":"B"}'
- Login:
  curl -X POST http://127.0.0.1:8000/api/auth/login -H "Content-Type: application/json" -d '{"email_or_username":"user1","password":"Password123"}'
- Akses profile (menggunakan access_token):
  curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/auth/profile

Pengembangan & produksi
- Development: ENVIRONMENT=development (CORS permissive, RATE_LIMIT tinggi)
- Production: ENVIRONMENT=production, set ALLOWED_ORIGINS, gunakan Redis untuk rate limit, gunakan HTTPS, set secure SECRET_KEY

Kontak & catatan
- File entrypoint: src/app/main.py  
- Routes dikelola di src/routes/ (__init__.py menggabungkan routers).  
- Untuk menambahkan route baru, tambahkan router lalu include ke api_router di src/routes/__init__.py.

Selesai — sesuaikan isi .env dan migrasi sebelum uji penuh.