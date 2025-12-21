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
    print("🤖 AI Thinking... Generating Simple & Brutal Content...")
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # --- 70% WEALTH & SUCCESS TOPICS ---
    financial_themes = [
        "Escaping the 9-5 Matrix", 
        "Salary is a Trap", 
        "Poor vs Rich Mindset", 
        "Assets vs Liabilities", 
        "Inflation Steals Your Money",
        "The Rule of the 1%",
        "Why You Are Still Broke",
        "Business vs Job",
        "Financial Discipline"
    ]

    # --- 30% DARK TRUTHS & PSYCHOLOGY TOPICS ---
    dark_themes = [
        "Dark Psychology of Power", 
        "Why Being Nice Fails", 
        "Trust Nobody", 
        "Cold Stoicism", 
        "Female Nature (Red Pill)",
        "Loneliness of Success",
        "Control Your Emotions"
    ]

    # PROBABILITY LOGIC: 70% chance for Finance, 30% for Dark
    if random.random() < 0.70:
        theme = random.choice(financial_themes)
        category = "WEALTH"
    else:
        theme = random.choice(dark_themes)
        category = "TRUTH"

    prompt = f"""
    You are a Ruthless Billionaire Mentor (Andrew Tate style).
    Theme: {theme}
    Category: {category}

    ### CRITICAL RULE (LANGUAGE):
    ❌ NO BIG WORDS (e.g., Masquerading, Inevitable, Masquerade).
    ✅ USE SIMPLE STREET ENGLISH (e.g., Faking, Real, Trap, Lie).
    Make it punchy. A 10-year-old should feel the pain of the truth.

    ### THE FLOW (Cliffhanger + Slap):
    HOOK: A suspended sentence. Make them curious. (e.g., "The bank is lying...", "Stop being kind...")
    BODY: The brutal punchline.

    ### EXAMPLES (Simple English):
    (Wealth):
    Hook: You will stay poor if...
    Body: You keep buying things to impress people.

    (Wealth):
    Hook: A salary is just a bribe...
    Body: To make you forget your dreams.

    (Dark Truth):
    Hook: People don't respect kindness...
    Body: They respect power and money.

    ### OUTPUT FORMAT (Strictly 5 parts):
    HOOK: [Max 7 words. Simple English. End with "..."]
    BODY: [Max 12 words. Harsh truth. Simple words.]
    TITLE: [Clickbait Title, max 60 chars, 1 emoji, NO hashtags]
    DESCRIPTION: [2 lines explaining the lesson. Add 5-6 hashtags.]
    TAGS: [20 high-traffic keywords: money, business, sigma, rich, motivation]
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Default Fail-safe
        data = {
            "HOOK": "Stop trusting your friends...",
            "BODY": "They secretly want you to fail.",
            "TITLE": f"Trust No One 👁️",
            "DESCRIPTION": f"Focus on yourself. #billionaire #truth #{theme.replace(' ', '')}",
            "TAGS": "motivation, dark psychology, business, sigma, viral"
        }

        lines = text.split('\n')
        current_key = None
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
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
    current_y = int(VIDEO_SIZE[1] * 0.40)

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

def upload_short(file_path, data):
    youtube = authenticate_youtube()
    print("🚀 Uploading to YouTube...")

    tag_list = [tag.strip() for tag in data["TAGS"].split(',')]
    if "shorts" not in tag_list: tag_list.append("shorts")
    
    final_title = data["TITLE"]
    if len(final_title) > 100: final_title = final_title[:97] + "..."

    request_body = {
        "snippet": {
            "title": final_title,
            "description": data["DESCRIPTION"],
            "tags": tag_list,
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"📊 Upload progress: {int(status.progress() * 100)}%")

    print(f"✅ Upload Complete! ID: {response.get('id')}")

# -------- MAIN --------
if __name__ == "__main__":
    video_data = create_video()
    try:
        upload_short(OUTPUT_FILE, video_data)
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
