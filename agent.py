import os
import io
import urllib.parse
import streamlit as st
import feedparser
from gtts import gTTS
from google import genai

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================

API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)

if not API_KEY:
    st.error(
        "No API key found. Set the GEMINI_API_KEY environment variable, "
        "or add it to .streamlit/secrets.toml as GEMINI_API_KEY = \"your-key\"."
    )
    st.stop()

client = genai.Client(api_key=API_KEY)
# Map UI language labels -> gTTS language codes
LANG_CODES = {
    "English": "en",
    "Urdu (اردو)": "ur",
    "Spanish (Español)": "es",
    "French (Français)": "fr",
    "Arabic (العربية)": "ar",
    "Mandarin (中文)": "zh-CN",
    "Hindi (हिन्दी)": "hi",
    "German (Deutsch)": "de",
    "Portuguese (Português)": "pt",
    "Russian (Русский)": "ru",
}

def generate_audio(text: str, language_label: str) -> bytes:
    """Generate speech audio (mp3 bytes) for the given text using gTTS,
    in the language matching the briefing's language."""
    lang_code = LANG_CODES.get(language_label, "en")
    clean_text = text.replace("**", "").replace("#", "")
    tts = gTTS(text=clean_text, lang=lang_code)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()

# ==========================================
# 2. STREAMLIT USER INTERFACE UI & SETTINGS
# ==========================================

st.set_page_config(page_title="AI News Curation Agent", layout="wide")

# --- Background theme selector + apply function (place this right after st.set_page_config(...)) ---
def apply_background_theme(theme: str) -> None:
    """
    Apply a background theme by injecting CSS into Streamlit page.
    theme: one of "Light", "Dark", "Ocean", "Forest", "Paper"
    """
    themes_css = {
        "Light": """
            <style>
            html, body, .stApp {
                background: #ffffff !important;
                color: #111827 !important;
            }
            .stApp .block-container {
                background: rgba(255,255,255,0.85) !important;
                border-radius: 10px;
                padding: 1rem;
            }
            </style>
        """,
        "Dark": """
            <style>
            html, body, .stApp {
                background: linear-gradient(180deg,#0b1220,#061021) fixed !important;
                color: #e6eef8 !important;
            }
            .stApp .block-container {
                background: rgba(0,0,0,0.45) !important;
                border-radius: 10px;
                padding: 1rem;
            }
            </style>
        """,
        "Ocean": """
            <style>
            html, body, .stApp {
                background-image: url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1400&auto=format&fit=crop') !important;
                background-size: cover !important;
                background-attachment: fixed !important;
                color: #f0f9ff !important;
            }
            .stApp .block-container {
                background: rgba(2,6,23,0.55) !important;
                border-radius: 10px;
                padding: 1rem;
            }
            </style>
        """,
        "Forest": """
            <style>
            html, body, .stApp {
                background-image: url('https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=1400&auto=format&fit=crop') !important;
                background-size: cover !important;
                background-attachment: fixed !important;
                color: #f7fff7 !important;
            }
            .stApp .block-container {
                background: rgba(2,25,8,0.55) !important;
                border-radius: 10px;
                padding: 1rem;
            }
            </style>
        """,
        "Paper": """
            <style>
            html, body, .stApp {
                background: linear-gradient(180deg,#f8f4ea,#efe6d6) !important;
                color: #2b2b2b !important;
            }
            .stApp .block-container {
                background: rgba(255,255,250,0.9) !important;
                border-radius: 10px;
                padding: 1rem;
                box-shadow: 0 6px 18px rgba(60,60,60,0.06);
            }
            </style>
        """,
    }

    css = themes_css.get(theme, themes_css["Light"])
    st.markdown(css, unsafe_allow_html=True)


# Sidebar selector + persistence
_theme_options = ["Light", "Dark", "Ocean", "Forest", "Paper"]
_default_theme = st.session_state.get("background_theme", "Light")
background_theme = st.sidebar.selectbox(
    "Background theme",
    _theme_options,
    index=_theme_options.index(_default_theme)
)
# persist choice so it survives reruns
st.session_state["background_theme"] = background_theme
# apply it
apply_background_theme(background_theme)
# -------------------------------------------------------------------------------

st.title("🤖 AI-Curated Audio News Agent")
st.write("An autonomous multi-lingual agent that processes raw live news streams and speaks briefings aloud.")

st.sidebar.header("⚙️ Configuration Settings")

target_language = st.sidebar.selectbox(
    "Set App Language / زبان منتخب کریں:",
    list(LANG_CODES.keys())
)

category = st.sidebar.selectbox(
    "Select News Domain:",
    ["Science", "Geopolitics", "Technology", "Computer Science",
     "Healthcare", "Fitness", "Space Exploration"]
)

# --- Science sub-discipline picker ---
science_niche = None
if category == "Science":
    science_niche = st.sidebar.selectbox(
        "Which field of science?",
        ["Biology", "Zoology", "Botany", "Genetics", "Marine Biology",
         "Physics", "Astrophysics", "Nuclear Physics", "Quantum Physics",
         "Chemistry", "Environmental Science", "Neuroscience", "Geology"]
    )

# --- Computer Science free-text topic picker ---
cs_topic = None
if category == "Computer Science":
    cs_topic = st.sidebar.text_input(
        "What computer science topic? (e.g. AI, Cybersecurity, Quantum Computing, Robotics)",
        value="Artificial Intelligence"
    )

def build_search_query() -> str:
    """Build the news search query string based on category + sub-selection."""
    if category == "Science" and science_niche:
        return science_niche
    if category == "Computer Science" and cs_topic and cs_topic.strip():
        return cs_topic.strip()
    return category

def build_rss_url(query: str) -> str:
    encoded = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"

# ==========================================
# 3. AGENT PROCESSING & TRANSLATION CORE
# ==========================================

st.sidebar.markdown("---")
col_fetch, col_stop = st.sidebar.columns(2)
fetch_clicked = col_fetch.button("🚀 Fetch Briefing")
stop_clicked = col_stop.button("🛑 Stop / Reset")

# "Stop / Reset" clears everything and brings the user back to a fresh
# selection state. Note: this resets state between actions — Streamlit's
# execution model does not allow literally interrupting a network call
# that is already in progress mid-flight.
if stop_clicked:
    for key in ['briefing_result', 'current_category', 'current_language',
                'current_query', 'audio_bytes']:
        st.session_state.pop(key, None)
    st.rerun()

if fetch_clicked:
    query = build_search_query()
    with st.spinner(f"Agent fetching live streams on '{query}' and structuring content via Gemini..."):
        try:
            feed = feedparser.parse(build_rss_url(query))
            raw_titles = [entry.title for entry in feed.entries[:12]]

            if not raw_titles:
                st.error("Could not fetch news streams. Check internet connection or try a different topic.")
            else:
                prompt = f"""
                You are an advanced news curation and professional translation agent.
                Analyze these raw headlines related to the topic: '{query}' (category: '{category}').
                Filter out duplicate stories, noise, or clickbait. Choose the top 3 most critical news stories.

                CRITICAL INSTRUCTION: You must translate and write your entire final output response in the following language: '{target_language}'.
                If the language is Urdu or Arabic, make sure it writes fluidly in its proper script.

                For each of the 3 chosen stories, provide a summary consisting of exactly two clear, engaging sentences.

                Format your final output precisely like this structure:

                Story 1: [Insert Headline/Title Here]
                Summary: [Insert your two-sentence briefing summary here]

                Story 2: [Insert Headline/Title Here]
                Summary: [Insert your two-sentence briefing summary here]

                Story 3: [Insert Headline/Title Here]
                Summary: [Insert your two-sentence briefing summary here]
                """

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[prompt, "\n".join(raw_titles)]
                )

                if response and response.text:
                    st.session_state['briefing_result'] = response.text
                    st.session_state['current_category'] = query
                    st.session_state['current_language'] = target_language
                    st.session_state.pop('audio_bytes', None)  # clear old audio
                else:
                    st.error("Received an empty response from the AI model. Try running it again.")

        except Exception as e:
            st.error(f"Error during agent runtime processing: {e}")

# ==========================================
# 4. SPLIT DISPLAY & VISUAL ROBOT AVATAR
# ==========================================

if 'briefing_result' in st.session_state:
    st.markdown("---")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 🤖 News Anchor")
        st.image(
            "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=400&auto=format&fit=crop",
            caption="AI Agent Broadcasting Active",
            use_container_width=True
        )

        speak_col, stop_col = st.columns(2)

        if speak_col.button("🔊 Read Aloud"):
            with st.spinner("Generating speech audio..."):
                try:
                    audio_bytes = generate_audio(
                        st.session_state['briefing_result'],
                        st.session_state['current_language']
                    )
                    st.session_state['audio_bytes'] = audio_bytes
                except Exception as e:
                    st.error(f"Could not generate audio: {e}")

        if stop_col.button("⏹ Stop Audio"):
            st.session_state.pop('audio_bytes', None)
            st.rerun()

        if 'audio_bytes' in st.session_state:
            st.audio(st.session_state['audio_bytes'], format="audio/mp3", autoplay=True)

    with col2:
        st.markdown(
            f"### ✨ Verified {st.session_state['current_category']} Briefing "
            f"({st.session_state['current_language']})"
        )
        st.info(st.session_state['briefing_result'])
