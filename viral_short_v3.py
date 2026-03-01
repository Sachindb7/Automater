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
    print("🤖 AI Thinking... Generating Fresh Content...")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # -------- MICRO NICHE THEME POOLS (100+) --------
    theme_pools = {
        "GROWTH": [
            "Starting Before You Feel Ready",
            "Consistency Beats Motivation",
            "Discipline Over Talent",
            "Long Term Thinking",
            "Work Ethic",
            "Focus and Execution",
            "Building Momentum",
            "Delayed Gratification",
            "Learning From Failure",
            "Power of Small Steps",
            "Compounding Effort Over Time",
            "Doing The Boring Work",
            "Showing Up On Bad Days",
            "Building Systems Not Goals",
            "Earning Respect Through Action",
            "Becoming Resourceful",
            "Investing In Yourself First",
            "Speed of Implementation",
            "Saying No To Distractions",
            "Choosing Hard Now For Easy Later",
        ],
        "TRUTH": [
            "Personal Responsibility",
            "Hard Truths About Progress",
            "Why Most People Quit",
            "Comfort vs Growth",
            "Self Control",
            "Facing Reality",
            "Nobody Owes You Anything",
            "Your Circle Reflects Your Future",
            "Average Is A Choice",
            "Time You Waste Never Returns",
            "Pain Of Regret vs Pain Of Discipline",
            "The Cost Of Staying The Same",
            "Opinions Dont Pay Your Bills",
            "Being Honest With Yourself",
            "Outgrowing People Is Normal",
        ],
        "MONEY": [
            "Money Is A Tool Not A Goal",
            "Value Creation Over Job Hunting",
            "Multiple Income Streams",
            "Spending Habits Define Your Future",
            "Selling Is A Life Skill",
            "Building Skills That Pay Forever",
            "The Real Cost Of Cheap Decisions",
            "Price Of Free Time",
            "Saving Alone Wont Make You Rich",
            "Your Network Is Your Net Worth",
            "Why Side Hustles Matter",
            "Learn To Sell Or Stay Broke",
            "Invest Time Before Money",
            "Money Follows Value Not Degrees",
            "Rich vs Wealthy Mindset",
        ],
        "MINDSET": [
            "Your Identity Shapes Your Actions",
            "Confidence Comes After Action",
            "Overthinking Kills Dreams",
            "Comparison Is Silent Poison",
            "Patience Is A Competitive Advantage",
            "Growth Happens In Silence",
            "What You Tolerate You Encourage",
            "Your Standards Define Your Life",
            "Mental Toughness Is A Muscle",
            "Detach From Outcomes Focus On Process",
            "Stop Asking Permission To Win",
            "Fear Is Not A Stop Sign",
            "Your Mind Quits Before Your Body",
            "Small Wins Build Big Confidence",
            "Prove It To Yourself Not Others",
        ],
        "HABITS": [
            "Morning Routine Shapes Your Day",
            "Sleep Is A Superpower",
            "Reading Changes Thinking",
            "Phone Addiction Kills Potential",
            "Environment Shapes Behavior",
            "Energy Management Over Time Management",
            "Eliminating Before Adding",
            "The Power Of Boredom",
            "Ritual vs Random Living",
            "Tracking Progress Creates Momentum",
            "Journaling Clears Mental Fog",
            "Walking Daily Changes Everything",
            "Cold Showers Build Willpower",
            "Eating Clean Fuels The Mind",
            "Digital Detox Weekly",
        ],
        "LONELY_GRIND": [
            "Why The Journey Feels Lonely",
            "Friends Disappear When You Level Up",
            "Nobody Claps Until You Win",
            "Silent Work Loud Results",
            "Building Alone Is A Superpower",
            "The Grind Nobody Sees",
            "Late Nights Early Mornings",
            "When Nobody Believes In You",
            "Success Is Lonely At First",
            "Your Comeback Is Being Built In Silence",
        ],
        "RELATIONSHIPS": [
            "Boundaries Are Self Respect",
            "Trust Actions Not Promises",
            "Not Everyone Deserves Your Energy",
            "Quality Over Quantity In Friendships",
            "You Teach People How To Treat You",
            "Stop Chasing People Who Ignore You",
            "Real Ones Stay Without Being Asked",
            "Loyalty Is Rare Protect It",
            "Some People Are Lessons Not Blessings",
            "Love Yourself Before Loving Others",
        ],
        "STUDENT_LIFE": [
            "Marks Dont Define Intelligence",
            "Learn Skills Not Just Syllabus",
            "College Is Not The Only Path",
            "Start Building While Studying",
            "Your 20s Are For Building Not Chilling",
            "Stop Waiting For The Right Time",
            "Use Your Free Time Wisely",
            "Every Expert Was Once A Beginner",
            "Fail Fast Learn Faster",
            "Your Degree Wont Save You Your Skills Will",
        ],
        "SOCIAL_MEDIA_AGE": [
            "Followers Dont Equal Success",
            "Stop Watching Others Win And Start",
            "Online Flex vs Real Life",
            "Scrolling Is Stealing Your Future",
            "You Consume More Than You Create",
            "Likes Dont Pay Bills",
            "Build In Private Win In Public",
            "Your Feed Is Programming Your Mind",
            "Attention Is The New Currency",
            "Create Dont Just Consume",
        ],
        "FEAR_AND_DOUBT": [
            "Doubt Kills More Dreams Than Failure",
            "You Are Closer Than You Think",
            "Fear Means You Care Enough",
            "Done Is Better Than Perfect",
            "Stop Waiting For Permission",
            "What If It Works Out",
            "The First Step Is Always Ugly",
            "Nobody Figured It Out Before Starting",
            "Scared Is Normal Stuck Is A Choice",
            "Your Only Competition Is Yesterday You",
        ],
    }

    # -------- PICK CATEGORY + THEME --------
    categories = list(theme_pools.keys())
    weights = [0.15, 0.12, 0.12, 0.13, 0.10, 0.10, 0.08, 0.08, 0.06, 0.06]
    category = random.choices(categories, weights=weights, k=1)[0]
    theme = random.choice(theme_pools[category])

    # -------- RANDOM TONE --------
    tones = [
        "calm older brother giving life advice",
        "quiet mentor who speaks from experience",
        "brutally honest friend at 2am",
        "someone who already made the mistakes",
        "wise person who says less but means more",
        "stoic thinker who cuts through noise",
        "street smart advisor with no filter",
        "coach who believes in you but won't sugarcoat",
    ]
    tone = random.choice(tones)

    # -------- RANDOM BODY STYLE --------
    body_styles = [
        "A short realization that hits deep",
        "A one-line truth bomb",
        "A comparison that makes the viewer think",
        "A question disguised as a statement",
        "An action step disguised as wisdom",
        "A metaphor about life or growth",
        "A painful contrast between two paths",
        "A calm but firm redirect of mindset",
    ]
    body_style = random.choice(body_styles)

    # -------- HUMAN SOUNDING HOOKS (40+) --------
    all_hooks = [
        "This hit me hard…",
        "Nobody tells you this…",
        "Bro just think about it…",
        "This changed my life…",
        "Read this twice…",
        "Not gonna sugarcoat it…",
        "Hear me out on this…",
        "This one hurt ngl…",
        "Real talk for a sec…",
        "You need to hear this…",
        "Let me be honest…",
        "This keeps me up at night…",
        "Wish I knew this sooner…",
        "Stop and think about this…",
        "Nobody warns you about this…",
        "This is gonna sting…",
        "Wait for it…",
        "One thing I learned late…",
        "The part nobody says…",
        "Took me years to get this…",
        "You already feel this…",
        "Just sit with this one…",
        "Quick reality check…",
        "Be honest with yourself…",
        "This sounds harsh but…",
        "The ugly truth is…",
        "No one prepared me for…",
        "Saving this for later…",
        "Think about this tonight…",
        "You're not gonna like this…",
        "Can we talk about this…",
        "Facts nobody accepts…",
        "This might wake you up…",
        "Pause and read this…",
        "Lemme tell you something…",
        "It clicked when I saw…",
        "Most people miss this…",
        "Dont skip this one…",
        "Felt this in my chest…",
        "One line that broke me…",
    ]
    selected_hooks = random.sample(all_hooks, 5)

    # -------- UNIQUE SEED --------
    seed = random.randint(10000, 99999)

    prompt = f"""
You are a {tone}.
You challenge the viewer without hate, insults, or shaming.
Your goal is to push action, not guilt.

Theme: {theme}
Category: {category}
Unique Seed: {seed}

### CRITICAL RULES (LANGUAGE):
❌ NO big words or fancy vocabulary.
❌ NO hate, insults, or blaming language.
❌ Do NOT use words like trap, scam, lie, bribe.
❌ Do NOT sound like AI or a robot.
✅ Use simple, casual, everyday English.
✅ Sound like a REAL PERSON texting a friend.
✅ Each output MUST feel fresh and never-seen-before.

### HOOK RULES (VERY STRICT):
- MUST be 4 to 6 words ONLY.
- End with "..."
- Sound like a real person talking, NOT a motivational poster.
- NO fancy words like "embrace", "unleash", "ignite", "forge", "transcend".
- Think of it like a text message from a friend.

### BODY RULES:
- Max 10 words.
- Actionable or reflective.
- Body Style: {body_style}
- Sound human and conversational.

### ANTI-REPETITION (BANNED PHRASES):
❌ NEVER use these overused lines in HOOK or BODY:
- "Growth starts when comfort ends"
- "Discipline beats motivation every time"
- "Your comfort zone is killing you"
- "Nobody is coming to save you"
- "Actions speak louder than words"
- "Consistency is key"
- "Hard work pays off"
- "Start before you're ready"
- "Your excuses are holding you back"
- "Success is not overnight"
- "Keep grinding" / "Stay focused" / "Trust the process"
- "Embrace the journey" / "Unleash your potential"

### HOOK STYLE (Pick ONE and twist it creatively):
{chr(10).join(f"- {h}" for h in selected_hooks)}

### TITLE RULES (VERY STRICT):
- Catchy, urgency-based, scroll-stopping.
- 2-3 emojis mixed naturally.
- 1-2 hashtags at the end.
- EVERYTHING under 100 characters total (including emojis + hashtags).
- Examples of GOOD titles:
  "You Need To Hear This Right Now 🔥💯 #shorts"
  "Stop Ignoring This 😤🚨 #mindset #shorts"
  "This One Hurts But Its True 💔🔥 #realtalk"
  "Bro This Changed Everything 🧠💡 #growth"

### BODY SAFETY RULE:
If the body only makes the viewer feel bad, rewrite it.
It must push action, not guilt.

### OUTPUT FORMAT (STRICT – 5 PARTS ONLY):
HOOK: [4-6 words only. End with "...". Sound human.]
BODY: [Max 10 words. Unique. Sound human.]
TITLE: [Catchy urgency title, 2-3 emojis, 1-2 hashtags, ALL under 100 chars]
DESCRIPTION: [2-4 short lines (seo worthy). Add 5-6 hashtags.]
TAGS: [25-30 high-traffic keywords/search intended tags all under 500 char]
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        data = {
            "HOOK": "This hit me hard...",
            "BODY": "You only grow when it gets uncomfortable.",
            "TITLE": "You Need To Hear This 🔥💯 #shorts",
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

        # -------- TITLE LENGTH SAFETY CHECK --------
        if len(data["TITLE"]) > 100:
            data["TITLE"] = data["TITLE"][:97] + "..."

        print(f"🔹 Category: {category}")
        print(f"🔹 Theme: {theme}")
        print(f"🔹 Tone: {tone}")
        print(f"🔹 Body Style: {body_style}")
        print(f"🔹 Hook: {data['HOOK']}")
        print(f"🔹 Body: {data['BODY']}")
        print(f"🔹 Title ({len(data['TITLE'])} chars): {data['TITLE']}")

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
    draw.rectangle([(0, TOP_MARGIN), (VIDEO_SIZE[0], TOP_MARGIN + LABEL_HEIGHT)], fill="white"
)

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

def get_random_music(duration):
    music_dir = "music"

    if not os.path.exists(music_dir):
        print("📢 No music folder found. Running without sound.")
        return None

    tracks = [
        os.path.join(music_dir, f)
        for f in os.listdir(music_dir)
        if f.lower().endswith((".mp3", ".wav"))
    ]

    if not tracks:
        print("📢 Music folder empty. Running without sound.")
        return None

    track_path = random.choice(tracks)
    audio = AudioFileClip(track_path)

    # If music shorter than video → loop
    if audio.duration < duration:
        audio = afx.audio_loop(audio, duration=duration)

    # Trim to exact video length + safe volume
    audio = audio.subclip(0, duration).volumex(0.25)

    print(f"🎵 Using music: {os.path.basename(track_path)}")
    return audio


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
    except Exception as e:
        print(f"❌ Upload Failed: {e}")


# -------- MAIN --------
if __name__ == "__main__":
    video_data = create_video()
    try:
        upload_short(OUTPUT_FILE, video_data)
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
