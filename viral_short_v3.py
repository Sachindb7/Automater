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

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# -------- CONFIGURATION --------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OUTPUT_FILE = "viral_short_v3.mp4"
VIDEO_SIZE = (1080, 1920)

CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"

FONT_REGULAR_PATH = "arial.ttf"
FONT_BOLD_PATH = "arialbd.ttf"

FONT_SIZE = 50
LEFT_MARGIN = 120
RIGHT_MARGIN = 120
LINE_SPACING = 30
PARAGRAPH_SPACING = 50

FADE_IN = 0.5
HOLD_DURATION = 3.0
FADE_OUT = 0.0

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# ============================================================
# 🔥 MASSIVE VARIETY SYSTEM
# ============================================================

THEMES = [
    "The pain of discipline vs the pain of regret",
    "Why your morning routine decides your future",
    "Small daily habits that destroy your life silently",
    "The difference between busy and productive",
    "Why most people quit right before the breakthrough",
    "Why broke people stay broke (mindset trap)",
    "The ugly truth about trading time for money",
    "What rich people never tell you about wealth",
    "Why saving money won't make you rich",
    "The skill nobody teaches you about money",
    "Why your lonely phase is your most powerful phase",
    "The friends you lose when you start growing",
    "Why nobody claps for you until you've already made it",
    "Eating alone, walking alone, winning alone",
    "The silence that builds empires",
    "Stop improving yourself and start accepting yourself",
    "The trap of toxic positivity nobody talks about",
    "Why you feel lost in your 20s (and it's okay)",
    "The version of you that scares you is the real you",
    "Why comfort is the slowest form of suicide",
    "Why some people are only loyal when they need you",
    "The moment you stop chasing people everything changes",
    "Not everyone deserves an explanation from you",
    "People show you who they are - believe them",
    "Why the strongest people have the fewest friends",
    "It's okay to not be okay (but don't stay there)",
    "The weight you carry that nobody sees",
    "Why overthinking is slowly killing your happiness",
    "The art of letting go without giving up",
    "Your worst days are building your best chapters",
    "Why failure is just data, not destiny",
    "The comeback is always stronger than the setback",
    "Nobody remembers average - be unforgettable",
    "Why your biggest flex should be your peace",
    "The graveyard of dreams is full of talented people",
    "Stop waiting for motivation, build momentum instead",
    "The 5 second rule that changed everything",
    "Why your environment matters more than your talent",
    "The lie of 'I'll start tomorrow'",
    "You're not lazy, you're scared",
    "Nobody is coming to save you",
    "Your phone is stealing your future",
    "The people you admire are just regular people who didn't quit",
    "Why being nice is not the same as being kind",
    "You're addicted to distraction and calling it relaxation",
    "The old you has to die for the new you to be born",
    "Why growth feels like breaking apart",
    "You weren't built to fit in, you were built to stand out",
    "The butterfly doesn't miss being a caterpillar",
    "Stop apologizing for evolving",
    "One day or day one - you decide",
    "The clock is ticking whether you move or not",
    "You don't have unlimited tomorrows",
    "Time doesn't wait for your perfect plan",
    "The best time was yesterday, the next best time is now",
    "Stop shrinking yourself to make others comfortable",
    "Your value doesn't decrease based on someone's inability to see your worth",
    "The loudest person in the room is the weakest",
    "Confidence is silent, insecurity is loud",
    "You teach people how to treat you",
    "Use your pain as fuel, not as an excuse",
    "They laughed at you, remember that when you win",
    "The revenge is living well",
    "Build in silence, let success make the noise",
    "Your haters are your biggest fans in disguise",
    "The obstacle is the way",
    "What you resist, persists",
    "The cave you fear to enter holds the treasure you seek",
    "Knowledge speaks, wisdom listens",
    "The unexamined life is not worth living",
    "Why social media is making you depressed",
    "The comparison trap that's ruining your life",
    "Why you feel empty even when you have everything",
    "The paradox of choice in the modern world",
    "Digital loneliness in a connected world",

    # ============================================================
    # 🆕 PERSPECTIVE-SHIFTING / DEEP PHILOSOPHICAL THEMES
    # ============================================================
    "Everything depends on perspective - the villain in one story is the hero in another",
    "If you ask the grass, the zebra is the monster and the lion is the protector",
    "Nothing in this world comes for free - even heaven demands death",
    "The knife thinks it's hurting the bread but it's actually helping someone eat",
    "The same rain that grows flowers also causes floods",
    "Fire destroys the forest but also clears the path for new life",
    "The same ocean that carries ships also swallows them",
    "A lock and a key are useless alone but together they protect everything",
    "Your ceiling is someone else's floor - perspective changes everything",
    "The wolf is evil in the story told by the sheep",
    "The same sun that melts ice also hardens clay - same situation different results",
    "A lion doesn't lose sleep over the opinion of sheep",
    "The tree that bends in the storm survives while the rigid one breaks",
    "Poison and medicine are sometimes the same thing - only the dose matters",
    "The darkness is not the opposite of light - it's the absence of it",
    "Every saint has a past and every sinner has a future",
    "The same wind blows on everyone but some build walls and some build windmills",
    "A bird sitting on a branch never worries about the branch breaking because it trusts its wings",
    "The river doesn't drink its own water - the tree doesn't eat its own fruit",
    "What feeds you today can starve you tomorrow if you depend on it forever",
    "The same society that tells you to be yourself will judge you for it",
    "They pray for you when you're sick but envy you when you're well",
    "The graveyard is the richest place - full of unwritten books and unfinished dreams",
    "A diamond is just a piece of coal that handled stress well",
    "The arrow can only be shot forward by pulling it backward first",
    "The tallest trees catch the most wind - success attracts storms",
    "Stars can't shine without darkness around them",
    "The most expensive thing in the world is trust - it takes years to build and seconds to destroy",
    "You can't read the label from inside the bottle - outsiders see what you can't",
    "The cage was open the whole time - you just never looked up",
    "Nobody notices your tears nobody notices your sadness but they all notice your mistakes",
    "The strongest soldiers are given the hardest battles",
    "A smooth sea never made a skilled sailor",
    "The candle that lights others burns itself - sacrifice is silent",
    "Sometimes the wrong train takes you to the right station",
    "People who live in glass houses judge others through the same walls",
    "The fisherman sees the ocean differently than the tourist",
    "If you chase two rabbits you catch none - focus is the real superpower",
    "The teacher appears when the student is ready not when the student asks",
    "Nothing worth having comes without a price - even breathing costs energy",
    "The world rewards you for results not for suffering",
    "Pain is the rent you pay for living in a strong body",
    "You can't heal in the same environment that made you sick",
    "The wolf you feed is the one that wins - choose your thoughts wisely",
    "A drowning man will grab even a sword - desperation blinds you",
    "The same door that closes behind you opens something ahead",
    "Broken crayons still color - your past doesn't define your output",
    "Sometimes the most productive thing you can do is rest",
    "Silence is the best answer to a fool and the best friend to the wise",
    "The things you own end up owning you - minimalism is freedom",
    "Nobody teaches you how to handle success and that's why it destroys so many",
    "The mountain you carry was only meant to be climbed",
    "An empty vessel makes the most noise - depth is always quiet",
]

CATEGORIES = [
    "GROWTH", "TRUTH", "MONEY", "MINDSET", "HABITS",
    "LONELY_GRIND", "DARK_MOTIVATION", "SELF_WORTH",
    "RELATIONSHIPS", "MENTAL_HEALTH", "HARD_TRUTH",
    "TIME_URGENCY", "PHILOSOPHY", "MODERN_STRUGGLE",
    "FAILURE_SUCCESS", "CONFIDENCE", "EMOTIONAL_DEPTH",
    "SILENT_POWER", "PAIN_TO_POWER", "REALITY_CHECK",

    # 🆕 NEW CATEGORIES
    "PERSPECTIVE_SHIFT", "DEEP_ANALOGY", "NATURE_WISDOM",
    "PARADOX", "DARK_PHILOSOPHY", "HIDDEN_TRUTH",
    "IRONY_OF_LIFE", "METAPHOR_BOMB", "SACRIFICE",
    "DUALITY", "TWISTED_REALITY", "RAW_OBSERVATION",
]

TONES = [
    "melancholic but empowering",
    "calm and wise, like a late night realization",
    "raw and brutally honest",
    "quiet confidence, like someone who already won",
    "slightly sad but deeply motivating",
    "spoken like a mentor who's been through hell",
    "cold truth delivered with warmth",
    "reflective, like writing in a journal at 3am",
    "powerful silence energy",
    "like advice from your future self",

    # 🆕 NEW TONES
    "perspective-flipping, like showing the other side of the coin",
    "dark and poetic, like a philosopher staring at the stars",
    "twisted irony, like life laughing at your plans",
    "nature-inspired wisdom, calm but devastating",
    "cold observation, like watching the world from a rooftop",
    "paradox energy, making you question everything",
    "ancient proverb rewritten for the modern soul",
    "quiet devastation, like a truth bomb wrapped in silk",
]

STRUCTURES = [
    "3 lines - setup, twist, punchline",
    "4 lines - slow build to a powerful ending",
    "3 lines - observation, realization, truth bomb",
    "4 lines - question format that makes you think",
    "3 lines - contrast between two ideas ending with wisdom",
    "3 lines - metaphor that hits different",
    "4 lines - storytelling micro-moment",

    # 🆕 NEW STRUCTURES
    "3 lines - perspective flip using two sides of the same thing",
    "2 lines - single devastating truth with no escape",
    "3 lines - analogy from nature applied to human life",
    "4 lines - if-you-ask format showing different perspectives",
    "3 lines - irony of life wrapped in simple words",
    "2 lines - paradox that makes you stop and think",
    "3 lines - something everyone sees differently depending on who they are",
]


def clean_line(line):
    cleaned = line.strip()
    cleaned = cleaned.replace("**", "")
    cleaned = cleaned.replace("##", "")
    cleaned = cleaned.replace("*", "")
    cleaned = cleaned.strip()
    return cleaned


def extract_value(line, key):
    cleaned = clean_line(line)
    pattern = re.compile(re.escape(key) + r'\s*:\s*', re.IGNORECASE)
    match = pattern.search(cleaned)
    if match:
        value = cleaned[match.end():].strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        return value
    return None


def detect_key(line):
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


# -------- STEP 1: Generate Content --------
def get_dynamic_content():
    print("🤖 AI Thinking... Generating Fresh Content...")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # 🔥 PURE RANDOM - no file tracking
    theme = random.choice(THEMES)
    category = random.choice(CATEGORIES)
    tone = random.choice(TONES)
    structure = random.choice(STRUCTURES)
    seed = random.randint(10000, 99999)
    timestamp = int(time.time())

    print(f"🎯 Theme: {theme}")
    print(f"🏷️  Category: {category}")
    print(f"🎭 Tone: {tone}")
    print(f"📐 Structure: {structure}")

    prompt = f"""
You are a quiet mentor who speaks from deep personal experience.
You challenge the viewer without hate, insults, or shaming.

Theme: {theme}
Category: {category}
Tone: {tone}
Structure: {structure}
Unique Seed: {seed}
Timestamp: {timestamp}

### CRITICAL RULES (LANGUAGE):
- NO big words or fancy vocabulary.
- NO hate, insults, or blaming language.
- Use simple, casual, everyday English.
- Sound like a REAL PERSON making a deep realization.
- DO NOT just rephrase the theme. Create an ORIGINAL thought INSPIRED by it.
- DO NOT use cliché phrases like "take the first step" or "start before you're ready."
- Surprise the reader. Say something they haven't heard 1000 times.

### PERSPECTIVE & DEEP PHILOSOPHY RULES (NEW - VERY IMPORTANT):
- Sometimes create quotes that FLIP perspective completely.
- Show the SAME situation from TWO different viewpoints.
- Use analogies from nature, animals, or everyday objects to reveal hidden truths.
- Think like: "If you ask the grass, the zebra is the **monster** and the lion is the **protector**."
- Think like: "Nothing in this world comes for **free**. Even heaven demands **death**."
- Think like: "The same **rain** that grows flowers also causes **floods**."
- The reader should STOP and RETHINK their entire understanding.
- Make the reader feel like they just saw the world from a completely new angle.
- Use irony, paradox, and duality whenever the theme allows it.

### QUOTE RULES (VERY STRICT):
- Generate a single continuous thought broken into {structure}.
- The tone should be: {tone}.
- Use ** around 1 or 2 high-impact words per line to make them bold.
- Each line should be SHORT (5-9 words max per line).
- The quote must feel FRESH and UNIQUE. Not generic motivation.
- Think of an angle nobody talks about.
- Example format (DO NOT copy this, create your own):
"Sometimes the **hardest** paths,
lead to the most **beautiful** destinations,
especially when you walk **alone**."

### WHAT TO AVOID (VERY IMPORTANT):
- Don't say "take the first step"
- Don't say "start before you're ready"
- Don't say "begin the journey"
- Don't say "just start"
- Don't give generic advice. Give a REALIZATION.
- Don't repeat themes from common motivational pages.
- Don't be preachy. Be observational. Be poetic. Be twisted.

### TITLE & METADATA RULES:
- Catchy, urgency-based, under 100 characters.
- 2-3 emojis, 1-2 hashtags.
- Title should make someone STOP scrolling.

### OUTPUT FORMAT (STRICT - 4 PARTS ONLY, NO extra formatting):
QUOTE: [Your 3-4 line quote with **bold** markers]
TITLE: [Catchy urgency title, emojis, hashtags]
DESCRIPTION: [2-4 short lines. Add 5-6 hashtags.]
TAGS: [25-30 keywords separated by comma]
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        print("=" * 50)
        print("📋 RAW AI RESPONSE:")
        print(text)
        print("=" * 50)

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
                clean = stripped.replace('"', '').strip()
                if clean:
                    temp_quote.append(clean)
            elif current_key == "DESCRIPTION":
                data["DESCRIPTION"] += "\n" + stripped
            elif current_key == "TAGS":
                data["TAGS"] += ", " + stripped

        if temp_quote:
            data["QUOTE"] = "\n".join(temp_quote)

        if len(data["TITLE"]) > 100:
            data["TITLE"] = data["TITLE"][:97] + "..."

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
            "DESCRIPTION": "Daily motivation for you. #discipline #growth #shorts",
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
            print("❌ Authentication fail!")
            return

        raw_tags = data.get("TAGS", "motivation, shorts")
        if isinstance(raw_tags, str):
            tag_list = [tag.strip() for tag in raw_tags.split(',') if tag.strip()]
        else:
            tag_list = raw_tags

        tag_lower = [t.lower() for t in tag_list]
        if "shorts" not in tag_lower:
            tag_list.append("shorts")

        title = data.get("TITLE", "Motivation 🔥 #shorts")
        if not title or title.strip() == "":
            title = "You Need To Hear This 🔥💯 #shorts"

        description = data.get("DESCRIPTION", "Daily motivation #shorts")
        if not description or description.strip() == "":
            description = "A reminder you needed today. #shorts #motivation"
        if "#Shorts" not in description:
            description += "\n\n#Shorts"

        print("\n📋 UPLOADING WITH:")
        print(f"   Title: {title}")
        print(f"   Tags: {tag_list[:10]}...")
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
