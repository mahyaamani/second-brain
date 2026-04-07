# 🧠 Second Brain

A personal AI knowledge assistant that grows smarter over time. Ask it questions, give it articles to read, or let it interview you — it builds and maintains a persistent wiki of everything it learns.

## Features

- **Chat interface** — talk to your Second Brain naturally
- **Auto-research** — give it a topic and it searches the web, reads articles, and synthesizes knowledge into your wiki
- **Interviews** — it asks you focused questions and stores your answers as structured notes
- **Persistent wiki** — everything is saved as markdown pages, organized by category
- **Knowledge graph** — visual graph showing how concepts connect, built after every response
- **Activity log** — searchable log of everything your Second Brain has done

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/mahyaamani/second-brain.git
cd second-brain
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API key
Copy the example env file and add your [Anthropic API key](https://console.anthropic.com/):
```bash
cp .env.example .env
```
Edit `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### 5. Run
```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

## Usage examples

| What you type | What happens |
|---|---|
| `research stoicism` | Searches the web, reads top articles, builds wiki pages |
| `interview me about my fitness goals` | Asks you questions, stores answers as structured notes |
| `what do I know about nutrition?` | Reads your wiki and gives a personalized summary |
| `ingest https://example.com/article` | Fetches the article and adds key knowledge to your wiki |

## Project structure

```
second-brain/
├── app.py                  # Streamlit UI
├── agent.py                # Claude tool-use loop
├── main.py                 # CLI entry point (text or voice mode)
├── tools/
│   ├── wiki.py             # Read/write wiki pages
│   ├── web.py              # Web search and article fetching
│   ├── interaction.py      # User input handling
│   └── graph_extractor.py  # Knowledge graph extraction
├── voice/
│   ├── stt.py              # Speech-to-text (Google Cloud)
│   └── tts.py              # Text-to-speech (Google Cloud)
└── wiki/                   # Your persistent knowledge base (markdown)
```

## Voice mode (optional)

Voice mode uses Google Cloud Speech-to-Text and Text-to-Speech. Set up a GCP service account and add the path to your `.env`:
```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```
Then run:
```bash
python main.py --voice
```
