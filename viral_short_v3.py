import os
import random
import textwrap
import time
import datetime
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

# ---> IMPORTANT: Ab 2 fonts chahiye. Ek regular, ek bold <---
FONT_REGULAR_PATH = "arial.ttf" 
FONT_BOLD_PATH = "arialbd.ttf"  

# Visual Settings
FONT_SIZE = 50            # Font size for both regular and bold
LEFT_MARGIN = 120         # Left space to match reference image
RIGHT_MARGIN = 120        # Right space for word wrapping
LINE_SPACING = 30         # Space between wrapped lines
PARAGRAPH_SPACING = 50    # Space between new lines (\n)

# Timing
FADE_IN = 1.0
HOLD_DURATION = 3.0       # Thoda badha diya taaki padhne ka time mile
FADE_OUT = 1.0

# YouTube API Scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# -------- STEP 1: Generate Content & Metadata --------
def get_dynamic_content():
    print("🤖 AI Thinking... Generating Fresh Content...")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # -------- MICRO NICHE THEME POOLS (Truncated for brevity, keep your original list) --------
    categories = ["GROWTH", "TRUTH", "MONEY", "MINDSET", "HABITS", "LONELY_GRIND"]
    theme = "Starting Before You Feel Ready" # Random fallback
    category = random.choice(categories)
    seed = random.randint(10000, 99999)

    # UPDATED PROMPT: Ab AI single QUOTE banayega with **bold** markers
    prompt = f"""
You are a quiet mentor who speaks from experience.
You challenge the viewer without hate, insults, or shaming.

Theme: {theme}
Category: {category}
Unique Seed: {seed}

### CRITICAL RULES (LANGUAGE):
❌ NO big words or fancy vocabulary.
❌ NO hate, insults, or blaming language.
✅ Use simple, casual, everyday English.
✅ Sound like a REAL PERSON making a deep realization.

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

### OUTPUT FORMAT (STRICT – 4 PARTS ONLY):
QUOTE: [Your 3-4 line quote with **bold** markers. Use \n for new lines if needed, or just type on new lines]
TITLE: [Catchy urgency title, emojis, hashtags]
DESCRIPTION: [2-4 short lines. Add 5-6 hashtags.]
TAGS: [25-30 keywords separated by comma]
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Fallback data in case of error
        data = {
            "QUOTE": "The journey feels **lonely**,\nbecause you are leveling **up**,\nand not everyone is meant to come **with** you.",
            "TITLE": "You Need To Hear This 🔥💯 #shorts",
            "DESCRIPTION": "A reminder you needed today.\n#growth #discipline #mindset #motivation",
            "TAGS": "motivation, mindset, discipline, growth, success, shorts, self improvement"
        }

        lines = text.split('\n')
        current_key = None
        temp_quote = []

        for line in lines:
            line = line.strip()
            if not line: continue

            if line.startswith("QUOTE:"):
                current_key = "QUOTE"
                temp_quote.append(line.replace("QUOTE:", "").strip())
            elif line.startswith("TITLE:"):
                current_key = "TITLE"
                data["TITLE"] = line.replace("TITLE:", "").strip().replace('"', '')
            elif line.startswith("DESCRIPTION:"):
                current_key = "DESCRIPTION"
                data["DESCRIPTION"] = line.replace("DESCRIPTION:", "").strip()
            elif line.startswith("TAGS:"):
                current_key = "TAGS"
                data["TAGS"] = line.replace("TAGS:", "").strip()
            elif current_key == "QUOTE":
                temp_quote.append(line)
            elif current_key == "DESCRIPTION":
                data["DESCRIPTION"] += "\n" + line

        if temp_quote:
            data["QUOTE"] = "\n".join(temp_quote)

        if len(data["TITLE"]) > 100:
            data["TITLE"] = data["TITLE"][:97] + "..."

        print(f"🔹 Quote:\n{data['QUOTE']}")
        return data, theme

    except Exception as e:
        print(f"❌ API Error: {e}")
        return None, theme

# -------- STEP 2: Create the Image (UPDATED FOR MIXED FONTS & CENTERING) --------
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

    # Helper function to measure and draw text
    def render_mixed_text(draw_obj, text, start_y, execute_draw=False):
        lines = text.split('\n')
        current_y = start_y
        
        # Get height of a standard letter to maintain line height consistency
        bbox_standard = font_reg.getbbox("A")
        standard_h = bbox_standard[3] - bbox_standard[1]
        space_w = font_reg.getlength(" ")

        for line in lines:
            words = line.split(' ')
            current_x = LEFT_MARGIN
            
            for word in words:
                if not word: continue
                
                # Detect if word should be bold
                is_bold = False
                clean_word = word
                if "**" in word:
                    is_bold = True
                    clean_word = word.replace("**", "")

                font_to_use = font_bold if is_bold else font_reg
                
                # Measure word width
                word_w = font_to_use.getlength(clean_word)

                # Word Wrapping Logic
                if current_x + word_w > LEFT_MARGIN + max_text_width:
                    current_x = LEFT_MARGIN
                    current_y += standard_h + LINE_SPACING

                # Draw the word
                if execute_draw and draw_obj:
                    draw_obj.text((current_x, current_y), clean_word, font=font_to_use, fill="white")
                
                # Move X position for next word
                current_x += word_w + space_w

            # Add paragraph spacing after completing a line from the original text
            current_y += standard_h + PARAGRAPH_SPACING

        return current_y - start_y

    # Pass 1: Measure total height required for the text block
    total_text_height = render_mixed_text(None, quote_text, 0, execute_draw=False)

    # Pass 2: Calculate true vertical center and draw
    start_y = (VIDEO_SIZE[1] - total_text_height) / 2
    
    # Slight optical adjustment (move slightly up for better viewing on phones)
    start_y -= 100 

    render_mixed_text(draw, quote_text, start_y, execute_draw=True)

    temp_path = "temp_frame_v3.png"
    img.save(temp_path)
    return temp_path


def get_random_music(duration):
    music_dir = "music"
    if not os.path.exists(music_dir): return None
    tracks = [os.path.join(music_dir, f) for f in os.listdir(music_dir) if f.lower().endswith((".mp3", ".wav"))]
    if not tracks: return None

    track_path = random.choice(tracks)
    audio = AudioFileClip(track_path)
    if audio.duration < duration: audio = afx.audio_loop(audio, duration=duration)
    audio = audio.subclip(0, duration).volumex(0.25)
    return audio

# -------- STEP 3: Animation --------
def create_video():
    data, theme = get_dynamic_content()
    
    if not data:
        data = {
            "QUOTE": "Consistency is what **transforms**,\naverage into **excellence**.",
            "TITLE": "The Secret to Success 💯 #shorts",
            "DESCRIPTION": "Daily motivation for you. Keep grinding! #discipline #growth",
            "TAGS": "motivation, discipline, hustle, viral, shorts"
        }

    # Pass the new single QUOTE to the image creator
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

# -------- STEP 4: YouTube Upload (Unchanged) --------
def authenticate_youtube():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token: token.write(creds.to_json())
            
    return build("youtube", "v3", credentials=creds)

def upload_short(file_path, data):
    try:
        youtube = authenticate_youtube()
        print("🚀 Uploading to YouTube...")
        
        tag_list = [tag.strip() for tag in data["TAGS"].split(',')]
        if "shorts" not in tag_list: tag_list.append("shorts")
        
        request_body = {
            "snippet": {
                "title": data["TITLE"],
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
        request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status: print(f"📊 Upload progress: {int(status.progress() * 100)}%")
            
        print(f"✅ Upload Complete! ID: {response.get('id')}")
    except Exception as e:
        print(f"❌ Upload Failed: {e}")

# -------- MAIN --------
if __name__ == "__main__":
    video_data = create_video()
    try:
        # Uncomment below line to enable actual upload
        # upload_short(OUTPUT_FILE, video_data)
        pass
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
