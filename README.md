# 🌟 ShopSpark AI Studio API

ShopSpark AI Studio হলো একটি আধুনিক **FastAPI** ভিত্তিক এআই ব্যাকএন্ড সার্ভিস। এটি বার্থডে পার্টি প্ল্যানিং, কাস্টম টি-শার্ট ডিজাইন ও মকআপ জেনারেশন এবং প্রিমিয়াম আমন্ত্রণপত্র (ইভেন্ট কার্ড ও মেসেজ) তৈরি করার শক্তিশালী এআই ইঞ্জিন সরবরাহ করে।

---

## 🏗️ প্রজেক্ট ফোল্ডার স্ট্রাকচার (Project Structure)

```
shopspark-studio-ai/
│
├── .env                  # লোকাল সিক্রেট কনফিগারেশন (Git-ignored)
├── .env.example          # এনভায়রনমেন্ট ভেরিয়েবল টেমপ্লেট
├── .gitignore            # অপ্রয়োজনীয় ও ক্যাশ ফাইল ইগনোর রুলস
├── main.py               # কোর FastAPI অ্যাপ্লিকেশন ও এআই রাউটসমূহ
├── requirements.txt      # পাইথন ডিপেন্ডেন্সিস তালিকা
├── uploads/              # ইউজার আপলোড করা ফাইল ডিরেক্টরি
│   └── .gitkeep
└── README.md             # পূর্ণাঙ্গ প্রজেক্ট ডকুমেন্টেশন
```

> **নোট**: `__pycache__` ও কম্পাইল্ড `.pyc` বাইনারি ফাইলগুলো সম্পূর্ণ ক্লিন করে `.gitignore`-এ যুক্ত করা হয়েছে যাতে রিপোজিটরি পরিষ্কার ও হালকা থাকে।

---

## 🚀 দ্রুত শুরু করার নির্দেশিকা (Quick Start Guide)

### ১. ভার্চুয়াল এনভায়রনমেন্ট সক্রিয় করা (Activate Virtual Environment)

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```
*(যদি PowerShell Script Execution Policy ইস্যু থাকে, তবে সরাসরি `.\venv\Scripts\python.exe main.py` রান করতে পারেন)*

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

---

### ২. প্যাকেজ ইন্সটল করা (Install Dependencies)

ভার্চুয়াল এনভায়রনমেন্টে প্রয়োজনীয় লাইব্রেরিগুলো ইন্সটল করতে:
```bash
pip install -r requirements.txt
```

প্যাকেজসমূহ:
- `fastapi` - উচ্চ পারফরম্যান্স সম্পন্ন ওয়েব ফ্রেমওয়ার্ক
- `uvicorn[standard]` - আল্ট্রাফাস্ট ASGI প্রোডাকশন সার্ভার
- `pydantic` - স্ট্রাকচার্ড ডাটা ভ্যালিডেশন
- `python-dotenv` - `.env` কনফিগারেশন লোডার
- `python-multipart` - ফাইল ও ফর্ম ডাটা হ্যান্ডলিং
- `requests` & `pillow` - নেটওয়ার্ক ও ইমেজ প্রসেসিং
- `openai` - ওপেনএআই এআই মডেল ইন্টিগ্রেশন
- `httpx` - এসিঙ্ক এইচটিটিপি ক্লায়েন্ট ও এপিআই টেস্টিং

---

### ৩. কনফিগারেশন (`.env`)

প্রজেক্টের রুট ডিরেক্টরিতে `.env` ফাইল কনফিগার করুন:
```env
PORT=8000
HOST=0.0.0.0
FRONTEND_URL=http://localhost:5173
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

---

### ৪. প্রজেক্ট রান করা (Run the Application)

**পদ্ধতি ১ (সরাসরি পাইথন স্ক্রিপ্ট থেকে):**
```bash
python main.py
```
বা ভার্চুয়াল এনভায়রনমেন্টের পাথ দিয়ে:
```powershell
.\venv\Scripts\python.exe main.py
```

**পদ্ধতি ২ (Uvicorn CLI দিয়ে অটো-রিলোড সহ):**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

সার্ভার চালু হলে ব্রাউজারে নিচের লিঙ্কগুলোতে ভিজিট করতে পারবেন:
- 🌐 **রুট এপিআই (Root API):** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 📖 **সোয়াগার ডকুমেন্টেশন (Interactive Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📑 **ReDoc ডকুমেন্টেশন:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 এপিআই এন্ডপয়েন্ট ও টেস্ট করার নিয়ম (API Endpoints & Testing)

### ১. হেলথ চেক (Health Check)
- **Method:** `GET`
- **URL:** `http://127.0.0.1:8000/health`
- **Response:**
```json
{
  "status": "healthy",
  "ai_ready": true
}
```

---

### ২. পার্টি প্ল্যান জেনারেটর (Party Generator)
- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/party_generate`
- **Headers:** `Content-Type: application/json`
- **Request Body (JSON):**
```json
{
  "person_name": "Alex",
  "person_age": 5,
  "budget": 1500,
  "num_guests": 20,
  "party_date": "15 Nov 2026",
  "location": "home",
  "party_details": {
    "theme": "spiderman",
    "favorite_activities": ["craft", "outdoor", "treasure"]
  },
  "num_product": 3
}
```

---

### ৩. টি-শার্ট ও মকআপ জেনারেটর (T-Shirt Designer)
- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/t_shirt_generate`
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `t_shirt_type`: `CHILD`
  - `t_shirt_size`: `3T`
  - `apparel_type`: `Toddler_Cotton_Jersey_TShirt`
  - `gender`: `BOY`
  - `t_shirt_color`: `blue`
  - `age`: `5`
  - `t_shirt_theme`: `spiderman`
  - `optional_description`: `Hero on mission`
  - `img_file`: *(ঐচ্ছিক ফাইল)*

---

### ৪. ইনভিটেশন কার্ড জেনারেটর (Invitation Card Generator)
- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/api/v1/generate-card`
- **Headers:** `Content-Type: application/json`
- **Request Body (JSON):**
```json
{
  "theme": "spiderman",
  "description": "Superhero birthday party",
  "age": 6,
  "gender": "Boy",
  "birthday_person_name": "Alex",
  "venue": "Magic Funland Club, Paris",
  "date": "2026-11-15",
  "time": "15:00",
  "contact_info": "+33 6 12 34 56 78",
  "language": "en"
}
```

---

### ৫. ইনভিটেশন শর্ট মেসেজ (Short Message Generator)
- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/api/v1/generate-message`
- **Headers:** `Content-Type: application/json`
- **Request Body (JSON):**
```json
{
  "childName": "Alex",
  "age": 6,
  "theme": "superhero",
  "venue": "Our Home",
  "language": "en"
}
```
- **Response:**
```json
{
  "success": true,
  "generated_message": "Calling all superheroes—suit up and fly over to Our Home to celebrate Alex turning 6! 🦸‍♂️💥 Join the mission for an epic day of games, cake, and super-powered fun! 🎉🎂⚡"
}
```

---

## 🧪 স্বয়ংক্রিয় টেস্ট রান করার স্ক্রিপ্ট (Automated Test Run)

আপনি নিচের কমান্ডটি দিয়ে এক ক্লিকে সম্পূর্ণ এপিআই টেস্ট করতে পারবেন:
```powershell
.\venv\Scripts\python.exe -c "from fastapi.testclient import TestClient; from main import app; c = TestClient(app); print('Root:', c.get('/').status_code); print('Health:', c.get('/health').status_code); print('Message:', c.post('/api/v1/generate-message', json={'childName':'Alex','age':6,'theme':'superhero','venue':'Home','language':'en'}).json())"
```
