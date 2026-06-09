# PantauGestur

Aplikasi deteksi gestur tangan real-time menggunakan kamera webcam. Hasil deteksi dikirim ke Firebase Realtime Database dan ditampilkan di dashboard web yang bisa dipantau langsung secara live.

## Kebutuhan

- Python 3.10+
- Node.js 20+
- npm
- Webcam

## Setup

### 1. Firebase

1. Buat project di [Firebase Console](https://console.firebase.google.com)
2. Enable **Anonymous Sign-in** di Authentication → Sign-in method
3. Buat Realtime Database, atur rules:
   ```json
   {
     "rules": {
       ".read": "auth != null",
       ".write": "auth != null"
     }
   }
   ```
4. Import `firebase-database-init.json` ke database
5. Generate **Service Account** (Project Settings → Service accounts) → download JSON → simpan sebagai `python/firebase-credentials.json`
6. Buat **Web App** (Project Settings → General → Add app → Web) → copy config

### 2. Python

```bash
cd python
pip install -r requirements.txt
```

### 3. Web

```bash
cp web/.env.example web/.env
```

Isi `web/.env` dengan config Firebase Web App dari langkah 1.6:

```
VITE_FIREBASE_API_KEY=AIza...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_DATABASE_URL=...
VITE_FIREBASE_PROJECT_ID=...
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
```

Lalu:

```bash
cd web
npm install
```

### 4. Model MediaPipe

Pastikan file `python/hand_landmarker.task` ada. Jika tidak, download dari:

```
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
```

## Menjalankan

### Terminal 1 — Python server (port 5002)

```bash
cd python
python server.py
```

> **Catatan:** Di Linux, jika butuh akses kamera, jalankan dengan `sg video -c`:
> ```bash
> sg video -c 'python server.py'
> ```

### Terminal 2 — React dashboard (port 3000)

```bash
cd web
npm run web
```

Buka `http://localhost:3000`.

## Troubleshooting

### Port 5002 already in use

Jika muncul `Address already in use` / `Port 5002 is in use`, ada proses server sebelumnya yang masih jalan. Kill dengan:

```bash
fuser -k 5002/tcp
```

Atau:

```bash
kill -9 $(lsof -ti :5002)
```

### Pakai script start

Jika mau gampang, edit dulu `start.sh` — sesuaikan path Python dengan environment kamu, lalu:

```bash
./start.sh
```

Atau langsung via npm (path Python perlu disesuaikan di `web/package.json` script `python`):

```bash
cd web
npm run dev
```

## Gestur

| Jari | Gestur     |
|------|------------|
| 0    | Fist       |
| 1    | Point      |
| 2    | Peace      |
| 3    | Three      |
| 4    | Four       |
| 5    | Open Hand  |

## API

| Endpoint           | Keterangan                          |
|--------------------|-------------------------------------|
| `/frame.jpg`       | Snapshot kamera terkini             |
| `/detection_data`  | JSON: gesture, fingers, stats       |
