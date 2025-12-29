import os
import random
import textwrap
import time
import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from moviepy.editor import ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont

# --- IMPORTS FOR YOUTUBE UPLOAD ---
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# -------- CONFIGURATION --------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Output Settings
OUTPUT_FILE = "viral_short_v3.mp4"
VIDEO_SIZE = (1080, 1920) # 1080p Full HD
FONT_PATH = "arialbd.ttf" # <--- IMPORTANT: Ye file honi chahiye

# Visual Settings
# 13% of 1920 height = 250px
TOP_MARGIN = 250          
LABEL_HEIGHT = 160        # White bar height
HOOK_FONT_SIZE = 55       # Thoda bada kiya kyuki resolution 1080p hai
BODY_FONT_SIZE = 65       # Thoda bada kiya 1080p ke liye
MAX_CHARS_BODY = 24       

# Timing
FADE_IN = 1.0
HOLD_DURATION = 2.0
FADE_OUT = 1.0

# YouTube API Scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# -------- STEP 1: Generate Content & Metadata --------
def get_dynamic_content():
    print("🤖 AI Thinking... Generating Cliffhanger + Growth Content...")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    financial_themes = [
        "Starting Before You Feel Ready",
        "Consistency Beats Motivation",
        "Discipline Over Talent",
        "Long Term Thinking",
        "Work Ethic",
        "Focus and Execution",
        "Building Momentum",
        "Delayed Gratification"
    ]

    dark_themes = [
        "Personal Responsibility",
        "Hard Truths About Progress",
        "Why Most People Quit",
        "Comfort vs Growth",
        "Self Control",
        "Facing Reality"
    ]

    if random.random() < 0.65:
        theme = random.choice(financial_themes)
        category = "GROWTH"
    else:
        theme = random.choice(dark_themes)
        category = "TRUTH"

    prompt = f"""
You are a calm but brutally honest mentor.
You challenge the viewer without hate, insults, or shaming.
Your goal is to push action, not guilt.

Theme: {theme}
Category: {category}

### CRITICAL RULES (LANGUAGE):
❌ NO big words.
❌ NO hate, insults, or blaming language.
❌ Do NOT use words like trap, scam, lie, bribe.
✅ Use simple, clear, direct English.

### TONE RULE:
Hooks can be intense, emotional, or painful.
Body must be grounded, constructive, and growth-focused.

### THE FLOW (Cliffhanger + Direction):
HOOK: Strong emotional cliffhanger that stops scrolling.
BODY: A realization or action that helps growth.

### HOOK STYLE (STRICT – follow this pattern):
- It hit me when I realized…
- Nobody told me that…
- You won’t get it until you notice…
- Tthing changed the moment I learned…
- This might hurt a bit…
- You won’t unhear this…
- Wait till you realise that…
- Here’s the part nobody talks about…
- I never understood it until…
- This one stings when you think about…

### EXAMPLES (STYLE REFERENCE):
Hook: This might hurt a bit…
Body: Comfort delays the life you want.

Hook: Nobody told me that…
Body: Starting messy beats waiting perfect.

Hook: It hit different when I realised…
Body: Discipline beats motivation every time.

### BODY SAFETY RULE:
If the body only makes the viewer feel bad, rewrite it.
It must push action, not guilt.

### OUTPUT FORMAT (STRICT – 5 PARTS ONLY):
HOOK: [Max 5-7 words. End with "..."]
BODY: [Max 10-12 words. Actionable or reflective.]
TITLE: [Max 60 chars, 2–3 emojis, 2–4 hashtags]
DESCRIPTION: [2 short lines. Add 5–6 hashtags.]
TAGS: [25–30 high-traffic keywords: motivation, discipline, success, mindset, growth]
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        data = {
            "HOOK": "This might hurt a bit...",
            "BODY": "Growth starts when comfort ends.",
            "TITLE": "This One Stings 💭 #mindset",
            "DESCRIPTION": "A reminder you needed today.\n#growth #discipline #mindset #motivation",
            "TAGS": "motivation, mindset, discipline, growth, success, shorts, self improvement"
        }

        lines = text.split('\n')
        current_key = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("HOOK:"):
                current_key = "HOOK"
                data["HOOK"] = line.replace("HOOK:", "").strip()
            elif line.startswith("BODY:"):
                current_key = "BODY"
                data["BODY"] = line.replace("BODY:", "").strip()
            elif line.startswith("TITLE:"):
                current_key = "TITLE"
                data["TITLE"] = line.replace("TITLE:", "").strip().replace('"', '')
            elif line.startswith("DESCRIPTION:"):
                current_key = "DESCRIPTION"
                data["DESCRIPTION"] = line.replace("DESCRIPTION:", "").strip()
            elif line.startswith("TAGS:"):
                current_key = "TAGS"
                data["TAGS"] = line.replace("TAGS:", "").strip()
            elif current_key == "DESCRIPTION":
                data["DESCRIPTION"] += "\n" + line

        print(f"🔹 Theme: {theme}")
        print(f"🔹 Hook: {data['HOOK']}")
        print(f"🔹 Body: {data['BODY']}")

        return data, theme

    except Exception as e:
        print(f"❌ API Error: {e}")
        return None, theme


# -------- STEP 2: Create the Image --------
def create_styled_image(hook_text, body_text):
    img = Image.new("RGB", VIDEO_SIZE, color="black")
    draw = ImageDraw.Draw(img)

    try:
        font_hook = ImageFont.truetype(FONT_PATH, HOOK_FONT_SIZE)
        font_body = ImageFont.truetype(FONT_PATH, BODY_FONT_SIZE)
    except:
        print("⚠️ Custom font not found! Using default.")
        font_hook = ImageFont.load_default()
        font_body = ImageFont.load_default()

    # --- 1. DRAW TOP WHITE LABEL (13% Down) ---
    draw.rectangle([(0, TOP_MARGIN), (VIDEO_SIZE[0], TOP_MARGIN + LABEL_HEIGHT)], fill="white")

    # Center Hook Text inside Label
    bbox = draw.textbbox((0, 0), hook_text, font=font_hook)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x_hook = (VIDEO_SIZE[0] - text_w) / 2
    # Vertically center inside the white bar
    y_hook = TOP_MARGIN + (LABEL_HEIGHT - text_h) / 2 - 8 # -10 for optical adjustment
    draw.text((x_hook, y_hook), hook_text, font=font_hook, fill="black")

    # --- 2. DRAW BODY TEXT (40% Down) ---
    wrapped_lines = textwrap.wrap(body_text, width=MAX_CHARS_BODY)
    line_heights = []
    padding = 25

    for line in wrapped_lines:
        bbox = draw.textbbox((0, 0), line, font=font_body)
        h = bbox[3] - bbox[1]
        line_heights.append(h)

    # Start Position: 40% of Height (approx 768px)
    current_y = int(VIDEO_SIZE[1] * 0.44)

    for i, line in enumerate(wrapped_lines):
        bbox = draw.textbbox((0, 0), line, font=font_body)
        w = bbox[2] - bbox[0]
        x = (VIDEO_SIZE[0] - w) / 2
        draw.text((x, current_y), line, font=font_body, fill="white")
        current_y += line_heights[i] + padding

    temp_path = "temp_frame_v3.png"
    img.save(temp_path)
    return temp_path

# -------- STEP 3: Animation --------
def create_video():
    data, theme = get_dynamic_content()
    
    if not data:
        print("⚠️ AI Data Failed! Using Fallback Content.")
        data = {
            "HOOK": "Never forget this...",
            "BODY": "Consistency is what transforms average into excellence.",
            "TITLE": "The Secret to Success 💯 #shorts",
            "DESCRIPTION": "Daily motivation for you. Keep grinding! #discipline #growth #mindset",
            "TAGS": "motivation, discipline, hustle, viral, shorts"
        }

    img_path = create_styled_image(data["HOOK"], data["BODY"])
    
    total_duration = FADE_IN + HOLD_DURATION + FADE_OUT
    clip = ImageClip(img_path).set_duration(total_duration)
    clip = clip.fadein(FADE_IN).fadeout(FADE_OUT)
    final = CompositeVideoClip([clip], size=VIDEO_SIZE)
    
    print("🎬 Rendering Video (1080p)...")
    final.write_videofile(OUTPUT_FILE, fps=24, codec="libx264")
    
    if os.path.exists(img_path):
        os.remove(img_path)
    print(f"✅ Video Ready: {OUTPUT_FILE}")
    
    return data

# -------- STEP 4: YouTube Upload --------
def authenticate_youtube():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())
            
    return build("youtube", "v3", credentials=creds)

# -------- STEP 4: YouTube Upload --------
def authenticate_youtube():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())
            
    return build("youtube", "v3", credentials=creds)

# -------- MAIN --------
if __name__ == "__main__":
    video_data = create_video()
    try:
        upload_short(OUTPUT_FILE, video_data)
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
