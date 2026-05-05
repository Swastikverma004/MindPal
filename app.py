import streamlit as st
import json
import os
import requests
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MindPal – Your Companion",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --sage:    #7D9B76;
    --cream:   #F5F0E8;
    --blush:   #E8D5C4;
    --clay:    #C4956A;
    --forest:  #2D4A3E;
    --ink:     #1C2B26;
    --mist:    #B8CCBA;
    --paper:   #FAF7F2;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--paper);
    color: var(--ink);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, var(--forest) 0%, #1a3329 100%) !important;
    border-right: none;
}
[data-testid="stSidebar"] * { color: var(--cream) !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: var(--cream) !important;
    border-radius: 10px !important;
    width: 100%;
    text-align: left !important;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.15) !important;
    border-color: var(--mist) !important;
}

/* Main area */
.stApp { background-color: var(--paper); }

/* Chat messages */
.user-bubble {
    background: var(--sage);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin: 6px 0 6px 20%;
    max-width: 75%;
    float: right;
    clear: both;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 2px 8px rgba(125,155,118,0.3);
}
.bot-bubble {
    background: white;
    border: 1px solid var(--blush);
    border-radius: 18px 18px 18px 4px;
    padding: 12px 18px;
    margin: 6px 20% 6px 0;
    max-width: 75%;
    float: left;
    clear: both;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.chat-container { overflow: hidden; padding: 10px 0; }
.chat-scroll { max-height: 62vh; overflow-y: auto; padding: 10px 20px; }

/* Headings */
h1, h2, h3 { font-family: 'DM Serif Display', serif !important; }

/* Input area */
.stTextInput > div > div > input {
    border-radius: 12px !important;
    border: 1.5px solid var(--blush) !important;
    background: white !important;
    padding: 10px 16px !important;
}
.stTextInput > div > div > input:focus { border-color: var(--sage) !important; }

/* Buttons */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"] {
    background: var(--sage) !important;
    border: none !important;
    color: white !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--forest) !important;
    transform: translateY(-1px);
}

.header-area {
    background: linear-gradient(135deg, var(--forest), #3a5f52);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    color: white;
}
.header-area h1 { color: white !important; margin: 0 0 6px 0; font-size: 2rem; }
.header-area p { color: var(--mist); margin: 0; font-size: 0.95rem; }

.persona-badge {
    background: linear-gradient(135deg, var(--clay), #d4a77a);
    color: white;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 0.8rem;
    font-weight: 500;
    display: inline-block;
    margin-bottom: 16px;
}

.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #999;
}
.empty-state .icon { font-size: 3rem; margin-bottom: 16px; }

.search-info {
    background: rgba(125,155,118,0.1);
    border: 1px solid var(--mist);
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 0.8rem;
    color: var(--forest);
    margin-bottom: 12px;
}
</style>

<!-- ✅ FIX: Enter key submits the form -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    function attachEnterListener() {
        const inputs = document.querySelectorAll('input[type="text"]');
        inputs.forEach(function(input) {
            if (!input.dataset.enterBound) {
                input.dataset.enterBound = "true";
                input.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        // Find the primary Send button and click it
                        const buttons = document.querySelectorAll('button[kind="primary"]');
                        buttons.forEach(function(btn) {
                            if (btn.innerText.includes('Send')) {
                                btn.click();
                            }
                        });
                    }
                });
            }
        });
    }
    // Run on load and re-attach after Streamlit rerenders
    attachEnterListener();
    const observer = new MutationObserver(attachEnterListener);
    observer.observe(document.body, { childList: true, subtree: true });
});
</script>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────────────────────────
CHAT_DIR = "chat_history"
os.makedirs(CHAT_DIR, exist_ok=True)

PRESET_CHARACTERS = [
    {"name": "Therapist",        "emoji": "🧠", "desc": "Professional, empathetic listener"},
    {"name": "Best Friend",      "emoji": "🤝", "desc": "Casual, supportive, real talk"},
    {"name": "Wife",             "emoji": "💑", "desc": "Loving, caring, warm partner"},
    {"name": "Life Coach",       "emoji": "🎯", "desc": "Motivating & goal-oriented"},
    {"name": "Shah Rukh Khan",   "emoji": "🌟", "desc": "Bollywood king, romantic & wise"},
    {"name": "Ranveer Singh",    "emoji": "🔥", "desc": "Energetic, wild, hype machine"},
    {"name": "Deepika Padukone", "emoji": "🌸", "desc": "Composed, elegant, emotionally aware"},
    {"name": "Kabir Singh",      "emoji": "🥃", "desc": "Intense, passionate, brutally honest"},
]

# ─── Session State ───────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "messages":          [],
        "character":         None,
        "system_prompt":     None,
        "chat_id":           None,
        "groq_key":          os.environ.get("GROQ_API_KEY", ""),
        "search_info":       "",   # stores what was found about the character
        "pending_input":     "",   # holds Enter-key submitted text
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── Groq Client ─────────────────────────────────────────────────────────────
def get_client():
    key = st.session_state.groq_key.strip()
    if not key:
        return None
    return Groq(api_key=key)

# ─── WEB SEARCH: Fetch character info from Wikipedia / DuckDuckGo ─────────────
def search_character_info(character: str) -> str:
    """
    Step 1: Search Wikipedia for the character.
    Step 2: Fall back to DuckDuckGo instant-answer API if Wikipedia misses.
    Returns a plain-text summary of who the character is.
    """
    info_parts = []

    # ── Wikipedia ──────────────────────────────────────────────────────────
    try:
        wiki_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + \
                   requests.utils.quote(character.replace(" ", "_"))
        r = requests.get(wiki_url, timeout=6,
                         headers={"User-Agent": "MindPal/1.0"})
        if r.status_code == 200:
            data = r.json()
            extract = data.get("extract", "")
            if extract and len(extract) > 80:
                info_parts.append(f"[Wikipedia] {extract[:1200]}")
    except Exception:
        pass

    # ── DuckDuckGo Instant Answer ──────────────────────────────────────────
    if not info_parts:
        try:
            ddg_url = "https://api.duckduckgo.com/"
            params  = {"q": character, "format": "json", "no_redirect": 1,
                       "no_html": 1, "skip_disambig": 1}
            r = requests.get(ddg_url, params=params, timeout=6,
                             headers={"User-Agent": "MindPal/1.0"})
            if r.status_code == 200:
                data = r.json()
                abstract = data.get("AbstractText", "")
                if abstract:
                    info_parts.append(f"[DuckDuckGo] {abstract[:1200]}")
                # Also grab related topics for richer context
                topics = data.get("RelatedTopics", [])[:3]
                for t in topics:
                    text = t.get("Text", "")
                    if text:
                        info_parts.append(text[:300])
        except Exception:
            pass

    return "\n\n".join(info_parts) if info_parts else ""


# ─── MIMICRY SYSTEM PROMPT GENERATOR ─────────────────────────────────────────
def generate_system_prompt(character: str) -> tuple[str, str]:
    """
    Returns (system_prompt, search_summary_for_display)
    Pipeline:
      1. Web search → gather real facts about the character
      2. Feed facts into a master mimicry prompt
      3. LLM generates a hyper-accurate persona system prompt
    """
    client = get_client()
    if not client:
        return "", ""

    # ── Step 1: Web Research ───────────────────────────────────────────────
    search_summary = search_character_info(character)
    research_block = (
        f"=== RESEARCH FOUND ABOUT '{character}' ===\n{search_summary}\n=== END RESEARCH ==="
        if search_summary
        else f"(No web data found for '{character}' — rely on your training knowledge)"
    )

    # ── Step 2: Mimicry Prompt Construction ───────────────────────────────
    meta_prompt = f"""You are the world's greatest AI mimicry artist and persona designer.

Your task: Create a system prompt that turns an AI into a PERFECT mimic of "{character}".

{research_block}

MIMICRY RULES — the system prompt you write MUST cover ALL of these:

1. IDENTITY LOCK
   - The AI IS {character}. Not similar to them. Not inspired by them. IS them.
   - It must never say "I am an AI", never break character, never refuse in-character questions.

2. LANGUAGE & SPEECH PATTERN (most important)
   - Identify the EXACT language(s) this character speaks. If they speak Hindi, write in Hindi. If Hinglish, use Hinglish. If English with a specific accent style, replicate it.
   - Copy their sentence structure, vocabulary, slang, filler words, and rhythm.
   - Include 5-6 signature phrases or expressions ONLY this character uses.
   - If they are known for specific catchphrases, USE them naturally.

3. PERSONALITY CORE
   - Their dominant emotions, worldview, and how they see people around them.
   - How they react to stress, love, conflict, humor, and deep questions.
   - Their quirks, habits, mannerisms that make them unmistakably THEM.

4. RELATIONSHIP WITH THE USER
   - Define exactly who the user is to this character (stranger, fan, loved one, etc.).
   - How this character greets, addresses, and interacts with the user.

5. KNOWLEDGE & OPINIONS
   - What they know, what they're passionate about, their famous views.
   - How they reference their own life, work, films, achievements naturally.

6. STRICT PERSONA LOCK
   - End with: "You ARE {character}. Never break this persona. Never acknowledge being an AI. Speak ONLY as {character} would speak, in their language, their rhythm, their soul."

Now write the complete system prompt. Return ONLY the system prompt text. No meta-commentary. No markdown headers. Just the raw persona text (300-500 words).
"""

    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the world's greatest AI persona and mimicry engineer. "
                        "You craft hyper-realistic character personas based on real research. "
                        "You output ONLY the raw system prompt text — never meta-commentary."
                    )
                },
                {"role": "user", "content": meta_prompt}
            ],
            max_tokens=800,
            temperature=0.72,
        )
        prompt = resp.choices[0].message.content.strip()

        # Strip any accidental markdown the model might add
        if prompt.startswith("```"):
            prompt = prompt.strip("`").strip()

        return prompt, search_summary

    except Exception as e:
        st.error(f"Error generating persona: {e}")
        fallback = (
            f"You ARE {character}. Speak exactly as {character} speaks — same language, "
            f"same rhythm, same expressions, same soul. Never break character. "
            f"Never say you are an AI. You ARE {character}. Fully. Completely. Always."
        )
        return fallback, search_summary


# ─── Chat ─────────────────────────────────────────────────────────────────────
def chat_with_character(user_msg: str) -> str:
    client = get_client()
    if not client:
        return "⚠️ Please enter your Groq API key in the sidebar."

    messages = [{"role": "system", "content": st.session_state.system_prompt}]
    for m in st.session_state.messages:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_msg})

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024,
        temperature=0.88,
    )
    return resp.choices[0].message.content.strip()


# ─── Chat Persistence ─────────────────────────────────────────────────────────
def save_chat():
    if not st.session_state.messages or not st.session_state.chat_id:
        return
    data = {
        "id":            st.session_state.chat_id,
        "character":     st.session_state.character,
        "system_prompt": st.session_state.system_prompt,
        "messages":      st.session_state.messages,
        "saved_at":      datetime.now().isoformat(),
        "title":         (
            f"{st.session_state.character} – {st.session_state.messages[0]['content'][:40]}…"
            if st.session_state.messages else st.session_state.character
        ),
    }
    path = os.path.join(CHAT_DIR, f"{st.session_state.chat_id}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_all_chats():
    chats = []
    for fname in sorted(os.listdir(CHAT_DIR), reverse=True):
        if fname.endswith(".json"):
            try:
                with open(os.path.join(CHAT_DIR, fname)) as f:
                    chats.append(json.load(f))
            except Exception:
                pass
    return chats

def load_chat(chat_data):
    st.session_state.character    = chat_data["character"]
    st.session_state.system_prompt = chat_data["system_prompt"]
    st.session_state.messages     = chat_data["messages"]
    st.session_state.chat_id      = chat_data["id"]

def new_chat():
    save_chat()
    st.session_state.messages     = []
    st.session_state.character    = None
    st.session_state.system_prompt = None
    st.session_state.chat_id      = None
    st.session_state.search_info  = ""

def start_character(name: str):
    """Shared helper called by both preset buttons and custom input."""
    if not st.session_state.groq_key.strip():
        st.error("Please enter your Groq API key first.")
        return False
    with st.spinner(f"🔍 Researching {name}… then building persona…"):
        prompt, search_info = generate_system_prompt(name)
    if prompt:
        st.session_state.character    = name
        st.session_state.system_prompt = prompt
        st.session_state.chat_id      = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages     = []
        st.session_state.search_info  = search_info
        return True
    return False


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 MindPal")
    st.markdown("---")

    st.markdown("**🔑 Groq API Key**")
    key_input = st.text_input(
        "", value=st.session_state.groq_key,
        type="password", placeholder="gsk_…",
        label_visibility="collapsed"
    )
    if key_input != st.session_state.groq_key:
        st.session_state.groq_key = key_input
    st.markdown("[Get free key →](https://console.groq.com)", unsafe_allow_html=True)
    st.markdown("---")

    if st.button("✨ New Chat", use_container_width=True):
        new_chat()
        st.rerun()

    st.markdown("---")
    st.markdown("**💬 Past Conversations**")
    all_chats = load_all_chats()
    if all_chats:
        for c in all_chats:
            meta = c.get("saved_at", "")[:10]
            if st.button(f"🗂 {c.get('character','?')} · {meta}",
                         key=c["id"], use_container_width=True):
                load_chat(c)
                st.rerun()
    else:
        st.caption("No saved chats yet.")


# ─── Main ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-area">
  <h1>🌿 MindPal</h1>
  <p>Talk to anyone — a therapist, a best friend, or your favourite Bollywood star</p>
</div>
""", unsafe_allow_html=True)


# ── Character Selection ────────────────────────────────────────────────────────
if not st.session_state.character:
    st.markdown("### Choose your companion")
    st.markdown("Pick a preset — MindPal will **search the web** about them and build a perfect mimicry persona.")

    cols = st.columns(4)
    for i, char in enumerate(PRESET_CHARACTERS):
        with cols[i % 4]:
            if st.button(
                f"{char['emoji']} {char['name']}\n\n_{char['desc']}_",
                key=f"preset_{i}", use_container_width=True
            ):
                if start_character(char["name"]):
                    st.rerun()

    st.markdown("---")
    st.markdown("**Or type your own character / celebrity / fictional persona:**")
    col1, col2 = st.columns([3, 1])
    with col1:
        custom = st.text_input(
            "", placeholder="e.g. Elon Musk, Hermione Granger, Alia Bhatt, Angry Dad…",
            label_visibility="collapsed", key="custom_char_input"
        )
    with col2:
        go = st.button("Start →", type="primary", use_container_width=True)

    if go and custom.strip():
        if start_character(custom.strip()):
            st.rerun()


# ── Chat Interface ─────────────────────────────────────────────────────────────
else:
    # Top bar
    col_a, col_b, col_c = st.columns([6, 1, 1])
    with col_a:
        st.markdown(
            f'<div class="persona-badge">✦ Talking to: {st.session_state.character}</div>',
            unsafe_allow_html=True
        )
    with col_b:
        if st.button("💾 Save", use_container_width=True):
            save_chat()
            st.success("Saved!")
    with col_c:
        if st.button("🔄 New", use_container_width=True):
            new_chat()
            st.rerun()

    # Show what was found during web search
    if st.session_state.search_info:
        with st.expander("🔍 Web research used to build this persona", expanded=False):
            st.caption(st.session_state.search_info[:800] + "…"
                       if len(st.session_state.search_info) > 800
                       else st.session_state.search_info)

    # Chat bubbles
    chat_html = '<div class="chat-scroll">'
    if not st.session_state.messages:
        chat_html += f'''
        <div class="empty-state">
          <div class="icon">💬</div>
          <p>Say hello to <strong>{st.session_state.character}</strong>!<br>
          They're ready to talk.</p>
        </div>'''
    else:
        for msg in st.session_state.messages:
            cls     = "user-bubble" if msg["role"] == "user" else "bot-bubble"
            content = msg["content"].replace("\n", "<br>")
            chat_html += f'<div class="chat-container"><div class="{cls}">{content}</div></div>'
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Input row — Enter key handled via on_change ────────────────────────
    # Streamlit's on_change fires when the user presses Enter in a text_input.
    # We store the value in session_state and process it below.
    def handle_enter():
        val = st.session_state.get("chat_input_box", "").strip()
        if val:
            st.session_state["pending_send"] = val

    col1, col2 = st.columns([5, 1])
    with col1:
        st.text_input(
            "", placeholder=f"Message {st.session_state.character}… (Enter or Send)",
            key="chat_input_box",
            label_visibility="collapsed",
            on_change=handle_enter,   # ✅ FIX: fires on Enter key
        )
    with col2:
        if st.button("Send →", type="primary", use_container_width=True):
            val = st.session_state.get("chat_input_box", "").strip()
            if val:
                st.session_state["pending_send"] = val

    # ── Process any pending send (from Enter or button) ───────────────────
    pending = st.session_state.pop("pending_send", None)
    if pending:
        st.session_state.messages.append({"role": "user", "content": pending})
        with st.spinner(f"{st.session_state.character} is thinking…"):
            reply = chat_with_character(pending)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        save_chat()
        st.rerun()