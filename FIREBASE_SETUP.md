# Firebase Setup Guide

## 1. Create a Firebase Project

1. Go to https://console.firebase.google.com/
2. Click **Add project**
3. Name it (e.g. `hand-gesture-analytics`)
4. Disable Google Analytics (optional)
5. Click **Create project**

## 2. Enable Authentication (Email/Password)

1. In Firebase Console, go to **Authentication** → **Sign-in method**
2. Click **Email/Password**, enable it, click **Save**
3. Go to **Users** tab, click **Add user**, create a test account (email + password)

## 3. Create Realtime Database

1. Go to **Realtime Database** → **Create Database**
2. Choose a region closest to you
3. Start in **test mode** (for development):

```json
{
  "rules": {
    ".read": "auth != null",
    ".write": "auth != null"
  }
}
```

4. Click **Enable**

## 4. Generate Admin SDK Credentials (Python)

1. Go to **Project Settings** → **Service accounts**
2. Click **Generate new private key**
3. Download the JSON file
4. Save as `python/firebase-credentials.json` in the project

## 5. Get Web App Config

1. Go to **Project Settings** → **General**
2. Under **Your apps**, click **Add app** → **Web**
3. Register the app (nickname: `web-dashboard`)
4. Copy the `firebaseConfig` object values

## 6. Configure Environment Variables

### React (.env)

Create `web/.env` with values from step 5:

```env
VITE_FIREBASE_API_KEY=AIza...
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
```

### Python

Either place `firebase-credentials.json` at `python/firebase-credentials.json`
or set the environment variable:

```bash
export FIREBASE_CREDENTIALS=/path/to/firebase-credentials.json
export FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com
```

## 7. Run the Project

### Python

```bash
cd python
pip install -r requirements.txt
python main.py
```

### React

```bash
cd web
npm install
npm run dev
```

## Database Structure (auto-created)

```
hand_gesture/
├── current/
│   ├── fingers: 2
│   ├── gesture: "Peace"
│   └── timestamp: 1749450000
├── stats/
│   ├── totalDetection: 152
│   ├── fistCount: 20
│   ├── pointCount: 15
│   ├── peaceCount: 70
│   ├── threeCount: 10
│   ├── fourCount: 12
│   └── openHandCount: 25
└── history/
    └── {timestamp}/
        ├── fingers: 2
        ├── gesture: "Peace"
        └── timestamp: 1749450000123
```
