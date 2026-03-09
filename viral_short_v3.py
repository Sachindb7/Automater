import os
import random
import textwrap
import time
import datetime
import re
from dotenv import load_dotenv
import google.generativeai as genai
from moviepy.editor import ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import AudioFileClip, afx

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

# Upload Settings
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"

# ---> IMPORTANT: Ab 2 fonts chahiye. Ek regular, ek bold <---
FONT_REGULAR_PATH = "arial.ttf" 
FONT_BOLD_PATH = "arialbd.ttf"  

# Visual Settings
FONT_SIZE = 50
LEFT_MARGIN = 120
RIGHT_MARGIN = 120
LINE_SPACING = 30
PARAGRAPH_SPACING = 50

# Timing
FADE_IN = 0.0
HOLD_DURATION = 4.0
FADE_OUT = 0.0

# YouTube API Scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


# ✅ FIX: Helper function to clean Gemini's messy formatting
def clean_line(line):
    """Remove **, ##, *, extra spaces from line for key detection"""
    cleaned = line.strip()
    cleaned = cleaned.replace("**", "")
    cleaned = cleaned.replace("##", "")
    cleaned = cleaned.replace("*", "")
    cleaned = cleaned.strip()
    return cleaned


def extract_value(line, key):
    """Extract value after KEY: from line, handling **, ##, quotes etc."""
    cleaned = clean_line(line)
    # Find the key position (case insensitive)
    pattern = re.compile(re.escape(key) + r'\s*:\s*', re.IGNORECASE)
    match = pattern.search(cleaned)
    if match:
        value = cleaned[match.end():].strip()
        # Remove surrounding quotes if any
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        return value
    return None


def detect_key(line):
    """Detect which key a line starts with, ignoring ** and ##"""
    cleaned = clean_line(line).upper()
    if cleaned.startswith("QUOTE"):
        return "QUOTE"
    elif cleaned.startswith("TITLE"):
        return "TITLE"
    elif cleaned.startswith("DESCRIPTION"):
        return "DESCRIPTION"
    elif cleaned.startswith("TAGS"):
        return "TAGS"
    return None


# -------- STEP 1: Generate Content & Metadata --------
def get_dynamic_content():
    print("🤖 AI Thinking... Generating Fresh Content...")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    categories = ["GROWTH", "TRUTH", "MONEY", "MINDSET", "HABITS", "LONELY_GRIND"]
    theme = "Starting Before You Feel Ready"
    category = random.choice(categories)
    seed = random.randint(10000, 99999)

    prompt = f"""
You are a quiet mentor who speaks from experience.
You challenge the viewer without hate, insults, or shaming.

Theme: {theme}
Category: {category}
Unique Seed: {seed}

### CRITICAL RULES (LANGUAGE):
- NO big words or fancy vocabulary.
- NO hate, insults, or blaming language.
- Use simple, casual, everyday English.
- Sound like a REAL PERSON making a deep realization.

### QUOTE RULES (VERY STRICT to match the visual style):
- Generate a single continuous thought broken into 3 to 4 short lines.
- The tone should be slightly melancholic but empowering.
- Use ** around 1 or 2 high-impact words per line to make them bold. 
- Example format:
"Sometimes the **hardest** paths,
lead to the most **beautiful** destinations,
especially when you walk **alone**."

### TITLE & METADATA RULES:
- Catchy, urgency-based, under 100 characters.
- 2-3 emojis, 1-2 hashtags.

### OUTPUT FORMAT (STRICT - 4 PARTS ONLY, NO extra formatting):
QUOTE: [Your 3-4 line quote with **bold** markers]
TITLE: [Catchy urgency title, emojis, hashtags]
DESCRIPTION: [2-4 short lines. Add 5-6 hashtags.]
TAGS: [25-30 keywords separated by comma]
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # ✅ DEBUG: Print raw AI response
        print("=" * 50)
        print("📋 RAW AI RESPONSE:")
        print(text)
        print("=" * 50)

        # Fallback data
        data = {
            "QUOTE": "The journey feels **lonely**,\nbecause you are leveling **up**,\nand not everyone is meant to come **with** you.",
            "TITLE": "You Need To Hear This 🔥💯 #shorts",
            "DESCRIPTION": "A reminder you needed today.\n#growth #discipline #mindset #motivation #shorts",
            "TAGS": "motivation, mindset, discipline, growth, success, shorts, self improvement"
        }

        lines = text.split('\n')
        current_key = None
        temp_quote = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # ✅ FIX: Use smart key detection (handles **, ##, etc.)
            detected = detect_key(stripped)

            if detected == "QUOTE":
                current_key = "QUOTE"
                val = extract_value(stripped, "QUOTE")
                if val:
                    temp_quote.append(val)
            elif detected == "TITLE":
                current_key = "TITLE"
                val = extract_value(stripped, "TITLE")
                if val:
                    data["TITLE"] = val.replace('"', '')
            elif detected == "DESCRIPTION":
                current_key = "DESCRIPTION"
                val = extract_value(stripped, "DESCRIPTION")
                if val:
                    data["DESCRIPTION"] = val
            elif detected == "TAGS":
                current_key = "TAGS"
                val = extract_value(stripped, "TAGS")
                if val:
                    data["TAGS"] = val
            elif current_key == "QUOTE":
                # Quote ki continuation lines
                clean = stripped.replace('"', '').strip()
                if clean:
                    temp_quote.append(clean)
            elif current_key == "DESCRIPTION":
                data["DESCRIPTION"] += "\n" + stripped
            elif current_key == "TAGS":
                # Tags continuation (rare but handle it)
                data["TAGS"] += ", " + stripped

        if temp_quote:
            data["QUOTE"] = "\n".join(temp_quote)

        if len(data["TITLE"]) > 100:
            data["TITLE"] = data["TITLE"][:97] + "..."

        # ✅ DEBUG: Print parsed data
        print("\n✅ PARSED DATA:")
        print(f"   TITLE: {data['TITLE']}")
        print(f"   QUOTE:\n   {data['QUOTE']}")
        print(f"   DESCRIPTION: {data['DESCRIPTION'][:80]}...")
        print(f"   TAGS: {data['TAGS'][:80]}...")
        print()

        return data, theme

    except Exception as e:
        print(f"❌ API Error: {e}")
        return None, theme


# -------- STEP 2: Create the Image --------
def create_styled_image(quote_text):
    img = Image.new("RGB", VIDEO_SIZE, color="black")
    draw = ImageDraw.Draw(img)

    try:
        font_reg = ImageFont.truetype(FONT_REGULAR_PATH, FONT_SIZE)
        font_bold = ImageFont.truetype(FONT_BOLD_PATH, FONT_SIZE)
    except Exception as e:
        print(f"⚠️ Font error: {e}. Using default.")
        font_reg = ImageFont.load_default()
        font_bold = ImageFont.load_default()

    max_text_width = VIDEO_SIZE[0] - LEFT_MARGIN - RIGHT_MARGIN

    def render_mixed_text(draw_obj, text, start_y, execute_draw=False):
        lines = text.split('\n')
        current_y = start_y
        
        bbox_standard = font_reg.getbbox("A")
        standard_h = bbox_standard[3] - bbox_standard[1]
        space_w = font_reg.getlength(" ")

        for line in lines:
            words = line.split(' ')
            current_x = LEFT_MARGIN
            
            for word in words:
                if not word:
                    continue
                
                is_bold = False
                clean_word = word
                if "**" in word:
                    is_bold = True
                    clean_word = word.replace("**", "")

                font_to_use = font_bold if is_bold else font_reg
                word_w = font_to_use.getlength(clean_word)

                if current_x + word_w > LEFT_MARGIN + max_text_width:
                    current_x = LEFT_MARGIN
                    current_y += standard_h + LINE_SPACING

                if execute_draw and draw_obj:
                    draw_obj.text((current_x, current_y), clean_word, font=font_to_use, fill="white")
                
                current_x += word_w + space_w

            current_y += standard_h + PARAGRAPH_SPACING

        return current_y - start_y

    total_text_height = render_mixed_text(None, quote_text, 0, execute_draw=False)
    start_y = (VIDEO_SIZE[1] - total_text_height) / 2
    start_y -= 100 

    render_mixed_text(draw, quote_text, start_y, execute_draw=True)

    temp_path = "temp_frame_v3.png"
    img.save(temp_path)
    return temp_path


def get_random_music(duration):
    music_dir = "music"
    if not os.path.exists(music_dir):
        return None
    tracks = [os.path.join(music_dir, f) for f in os.listdir(music_dir) if f.lower().endswith((".mp3", ".wav"))]
    if not tracks:
        return None

    track_path = random.choice(tracks)
    audio = AudioFileClip(track_path)
    if audio.duration < duration:
        audio = afx.audio_loop(audio, duration=duration)
    audio = audio.subclip(0, duration).volumex(0.25)
    return audio


# -------- STEP 3: Animation --------
def create_video():
    data, theme = get_dynamic_content()
    
    if not data:
        data = {
            "QUOTE": "Consistency is what **transforms**,\naverage into **excellence**.",
            "TITLE": "The Secret to Success 💯 #shorts",
            "DESCRIPTION": "Daily motivation for you. Keep grinding! #discipline #growth #shorts",
            "TAGS": "motivation, discipline, hustle, viral, shorts"
        }

    img_path = create_styled_image(data["QUOTE"])
    
    total_duration = FADE_IN + HOLD_DURATION + FADE_OUT
    clip = ImageClip(img_path).set_duration(total_duration)
    clip = clip.fadein(FADE_IN).fadeout(FADE_OUT)
    final = CompositeVideoClip([clip], size=VIDEO_SIZE)

    music = get_random_music(total_duration)
    if music:
        final = final.set_audio(music)

    final.write_videofile(
        OUTPUT_FILE,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )
    
    if os.path.exists(img_path):
        os.remove(img_path)
    print(f"✅ Video Ready: {OUTPUT_FILE}")
    
    return data


# -------- STEP 4: YouTube Upload --------
def authenticate_youtube():
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Token expired, refreshing...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                print(f"❌ '{CLIENT_SECRET_FILE}' nahi mila!")
                return None
            
            print("🔐 Browser kholega for Google login...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        print("✅ Token saved!")
    
    return build("youtube", "v3", credentials=creds)


def upload_short(file_path, data):
    try:
        youtube = authenticate_youtube()
        
        if youtube is None:
            print("❌ Authentication fail! client_secret.json check karo")
            return
        
        # ✅ FIX: Tags ko properly list mein convert karo
        raw_tags = data.get("TAGS", "motivation, shorts")
        if isinstance(raw_tags, str):
            tag_list = [tag.strip() for tag in raw_tags.split(',') if tag.strip()]
        else:
            tag_list = raw_tags
        
        # Shorts tag ensure karo
        tag_lower = [t.lower() for t in tag_list]
        if "shorts" not in tag_lower:
            tag_list.append("shorts")

        # Title fallback
        title = data.get("TITLE", "Motivation 🔥 #shorts")
        if not title or title.strip() == "":
            title = "You Need To Hear This 🔥💯 #shorts"
        
        # Description fallback
        description = data.get("DESCRIPTION", "Daily motivation #shorts")
        if not description or description.strip() == "":
            description = "A reminder you needed today. #shorts #motivation"
        if "#Shorts" not in description:
            description += "\n\n#Shorts"
        
        # ✅ DEBUG: Print what's being uploaded
        print("\n📋 UPLOADING WITH:")
        print(f"   Title: {title}")
        print(f"   Tags: {tag_list[:10]}...")  # First 10 tags
        print(f"   Description: {description[:60]}...")
        print()
        
        request_body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tag_list,
                "categoryId": "22",
                "defaultLanguage": "en",
                "defaultAudioLanguage": "en",
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            }
        }

        media = MediaFileUpload(
            file_path, 
            mimetype="video/mp4",
            resumable=True, 
            chunksize=256 * 1024
        )
        
        request = youtube.videos().insert(
            part="snippet,status", 
            body=request_body, 
            media_body=media
        )
        
        print("🚀 Uploading to YouTube...")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   📊 Upload: {int(status.progress() * 100)}%")
        
        video_id = response.get('id')
        url = f"https://youtube.com/shorts/{video_id}"
        print(f"✅ Upload Complete!")
        print(f"🔗 URL: {url}")
        
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
        import traceback
        traceback.print_exc()


# -------- MAIN --------
if __name__ == "__main__":
    video_data = create_video()
    
    if video_data:
        upload_short(OUTPUT_FILE, video_data)
    else:
        print("❌ Video data generate nahi hua")
