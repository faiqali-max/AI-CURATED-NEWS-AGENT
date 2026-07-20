# AI-CURATED-NEWS-AGENT
# 🤖 AI-Curated Audio News Agent

An autonomous, multi-lingual Streamlit app that fetches live news headlines, curates the top stories using Google's Gemini AI, and reads the briefing aloud in your chosen language.

## 🌟 Core Agentic Concepts Implemented

To meet the core evaluation requirements of the Kaggle 5-Day AI Agents course, this project directly integrates the following design patterns:

- **Tool Use & External API Integration**:
  - `feedparser` Tool: Directly fetches dynamic, real-time Google News RSS payloads based on user-selected domains and custom search queries.
  - `gTTS` Tool (Google Text-to-Speech): Dynamic multi-lingual text-to-speech engine that converts curated textual briefings into audio streams on the fly.
- **Context & Structured System Prompting**:
  - Utilizes `gemini-2.5-flash` with strict system instructions to filter out clickbait/noise, restrict output to 3 core stories (2 sentences each), and enforce fluid translation across 10 target languages (including RTL script support for languages like Urdu and Arabic).
- **Sequential Agentic Workflow**:
  - Structured pipeline: Ingestion Agent (RSS Fetch) → Curation & Translation Agent (Gemini Synthesis) → Audio Broadcast Agent (TTS Synthesis & UI State) while it has made as a single agent all the things are done by a single agent but it can be called a Multi Agent due to this Ingestion Agent (RSS Fetch) → Curation & Translation Agent (Gemini Synthesis) → Audio Broadcast Agent (TTS Synthesis & UI State)

## Features

- **Live news fetching** from Google News RSS feeds
- **AI curation** — Gemini filters out duplicates and clickbait, picks the top 3 stories, and writes a two-sentence summary for each
- **Multi-language output** — briefings can be generated and translated into English, Urdu, Spanish, French, Arabic, Mandarin, Hindi, German, Portuguese, or Russian
- **Text-to-speech** — briefings can be read aloud using Google Text-to-Speech (gTTS), with native pronunciation for each supported language
- **News categories**:
  - Science *(with sub-discipline selection: Biology, Zoology, Botany, Genetics, Marine Biology, Physics, Astrophysics, Nuclear Physics, Quantum Physics, Chemistry, Environmental Science, Neuroscience, Geology)*
  - Geopolitics
  - Technology
  - Computer Science *(free-text topic search, e.g. "AI", "Cybersecurity", "Quantum Computing")*
  - Healthcare
  - Fitness
  - Space Exploration
- **Stop / Reset controls** to clear a briefing and start a new topic selection

## Live Demo

Once deployed, your app will be available at:
```
https://ai-curated-news-agent-nzmxndrloh2lgb4uumgi2c.streamlit.app/
```

## 📺 YouTube Video

Watch the project demo here:
```
https://youtu.be/Z-81KihMnHk
```

## Tech Stack

- [Streamlit](https://streamlit.io/) — web app framework
- [feedparser](https://pypi.org/project/feedparser/) — RSS feed parsing
- [google-genai](https://pypi.org/project/google-genai/) — Gemini API client
- [gTTS](https://pypi.org/project/gTTS/) — Google Text-to-Speech

## Setup — Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/faiqali-max/AI-CURATED-NEWS-AGENT.git
cd AI-CURATED-NEWS-AGENT

```
> Note: Only the judges can do these steps of cloning etc.

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Gemini API key

Get a free key from [Google AI Studio](https://aistudio.google.com/apikey).

Create a file at `.streamlit/secrets.toml` in the project folder:
```toml
GEMINI_API_KEY = "your-api-key-here"
```





## Deploy for Free — Streamlit Community Cloud

1. Push this repo to your GitHub account (make sure `agent.py` and `requirements.txt` are included, and `secrets.toml` is **not**)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **"Create app"** → select this repository → set main file to `agent.py`
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your-api-key-here"
   ```
5. Click **Deploy**

Your app will be live at a public `.streamlit.app` URL — no local server or firewall setup needed.

## Requirements File

`requirements.txt` should contain:
```
streamlit
feedparser
gtts
google-genai
```

## Notes & Limitations

- Text-to-speech uses gTTS, which requires an internet connection (it calls Google's TTS service) — this works both locally and when deployed.
- The "Stop / Reset" button clears the current session state between actions; it cannot interrupt a news-fetch or AI-generation call that is already in progress, since Streamlit runs each action as a single blocking pass.
- News results depend on Google News RSS availability and may vary in freshness by topic and region.

## License

Copyright (c) 2026 Faiq Ali. All Rights Reserved. (Educational review only)
