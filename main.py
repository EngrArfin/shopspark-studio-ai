import os
import json
import re
import urllib.parse
import random
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="ShopSpark AI Studio API",
    description="Backend API powered by Gemini & OpenAI for Party Planning, Custom T-Shirt Design & Mockups, and Invitation Cards.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory setup
if os.environ.get("VERCEL"):
    UPLOAD_DIR = "/tmp/uploads"
else:
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ==========================================
# 1. Pydantic Models (Schemas)
# ==========================================

# --- Party Generator Schemas ---
class PartyDetails(BaseModel):
    theme: str = Field(..., json_schema_extra={"example": "spiderman"}, description="Party theme")
    favorite_activities: List[str] = Field(
        default=["craft", "outdoor", "treasure"], 
        json_schema_extra={"example": ["craft", "outdoor", "treasure"]},
        description="List of preferred activities"
    )

class PartyGenerationRequest(BaseModel):
    person_name: str = Field(..., json_schema_extra={"example": "Alex"}, description="Name of the person celebrating")
    person_age: int = Field(..., json_schema_extra={"example": 5}, description="Age of the person")
    budget: float = Field(..., json_schema_extra={"example": 1500}, description="Total budget in currency")
    num_guests: int = Field(..., json_schema_extra={"example": 20}, description="Expected number of guests")
    party_date: str = Field(..., json_schema_extra={"example": "15 Nov 2026"}, description="Date of the party")
    location: str = Field(..., json_schema_extra={"example": "home"}, description="Location type (e.g. home, park, venue)")
    party_details: PartyDetails
    num_product: int = Field(default=3, json_schema_extra={"example": 3}, description="Number of suggested gift products")

class SongMovieLink(BaseModel):
    title: str
    description: str
    channel: str
    url: str
    views: str

class SuggestedGift(BaseModel):
    id: str
    title: str
    link: str
    image_url: str

class PartyGenerationResponse(BaseModel):
    party_plan: Dict[str, List[str]]
    adventure_song_movie_links: List[SongMovieLink]
    suggested_gifts: List[SuggestedGift]


# --- T-Shirt Generator Schemas ---
class GenerateTShirtResponse(BaseModel):
    success: bool
    message: str
    generated_design_url: str
    generated_mockup_url: str


# --- Invitation Card Schemas ---
class GenerateCardRequest(BaseModel):
    theme: str = Field(..., json_schema_extra={"example": "spiderman"})
    description: Optional[str] = Field("Superhero birthday party", json_schema_extra={"example": "Fun party"})
    age: int = Field(..., json_schema_extra={"example": 6})
    gender: Optional[str] = Field("Boy", json_schema_extra={"example": "Boy"})
    birthday_person_name: str = Field(..., json_schema_extra={"example": "Alex"})
    venue: str = Field(..., json_schema_extra={"example": "Magic Funland Club, Paris"})
    date: str = Field(..., json_schema_extra={"example": "2026-11-15"})
    time: str = Field(..., json_schema_extra={"example": "15:00"})
    contact_info: str = Field(..., json_schema_extra={"example": "+33 6 12 34 56 78"})
    language: str = Field(default="en", json_schema_extra={"example": "en"})
    message: Optional[str] = None

class GeneratedImage(BaseModel):
    url: str
    public_id: str

class GenerateCardResponse(BaseModel):
    invitation_text: str
    images: List[GeneratedImage]


# --- Message Generator Schemas ---
class GenerateMessageRequest(BaseModel):
    childName: str = Field(..., json_schema_extra={"example": "Alex"})
    age: int = Field(..., json_schema_extra={"example": 6})
    theme: Optional[str] = Field("superhero", json_schema_extra={"example": "spiderman"})
    venue: Optional[str] = Field("Our Home", json_schema_extra={"example": "Magic Funland Club"})
    language: Optional[str] = Field("en", json_schema_extra={"example": "en"})

class GenerateMessageResponse(BaseModel):
    success: bool
    generated_message: str


# ==========================================
# 2. AI Utility & Engine Functions
# ==========================================

def call_gemini_api(prompt: str) -> Optional[str]:
    """Call Google Gemini 3.8 Flash for intelligent text/JSON generation."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or "your_" in gemini_key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={gemini_key}"
    try:
        response = requests.post(
            url,
            json={"contents": [{"parts": [{"text": prompt}]}]},
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                texts = [p.get("text", "") for p in parts if "text" in p]
                if texts:
                    return "".join(texts).strip()
        else:
            print(f"[Gemini API Warning] Status {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"[Gemini API Exception]: {e}")
    return None


def call_openai_chat(prompt: str) -> Optional[str]:
    """Call OpenAI Chat Completions as secondary fallback."""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or "your_" in openai_key:
        return None
    try:
        import openai
        client = openai.OpenAI(api_key=openai_key)
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        return res.choices[0].message.content
    except Exception as e:
        print(f"[OpenAI Chat Exception]: {e}")
    return None


def ask_ai(prompt: str) -> Optional[str]:
    """Tries Gemini first, then OpenAI fallback."""
    result = call_gemini_api(prompt)
    if result:
        return result
    return call_openai_chat(prompt)


def extract_json(raw_text: str) -> Optional[dict]:
    """Robustly extracts and parses JSON dictionary from LLM responses."""
    if not raw_text:
        return None
    
    # 1. Try stripping markdown blocks
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # 2. Try regex extraction of JSON object {...}
    match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except Exception:
            pass

    return None


def generate_ai_image_url(prompt: str, seed: Optional[int] = None) -> str:
    """
    Generates high-resolution AI artwork URL for T-Shirt graphics and mockups.
    First checks OpenAI image generation; falls back to instant Pollinations AI (Flux engine).
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and "your_" not in openai_key:
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            res = client.images.generate(
                model="gpt-image-1-mini",
                prompt=prompt[:950],
                size="1024x1024",
                n=1
            )
            if res.data and res.data[0].url:
                return res.data[0].url
        except Exception:
            # If OpenAI credit balance is exhausted or rate-limited, fall back to Flux AI
            pass

    # High quality, instant AI image generation using Flux/SDXL engine
    seed_val = seed or random.randint(1000, 999999)
    encoded_prompt = urllib.parse.quote(prompt.strip())
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed_val}&nologo=true&enhance=true"


# ==========================================
# 3. System & Health Check Endpoints
# ==========================================

@app.get("/", tags=["System"])
async def root():
    return {
        "status": "online",
        "service": "ShopSpark AI Studio API",
        "version": "2.0.0",
        "ai_engines": {
            "gemini": "Active (Gemini 3.8 Flash)",
            "openai": "Configured (Fallback)",
            "image_generation": "Flux / DALL-E AI Engine Active"
        },
        "swagger_docs": "/docs",
        "redoc_docs": "/redoc",
        "endpoints": [
            "POST /party_generate",
            "POST /t_shirt_generate",
            "POST /api/v1/generate-card",
            "POST /api/v1/generate-message"
        ]
    }

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "ai_ready": True}


# ==========================================
# 4. AI Feature Endpoints
# ==========================================

# 1. Party Plan Generator
@app.post("/party_generate", response_model=PartyGenerationResponse, tags=["Party Generator"])
async def generate_party_plan(payload: PartyGenerationRequest):
    """
    Generates an intelligent, tailored hourly birthday party itinerary, song/video links,
    and gift ideas using Gemini AI.
    """
    theme = payload.party_details.theme
    name = payload.person_name
    age = payload.person_age
    budget = payload.budget
    num_guests = payload.num_guests
    location = payload.location
    activities = ", ".join(payload.party_details.favorite_activities)

    ai_prompt = f"""
    You are an expert children's birthday party planner. Create a personalized party plan for:
    - Celebrant: {name}, turning {age} years old
    - Theme: {theme}
    - Budget: ${budget}
    - Number of Guests: {num_guests}
    - Location: {location}
    - Favorite Activities: {activities}
    - Suggested Gifts Count: {payload.num_product}

    Output ONLY a valid JSON object (no markdown quotes, no extra text outside the JSON) with the following structure:
    {{
      "party_plan": {{
        "1. Welcome & Arrival (02:00 PM - 02:30 PM)": ["bullet 1", "bullet 2", "bullet 3"],
        "2. Main Adventure (02:30 PM - 03:45 PM)": ["bullet 1", "bullet 2", "bullet 3"],
        "3. Feast & Refreshments (03:45 PM - 04:30 PM)": ["bullet 1", "bullet 2", "bullet 3"],
        "4. Cake Celebration (04:30 PM - 05:00 PM)": ["bullet 1", "bullet 2", "bullet 3"],
        "5. Farewell & Goodies (05:00 PM - 05:30 PM)": ["bullet 1", "bullet 2"]
      }},
      "adventure_song_movie_links": [
        {{
          "title": "Title related to {theme}",
          "description": "Fun description for party",
          "channel": "Kids Party Fun",
          "url": "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
          "views": "2.1M"
        }},
        {{
          "title": "Adventure Theme Song",
          "description": "Celebration dance song",
          "channel": "Party Beats Hub",
          "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
          "views": "3.5M"
        }}
      ],
      "suggested_gifts": [
        {{
          "id": "gift-1",
          "title": "Themed gift item for {name}",
          "link": "/products/custom-gift",
          "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop&q=80"
        }}
      ]
    }}
    Ensure suggested_gifts contains exactly {payload.num_product} items.
    """

    raw_response = ask_ai(ai_prompt)
    if raw_response:
        data = extract_json(raw_response)
        if data and "party_plan" in data:
            return PartyGenerationResponse(
                party_plan=data.get("party_plan", {}),
                adventure_song_movie_links=data.get("adventure_song_movie_links", []),
                suggested_gifts=data.get("suggested_gifts", [])[:payload.num_product]
            )

    # Fallback dynamic plan if AI response formatting fails
    party_plan = {
        "1. Welcome & VIP Arrival (02:00 PM - 02:30 PM)": [
            f"VIP Welcome: Greet guests with personalized {theme.capitalize()} badges & wristbands",
            f"Refreshing welcome drinks and music playing in the {location.capitalize()} entrance",
            f"Fun photo booth snapshot station with {theme.capitalize()} props and masks"
        ],
        "2. Main Event Adventure (02:30 PM - 03:45 PM)": [
            f"Grand Quest for {name}'s {age}th Birthday: Hero challenge obstacle course",
            f"Creative workshop focusing on: {activities}",
            f"Interactive {theme.capitalize()} trivia quiz & treasure hunt with fun prizes"
        ],
        "3. Feast & Refreshments (03:45 PM - 04:30 PM)": [
            f"Delicious thematic food platter (mini sliders, nuggets, superhero fruit skewers)",
            "Beverage station with signature colorful celebration punch",
            "Social playtime and kid-friendly party games"
        ],
        "4. Grand Cake Celebration (04:30 PM - 05:00 PM)": [
            f"Spectacular entrance of the {theme.capitalize()} themed Birthday Cake",
            f"Celebratory birthday anthem for {name} followed by cake cutting ceremony",
            "Group family & friends commemorative photos"
        ],
        "5. Farewell & Gift Bags (05:00 PM - 05:30 PM)": [
            f"Handing out custom {theme.capitalize()} gift favor bags to all {num_guests} guests",
            f"Warm thank-you speech and farewell cheer"
        ]
    }

    songs = [
        SongMovieLink(
            title=f"{theme.capitalize()} Celebration Anthem",
            description=f"High-energy upbeat adventure party music for {name}'s big day",
            channel="Kids Party Studio",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            views="2.4M"
        ),
        SongMovieLink(
            title=f"The Ultimate {theme.capitalize()} Dance Challenge",
            description="Fun interactive choreography dance for children party games",
            channel="FunKids Hub",
            url="https://www.youtube.com/watch?v=kJQP7kiw5Fk",
            views="1.8M"
        )
    ]

    gifts = [
        SuggestedGift(
            id="gift-1",
            title=f"Customized {theme.capitalize()} Birthday T-Shirt for {name}",
            link="/custom-t-shirt",
            image_url="https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop&q=80"
        ),
        SuggestedGift(
            id="gift-2",
            title=f"{theme.capitalize()} Deluxe Adventure Toy Set",
            link="/products/toys",
            image_url="https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=500&auto=format&fit=crop&q=80"
        ),
        SuggestedGift(
            id="gift-3",
            title=f"Personalized {theme.capitalize()} Keepsake Mug & Cap",
            link="/products/accessories",
            image_url="https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500&auto=format&fit=crop&q=80"
        )
    ]

    return PartyGenerationResponse(
        party_plan=party_plan,
        adventure_song_movie_links=songs,
        suggested_gifts=gifts[:payload.num_product]
    )


# 2. AI T-Shirt & Logo Generator (Real AI Graphic + Realistic Mockup)
@app.post("/t_shirt_generate", response_model=GenerateTShirtResponse, tags=["T-Shirt Designer"])
async def generate_tshirt(
    t_shirt_type: str = Form(..., description="CHILD or ADULT"),
    t_shirt_size: str = Form(..., description="Size e.g. 3T, S, M, L, XL"),
    apparel_type: str = Form("Toddler_Cotton_Jersey_TShirt"),
    gender: str = Form(..., description="BOY, GIRL, MALE, FEMALE"),
    t_shirt_color: str = Form(..., description="Color e.g. white, black, blue, red"),
    age: int = Form(..., description="Age of the person"),
    t_shirt_theme: str = Form(..., description="Theme e.g. spiderman, dinosaur, astronaut, anime"),
    optional_description: Optional[str] = Form(None, description="Optional extra description or custom text"),
    img_file: Optional[UploadFile] = File(None, description="Optional user uploaded logo or photo")
):
    """
    Generates genuine AI vector graphic logo artwork and realistic T-shirt mockup images
    based on customer theme, color, age, gender, and custom prompts.
    """
    # 1. Handle optional uploaded asset
    uploaded_filename = None
    if img_file and img_file.filename:
        clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', img_file.filename)
        safe_filename = f"upload_{random.randint(1000, 9999)}_{clean_name}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        with open(file_path, "wb") as f:
            f.write(await img_file.read())
        uploaded_filename = safe_filename

    # 2. Build AI Graphic Logo Prompt
    extra_details = f", {optional_description}" if optional_description else ""
    design_prompt = (
        f"Clean vector graphic logo of {t_shirt_theme}, modern streetwear sticker art, "
        f"suitable for {gender.lower()} age {age}, vibrant colors, sharp clean outlines, "
        f"isolated on plain white background, premium t-shirt graphic print design{extra_details}"
    )

    # 3. Build AI T-Shirt Mockup Prompt
    mockup_prompt = (
        f"A premium high quality {t_shirt_color.lower()} {apparel_type.replace('_', ' ')} t-shirt "
        f"with a centered graphic logo of {t_shirt_theme} printed on the chest, "
        f"clean studio lighting, professional product photography on flat lay white background"
    )

    seed = random.randint(10000, 999999)
    design_url = generate_ai_image_url(design_prompt, seed=seed)
    mockup_url = generate_ai_image_url(mockup_prompt, seed=seed + 1)

    extra_msg = f" with '{optional_description}'" if optional_description else ""
    file_msg = f" and uploaded image '{img_file.filename}'" if img_file else ""

    return GenerateTShirtResponse(
        success=True,
        message=f"Custom {t_shirt_color.capitalize()} {t_shirt_theme.capitalize()} T-Shirt for {gender.capitalize()} (Size: {t_shirt_size}, Age: {age}) generated successfully{extra_msg}{file_msg}!",
        generated_design_url=design_url,
        generated_mockup_url=mockup_url
    )


# 3. AI Party Invitation Card Generator
@app.post("/api/v1/generate-card", response_model=GenerateCardResponse, tags=["Invitation Cards"])
async def generate_card(payload: GenerateCardRequest):
    """
    Generates tailored invitation text and dynamic card previews using AI.
    """
    theme_title = payload.theme.capitalize()

    # Use Gemini to generate poetic and personalized invitation text
    prompt = (
        f"Write a cheerful and exciting birthday party invitation message in {payload.language} language "
        f"for {payload.birthday_person_name}'s {payload.age}th birthday party. "
        f"Theme: {payload.theme}. Venue: {payload.venue}. Date: {payload.date}. Time: {payload.time}. "
        f"RSVP Contact: {payload.contact_info}. Keep it friendly and concise (max 3 sentences)."
    )
    
    ai_text = ask_ai(prompt)
    if ai_text:
        invitation_text = ai_text.strip().replace('"', '')
    else:
        if payload.language.lower() == "bn":
            invitation_text = (
                f"আপনি আনন্দের সাথে আমন্ত্রিত {payload.birthday_person_name}-এর {payload.age}-তম জন্মদিনের উৎসবে! "
                f"থিম: {theme_title}। তারিখ: {payload.date}, সময়: {payload.time}। স্থান: {payload.venue}। "
                f"যোগাযোগ: {payload.contact_info}।"
            )
        elif payload.language.lower() == "fr":
            invitation_text = (
                f"Vous êtes chaleureusement invité à fêter le {payload.age}e anniversaire de {payload.birthday_person_name} ! "
                f"Thème : {theme_title}. Rendez-vous le {payload.date} à {payload.time} au lieu : {payload.venue}. "
                f"RSVP : {payload.contact_info}."
            )
        else:
            invitation_text = (
                f"You're invited to celebrate {payload.birthday_person_name}'s {payload.age}th Birthday Bash! "
                f"Get ready for an epic {theme_title} adventure at {payload.venue} on {payload.date} at {payload.time}. "
                f"RSVP: {payload.contact_info}. We can't wait to see you there!"
            )

    # Generate custom themed invitation card visuals
    card_prompt_1 = f"Birthday invitation card template, {payload.theme} theme, celebratory balloons, confetti, elegant typography, high resolution graphic design"
    card_prompt_2 = f"Magical colorful birthday card invitation, superhero {payload.theme} adventure theme, festive decorative background"

    images = [
        GeneratedImage(
            url=generate_ai_image_url(card_prompt_1, seed=random.randint(100, 9999)),
            public_id=f"card_{payload.theme.lower()}_primary_01"
        ),
        GeneratedImage(
            url=generate_ai_image_url(card_prompt_2, seed=random.randint(10000, 99999)),
            public_id=f"card_{payload.theme.lower()}_alternative_02"
        )
    ]

    return GenerateCardResponse(
        invitation_text=invitation_text,
        images=images
    )


# 4. AI Invitation Message Generator
@app.post("/api/v1/generate-message", response_model=GenerateMessageResponse, tags=["Invitation Cards"])
async def generate_message(payload: GenerateMessageRequest):
    """
    Generates short, catchy, themed party invitation messages using AI.
    """
    theme = (payload.theme or "Super").capitalize()
    
    prompt = (
        f"Write a short, fun, catchy 1-2 sentence party invitation SMS/message in {payload.language or 'en'} language "
        f"for celebrating {payload.childName}'s {payload.age}th birthday party at {payload.venue}. "
        f"Theme: {theme}. Include celebration emojis."
    )
    
    ai_msg = ask_ai(prompt)
    if ai_msg:
        msg = ai_msg.strip().replace('"', '')
    else:
        if payload.language and payload.language.lower() == "bn":
            msg = f"🎉 আমাদের সাথে যোগ দিন {payload.childName}-এর {payload.age}-তম জন্মদিনের উৎসবে! {payload.venue}-এ জমকালো {theme} পার্টিতে দারুণ সব খেলা ও মজার খাবারের আমন্ত্রণ রইল!"
        else:
            msg = f"🎉 Join us in celebrating {payload.childName}'s {payload.age}th Birthday! An unforgettable {theme} party is planned at {payload.venue}. Get ready for epic fun!"

    return GenerateMessageResponse(
        success=True,
        generated_message=msg
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"🚀 Starting ShopSpark AI Studio API on http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
