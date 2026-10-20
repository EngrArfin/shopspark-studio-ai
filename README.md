# 🌟 ShopSpark AI Studio API

ShopSpark AI Studio is a high-performance **FastAPI** backend microservice designed for AI-driven e-commerce and event planning experiences. Powered by **Google Gemini** and **OpenAI**, it offers intelligent birthday party itineraries, custom T-shirt graphic & mockup generation, and personalized event invitation cards & text messages.

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Deployment](https://img.shields.io/badge/Vercel-Live-black?logo=vercel)](https://shopspark-studio-ai.vercel.app)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌐 Live Production Links

- 🚀 **Live API Base URL:** [https://shopspark-studio-ai.vercel.app](https://shopspark-studio-ai.vercel.app)
- 📖 **Interactive Swagger UI:** [https://shopspark-studio-ai.vercel.app/docs](https://shopspark-studio-ai.vercel.app/docs)
- 📑 **ReDoc Documentation:** [https://shopspark-studio-ai.vercel.app/redoc](https://shopspark-studio-ai.vercel.app/redoc)
- 🩺 **Health Check:** [https://shopspark-studio-ai.vercel.app/health](https://shopspark-studio-ai.vercel.app/health)

---

## 🏗️ Project Structure

```text
shopspark-studio-ai/
│
├── .env                  # Local environment configuration (Git-ignored)
├── .env.example          # Environment variables template
├── .gitignore            # Git exclusion rules
├── .dockerignore         # Docker build exclusion rules
├── Dockerfile            # Container build specification
├── Procfile              # Process runner config for Render / Railway / Heroku
├── main.py               # Core FastAPI application & AI service routes
├── requirements.txt      # Python dependencies
├── uploads/              # Temporary file uploads directory (Git-tracked with .gitkeep)
│   └── .gitkeep
└── README.md             # Comprehensive project documentation
```

---

## ✨ Features

- **🎉 Intelligent Party Planner (`/party_generate`):** Builds time-slotted itineraries, recommended activities, gift product counts, budget allocation, and theme-matched songs/movie suggestions.
- **👕 AI T-Shirt Designer & Mockup Engine (`/t_shirt_generate`):** Generates vector graphic artwork stickers and photorealistic studio mockup images on colored apparel.
- **💌 Invitation Card Creator (`/api/v1/generate-card`):** Creates formatted party invitation texts along with theme-based card illustrations.
- **📱 Instant Invitation Short Message (`/api/v1/generate-message`):** Crafts fun, catchy 1-2 sentence invitation SMS/WhatsApp messages in English or Bengali.
- **⚡ Dual AI Engine Architecture:** Primary ultra-fast generation via Google Gemini with intelligent OpenAI fallback.

---

## 🚀 Quick Start Guide

### 1. Clone the Repository

```bash
git clone https://github.com/EngrArfin/shopspark-studio-ai.git
cd shopspark-studio-ai
```

### 2. Set Up Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If you encounter execution policy restrictions in PowerShell, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

Install all required production and AI libraries:
```bash
pip install -r requirements.txt
```

Core dependencies include:
- `fastapi` - Modern asynchronous web framework
- `uvicorn[standard]` - High-performance ASGI production server
- `pydantic` - Data parsing and request validation
- `python-dotenv` - Environment variable management
- `python-multipart` - Multi-part file upload support
- `requests` & `pillow` - Network utilities and image handling
- `openai` - OpenAI SDK integration
- `httpx` - Async HTTP client for external AI calls

---

### 4. Configure Environment Variables

Create a `.env` file in the project root based on `.env.example`:

```env
PORT=8000
HOST=0.0.0.0
FRONTEND_URL=http://localhost:5173
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

---

### 5. Run the Application Locally

**Option A (Using Python entrypoint):**
```bash
python main.py
```
*(or with virtual environment path: `.\venv\Scripts\python.exe main.py`)*

**Option B (Using Uvicorn CLI with hot-reload):**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Once running, access the local endpoints at:
- Root API: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 API Endpoints & Request Examples

### 1. System Health Check
- **Method:** `GET`
- **Path:** `/health`
- **Response:**
```json
{
  "status": "healthy",
  "ai_ready": true
}
```

---

### 2. Party Plan Generator
- **Method:** `POST`
- **Path:** `/party_generate`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
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

### 3. T-Shirt Design & Mockup Generator
- **Method:** `POST`
- **Path:** `/t_shirt_generate`
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
  - `img_file`: *(Optional file upload)*

---

### 4. Invitation Card Generator
- **Method:** `POST`
- **Path:** `/api/v1/generate-card`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
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

### 5. Short Message Generator
- **Method:** `POST`
- **Path:** `/api/v1/generate-message`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
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
  "generated_message": "🎉 Join us in celebrating Alex's 6th Birthday! An unforgettable Superhero party is planned at Our Home. Get ready for epic fun! 🎂⚡"
}
```

---

## 🧪 Automated Testing Script

Run a quick end-to-end verification of all main endpoints in a single command:

```powershell
.\venv\Scripts\python.exe -c "from fastapi.testclient import TestClient; from main import app; c = TestClient(app); print('Root:', c.get('/').status_code); print('Health:', c.get('/health').status_code); print('Message:', c.post('/api/v1/generate-message', json={'childName':'Alex','age':6,'theme':'superhero','venue':'Home','language':'en'}).json())"
```

---

## ☁️ Deployment Guide

### Option 1: Vercel (Current Production Platform)

This repository includes native zero-config deployment support for Vercel.

1. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```
2. Deploy directly from your terminal:
   ```bash
   vercel --prod
   ```
3. Set your environment variables in the Vercel dashboard:
   - `OPENAI_API_KEY`
   - `GEMINI_API_KEY`
   - `FRONTEND_URL`

---

### Option 2: Render.com

1. Create a new **Web Service** on [Render](https://render.com).
2. Connect your GitHub repository: `shopspark-studio-ai`.
3. Configure the service settings:
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add your environment variables (`OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.) in the Environment tab.

---

### Option 3: Docker Container

A multi-stage, optimized `Dockerfile` is included.

1. Build the Docker image:
   ```bash
   docker build -t shopspark-ai-studio .
   ```
2. Run the container:
   ```bash
   docker run -d -p 8000:8000 --env-file .env shopspark-ai-studio
   ```
3. Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
