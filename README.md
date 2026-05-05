# 🌿 MindPal – Your AI Companion

Talk to a therapist, best friend, wife, life coach, or any Bollywood character — powered by Groq's free LLM API.

---

## ✨ Features

- **Dynamic Persona Generation** – Enter any character name and the app auto-generates a rich system prompt
- **8 Preset Characters** – Therapist, Best Friend, Wife, Life Coach, SRK, Ranveer Singh, Deepika, Kabir Singh
- **Custom Characters** – Type ANY character (e.g. "Angry Dad", "Alia Bhatt", "Stoic Mentor")
- **Chat History** – All chats auto-save; resume any past conversation from the sidebar
- **New Chat** – Start fresh anytime; old chat is saved automatically
- **Full Memory** – The model remembers your entire conversation when replying
- **Hinglish Support** – Bollywood characters respond in natural Hindi-English mix

---

## 🚀 Setup (3 Easy Steps)

### Step 1 – Get Your Free Groq API Key
1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up for free (no credit card needed)
3. Click **"Create API Key"** and copy it

### Step 2 – Install Dependencies
Open a terminal in this folder and run:

```bash
pip install -r requirements.txt
```

### Step 3 – Run the App

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501** in your browser.

---

## 🔑 Using the App

1. Paste your Groq API key in the **sidebar** (it's stored only in your session)
2. Pick a **preset character** or type a **custom one**
3. The app generates a persona prompt automatically — no setup needed!
4. Start chatting 💬
5. Use **"New Chat"** to start fresh — old chat saves automatically
6. Access past chats from the **sidebar history**

---

## 📁 Project Structure

```
mindpal/
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
├── .streamlit/
│   └── config.toml     # Theme configuration
├── chat_history/       # Auto-created: stores saved chats as JSON
└── README.md
```

---

## 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| **Streamlit** | Web UI framework |
| **Groq** | Free LLM API (llama3-8b-8192) |
| **llama3-8b-8192** | Fast, free model for chat & prompt generation |

---

## 💡 Example Characters to Try

- `Therapist` – Safe, professional emotional support
- `Shah Rukh Khan` – Romantic, philosophical, iconic
- `Best Friend` – Casual, honest, no-filter advice
- `Kabir Singh` – Intense, raw, emotional
- `Angry Dad` – Tough love with a soft heart
- `Motivational Coach` – High energy, goal-focused
- `Yoda` – Wise, mysterious, philosophical

---

## ❓ Troubleshooting

**App won't start?**
→ Make sure you're in the `mindpal/` folder when running `streamlit run app.py`

**API errors?**
→ Double-check your Groq API key in the sidebar

**Characters feel generic?**
→ Try being more specific: "Supportive Indian Mom" vs just "Mom"
