import os
import random
import textwrap
import time
import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from moviepy.editor import ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont

# --- NEW IMPORTS FOR YOUTUBE ---
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
VIDEO_SIZE = (720, 1280)  # 9:16 Portrait
FONT_PATH = "arial.ttf"   # Make sure this exists

# Visual Settings
TOP_MARGIN = 150          
LABEL_HEIGHT = 160        
HOOK_FONT_SIZE = 40       
BODY_FONT_SIZE = 50       
MAX_CHARS_BODY = 24       

# Timing
FADE_IN = 1.0
HOLD_DURATION = 2.0
FADE_OUT = 1.0

# YouTube API Scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# -------- STEP 1: Generate Content & Metadata with Gemini --------
def get_dynamic_content():
    print("🤖 AI Thinking... Generating Script & Metadata...")
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    themes = ["Stoic Reality", "Harsh Truths", "Discipline", "Focus", "Men's Growth", "Financial Freedom", "Lone Wolf Mindset", "Psychology Facts"]
    theme = random.choice(themes)

    # UPDATED PROMPT: Ab hum Title, Desc, Tags bhi maang rahe hain
    prompt = f"""
    You are a YouTube Viral Strategist. Generate content for a Short about: {theme}.
    
    Strictly follow this output format (5 parts):
    HOOK: [Ultra-suspenseful intro, max 6 words,
    e.g. "Nobody tells you this...", Nobody told me that... , It hit me hard when i realized...,This won't make sense until..
    (use similar to this type , dont use same and dont use similar too everytime this are just a few examples)]
    BODY: [Deep punchy line, max 12 words]
    TITLE: [Clickbait Title for YouTube Shorts, max 60 chars, include 1-2 emoji, 2-3 HASHTAGS in title]
    DESCRIPTION: [3-5 sentences explaining the deeper meaning. Then add 5-6 unique hashtags relevant to this specific quote.]
    TAGS: [List of 20-30 comma-separated high-traffic keywords/search-oriented tags related to this specific topic]
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Default values (Fail-safe)
        data = {
            "HOOK": "Wait for it...",
            "BODY": "Work hard in silence.",
            "TITLE": f"This changed my life 🤯",
            "DESCRIPTION": f"Subscribe for more! #motivation #{theme.replace(' ', '')}",
            "TAGS": "motivation, discipline, growth, viral"
        }

        # Parsing the AI response
        lines = text.split('\n')
        current_key = None
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Check for keys and remove the "KEY:" part
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
                # Description can be multi-line, so append extra lines
                data["DESCRIPTION"] += "\n" + line

        print(f"🔹 Theme: {theme}")
        print(f"🔹 Hook: {data['HOOK']}")
        print(f"🔹 Title: {data['TITLE']}")
        
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
        font_hook = ImageFont.load_default()
        font_body = ImageFont.load_default()

    # Draw White Label
    draw.rectangle([(0, TOP_MARGIN), (VIDEO_SIZE[0], TOP_MARGIN + LABEL_HEIGHT)], fill="white")

    # Hook Text
    bbox = draw.textbbox((0, 0), hook_text, font=font_hook)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x_hook = (VIDEO_SIZE[0] - text_w) / 2
    y_hook = TOP_MARGIN + (LABEL_HEIGHT - text_h) / 2
    draw.text((x_hook, y_hook), hook_text, font=font_hook, fill="black")

    # Body Text
    wrapped_lines = textwrap.wrap(body_text, width=MAX_CHARS_BODY)
    line_heights = []
    total_h = 0
    padding = 20

    for line in wrapped_lines:
        bbox = draw.textbbox((0, 0), line, font=font_body)
        h = bbox[3] - bbox[1]
        line_heights.append(h)
        total_h += h + padding

    start_of_black_area = TOP_MARGIN + LABEL_HEIGHT
    available_height = VIDEO_SIZE[1] - start_of_black_area
    current_y = start_of_black_area + (available_height - total_h) / 2

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
        # Fallback if API fails completely
        data = {"HOOK": "Error", "BODY": "Try again later", "TITLE": "Error", "DESCRIPTION": "", "TAGS": ""}

    img_path = create_styled_image(data["HOOK"], data["BODY"])
    
    total_duration = FADE_IN + HOLD_DURATION + FADE_OUT
    clip = ImageClip(img_path).set_duration(total_duration)
    clip = clip.fadein(FADE_IN).fadeout(FADE_OUT)
    final = CompositeVideoClip([clip], size=VIDEO_SIZE)
    
    print("🎬 Rendering Video...")
    final.write_videofile(OUTPUT_FILE, fps=24, codec="libx264")
    
    if os.path.exists(img_path):
        os.remove(img_path)
    print(f"✅ Video Ready: {OUTPUT_FILE}")
    
    return data # Return full data dictionary

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

    # Preparing Tags (converting string to list)
    tag_list = [tag.strip() for tag in data["TAGS"].split(',')]
    
    # Add standard shorts tags if not present
    if "shorts" not in tag_list: tag_list.append("shorts")
    
    # Title Truncate (just in case AI goes crazy)
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

    print(f"✅ Upload Complete! https://www.youtube.com/watch?v={response.get('id')}")

# -------- MAIN --------
if __name__ == "__main__":
    # 1. Video Banao & Data Lao
    video_data = create_video()
    
    # 2. Upload Karo (New Dynamic Data ke saath)
    try:
        upload_short(OUTPUT_FILE, video_data)
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
