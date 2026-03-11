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
# 🔥 BILLIONAIRE MINDSET - FOCUSED VARIETY SYSTEM
# ============================================================

THEMES = [
    # ---------- 💰 MONEY MINDSET ----------
    "Why broke people stay broke - it's a mindset not a bank balance",
    "The ugly truth about trading your time for money",
    "What rich people understand about money that you don't",
    "Why saving money alone will never make you rich",
    "The one money skill school never taught you",
    "Your salary is someone else's daily spending - let that sink in",
    "Rich people buy time while broke people sell time",
    "Money follows value - become more valuable",
    "Stop working for money and make money work for you",
    "The difference between looking rich and being rich",

    # ---------- 🔥 DISCIPLINE & HABITS ----------
    "The pain of discipline vs the pain of regret - pick one",
    "Your morning routine is secretly deciding your future",
    "Small daily habits that are quietly destroying your life",
    "The real difference between being busy and being productive",
    "The biggest lie you tell yourself is I'll start tomorrow",
    "Stop waiting for motivation and just build momentum",
    "Discipline is doing it even when you don't feel like it",
    "Your daily routine is either building your dream or someone else's",
    "One hour a day on your skill changes everything in one year",
    "The things you do when nobody is watching decide your future",

    # ---------- 📈 GROWTH & LEVELING UP ----------
    "Why most people quit right before the breakthrough happens",
    "The friends you lose when you start leveling up",
    "Why nobody claps for you until you've already made it",
    "The old you has to go so the new you can show up",
    "Growth is uncomfortable and that's exactly the point",
    "You weren't built to stay the same person forever",
    "Stop saying sorry for becoming a better version of yourself",
    "The glow up happens in private the results show up in public",
    "You are one decision away from a completely different life",
    "Level up so hard that people who knew the old you can't keep up",

    # ---------- 💎 SELF WORTH & CONFIDENCE ----------
    "Your value doesn't drop just because someone can't see it",
    "Confidence is quiet and insecurity is always loud",
    "Stop making yourself smaller so others feel comfortable",
    "You teach people how to treat you by what you accept",
    "Your biggest flex should be your peace of mind",
    "Not everyone deserves a front row seat in your life",
    "Know your worth then add tax to it",
    "The way you treat yourself sets the standard for everyone else",
    "Stop looking for approval from people who don't even approve of themselves",
    "You are the prize - start acting like it",

    # ---------- 🐺 LONE WOLF / GRINDING ALONE ----------
    "Your lonely phase is actually your most powerful phase",
    "Eating alone walking alone winning alone - it's a phase not a life",
    "The silence nobody sees is building the success everyone will hear",
    "Build in silence and let your results do all the talking",
    "The strongest people often have the smallest circles",
    "Sometimes you gotta distance yourself to see things clearly",
    "Alone time is when you find out who you really are",
    "The table you sit at alone today will be full tomorrow",
    "Working alone means nobody can slow you down",
    "Your circle got smaller because your vision got bigger",

    # ---------- 💪 COMEBACK & RISING UP ----------
    "The comeback is always stronger than the setback",
    "They laughed at you then - remember that when you win",
    "Use your pain as fuel not as an excuse to stop",
    "Your worst days are secretly building your best chapters",
    "Every setback is just a setup for something bigger",
    "You've survived 100% of your worst days so far",
    "The ones who doubted you will be the first to congratulate you",
    "Rock bottom taught me things mountain tops never could",
    "Tough times don't last but tough people definitely do",
    "Your biggest scars will become your greatest story",

    # ---------- ⏰ TIME & URGENCY ----------
    "One day or day one - you decide right now",
    "The clock is ticking whether you make a move or not",
    "You don't have unlimited tomorrows - act like it",
    "The best time was yesterday the next best time is right now",
    "Time is the only thing you can't buy back no matter how rich you get",
    "A year from now you'll wish you started today",
    "Everyone has 24 hours - how you use yours is the difference",
    "You're not running out of time you're running out of excuses",

    # ---------- 🗣️ REAL TALK / RELATABLE ----------
    "You're not lazy you're just scared to fail",
    "Nobody is coming to save you - that's your job now",
    "Your phone is stealing your future one scroll at a time",
    "You're addicted to distraction and you're calling it relaxation",
    "The people you admire are regular people who just didn't quit",
    "Feeling lost in your 20s is normal - just don't stay lost",
    "Stop comparing your chapter 1 to someone else's chapter 20",
    "The only person you should try to be better than is who you were yesterday",
    "Everybody wants the results but nobody wants the boring work",
    "You don't need more time you need more focus",
    "Hard work beats talent when talent doesn't work hard",
    "Most people don't want to see you win because it reminds them they're losing",
    "Your comfort zone is a beautiful place but nothing grows there",

    # ---------- 🌊 RARE DEEP ONES (1 in 20-30 ratio) ----------
    "Nothing in this world comes for free - even heaven demands death",
    "A diamond is just a piece of coal that handled pressure well",
    "Broken crayons still color - your past doesn't define your future",
    "A smooth sea never made a skilled sailor",
    "Stars only shine when it's dark enough around them",
]


CATEGORIES = [
    "MONEY_MINDSET", "GROWTH", "DISCIPLINE", "SELF_WORTH",
    "CONFIDENCE", "LONE_WOLF", "COMEBACK", "HARD_TRUTH",
    "TIME_URGENCY", "HABITS", "REAL_TALK", "RARE_DEEP",
]


TONES = [
    "like your best friend giving you a reality check at 2am",
    "calm and confident, like someone who already made it",
    "raw and honest, no sugarcoating but no hate either",
    "like a big brother who genuinely wants you to win",
    "warm but firm, like a mentor who believes in you",
    "quiet winner energy, someone who moves in silence",
    "late night honest conversation between two real ones",
    "slightly emotional but deeply empowering",
]


STRUCTURES = [
    "3 lines - setup, twist, punchline",
    "4 lines - slow build to a powerful ending",
    "3 lines - observation, realization, truth bomb",
    "3 lines - contrast between two ideas ending with wisdom",
    "3 lines - simple metaphor that hits different",
    "4 lines - relatable moment leading to a powerful realization",
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
You are writing for a YouTube Shorts channel called "BILLIONAIRE MINDSET".
The channel posts positive motivation, money mindset, growth, and real bro-to-bro talk.
The vibe is like a friend who genuinely wants you to win in life.

Theme: {theme}
Category: {category}
Tone: {tone}
Structure: {structure}
Unique Seed: {seed}
Timestamp: {timestamp}

### WHO YOU ARE:
- You are NOT a preacher, philosopher, or professor.
- You are a real person who has been through real struggles and came out stronger.
- You talk like a FRIEND, not a teacher. Like a big brother, not a guru.
- Your words should feel like HOME - warm, real, and deeply honest.
- The reader should feel "damn, this hit different" and genuinely SMILE.
- Your content should make people SAVE it, SCREENSHOT it, and set it as wallpaper.

### LANGUAGE RULES (MOST IMPORTANT - READ CAREFULLY):
- Use ONLY simple, everyday English words that a normal person uses.
- Write like a 10th grader would talk to his best friend.
- If a 15-year-old wouldn't say that word in casual conversation, DON'T use it.
- The MEANING should be deep, NOT the vocabulary.
- Short words. Real feelings. Simple sentences. That's it.
- Every single word should feel NATURAL, like someone actually said it out loud.

### BANNED WORDS (ABSOLUTELY NEVER USE ANY OF THESE):
ephemeral, transcend, paradox, dichotomy, juxtaposition, existential,
ethereal, quintessential, metamorphosis, profound, inevitably, merely,
whilst, henceforth, illuminate, encompass, paradigm, manifestation,
resonate, trajectory, culmination, intrinsic, perpetual, abyss,
clandestine, enigma, facade, harbinger, labyrinth, ominous,
precipice, remnant, sovereign, ubiquitous, venerate, wield,
unbeknownst, forsake, azure, luminous, celestial, edifice,
oblivion, serenity, tempest, zenith, nadir, crucible, 
orchestrate, juxtapose, articulate, unravel, mundane,
mosaic, dissonance, convergence, visceral, poignant,
embark, forge, ignite, propel, catalyst, beacon, vessel,
tapestry, compass, anchor, realm, thrive, alchemize,
amidst, midst, therein, wherein, bestow, behold

### VIBE & FEELING RULES:
- The quote should hit a NERVE - something deeply relatable to everyday life.
- It should make someone stop scrolling and think "this is about ME".
- The overall feeling should be POSITIVE and EMPOWERING, never depressing.
- Think: wallpaper-worthy. Screenshot-worthy. Save-worthy.
- The reader should want to come back every day for more.
- Make them SMILE with how real and relatable it feels.
- NOT negative, NOT hateful, NOT shaming anyone.
- It should feel like that one line your best friend said that stuck with you forever.

### QUOTE RULES (VERY STRICT):
- Generate a single continuous thought broken into {structure}.
- The tone should be: {tone}.
- Use ** around ONLY 1 or 2 high-impact words per line to make them bold.
- Each line should be SHORT (5-9 words max per line).
- The quote must feel FRESH and UNIQUE - not something you see on every page.
- DO NOT just rephrase the theme. Create an ORIGINAL thought INSPIRED by it.
- Think of an angle nobody else talks about.
- Example quality level (DO NOT copy these, create something completely new):
  "Everyone wants the **lifestyle**,
  nobody wants the **late nights**,
  that's why most people stay **average**."

### WHAT TO AVOID (VERY IMPORTANT):
- Don't say "take the first step"
- Don't say "start before you're ready"
- Don't say "begin the journey"
- Don't say "just start"
- Don't say "embrace the struggle"
- Don't say "unlock your potential"
- Don't say "ignite your passion"
- Don't say "forge your path"
- Don't use ANY motivational clichés that you see on every Instagram page
- Don't be preachy or lecture-like
- Don't be negative, dark, or morbid
- Don't use complex metaphors that confuse people
- Don't sound like a robot or AI - sound like a REAL HUMAN
- Give a REALIZATION or OBSERVATION, not advice or instructions

### TITLE & METADATA RULES:
- Catchy, makes someone STOP scrolling, under 100 characters.
- 2-3 emojis, include #shorts hashtag.
- Title should feel urgent and personal like it's speaking directly to the viewer.

### OUTPUT FORMAT (STRICT - 4 PARTS ONLY, NO extra formatting):
QUOTE: [Your 3-4 line quote with **bold** markers]
TITLE: [Catchy urgency title with emojis and #shorts]
DESCRIPTION: [2-4 short lines. Add 5-6 hashtags including #shorts]
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
