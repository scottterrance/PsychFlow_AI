# PsychFlow AI

A **6-agent interview prep pipeline** that turns a recruiter message + job description + resume into a complete, US-tech-interview playbook: psychological profile of your interviewer, predicted questions, witty answers, and conversation-control tactics.

100% free stack — runs locally with a free Google Gemini API key.

```
[1] Data Parser
       |
       v
[2] Interviewer Psychologist  +  [3] Company & JD Analyst   (parallel)
       |                                  |
       +-----------------+----------------+
                         v
                [4] Question Predictor
                         |
       +-----------------+-----------------+
       v                                   v
[5] Answer Crafter                  [6] Airflow Strategist  (parallel)
```

## Stack

| Layer | Tech |
|---|---|
| LLM | [Google Gemini 2.0 Flash](https://aistudio.google.com/) (free tier, no credit card) |
| Backend | Python 3.10+, FastAPI, `google-genai` SDK |
| Frontend | React 18, Vite, Tailwind CSS |
| Orchestration | `asyncio` (steps 2 & 3 run in parallel; 5 & 6 run in parallel) |

## Project layout

```
PsychFlow_AI/
├── backend/
│   ├── psychflow/
│   │   ├── agents/         # 6 agent files (one per agent)
│   │   ├── llm.py          # Gemini wrapper
│   │   ├── pipeline.py     # orchestrates the 6 agents
│   │   └── schemas.py      # Pydantic request/response models
│   ├── main.py             # FastAPI app
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.jsx         # form + report UI
    │   ├── api.js          # calls /api/analyze
    │   └── index.css       # Tailwind layers
    ├── index.html
    ├── package.json
    └── vite.config.js
```

---

## Local setup (step-by-step)

### Prerequisites — install these once

| Tool | Version | Install |
|---|---|---|
| **Python** | 3.10+ | [python.org/downloads](https://www.python.org/downloads/) |
| **Node.js** | 18+ | [nodejs.org/en/download](https://nodejs.org/en/download) |
| **Git** | any | [git-scm.com/downloads](https://git-scm.com/downloads) |

Verify in your terminal:

```bash
python --version    # 3.10 or higher
node --version      # v18 or higher
npm --version
git --version
```

### Recommended VS Code extensions (optional but nice)

- **Python** (`ms-python.python`)
- **Pylance** (`ms-python.vscode-pylance`)
- **ES7+ React/Redux/React-Native snippets** (`dsznajder.es7-react-js-snippets`)
- **Tailwind CSS IntelliSense** (`bradlc.vscode-tailwindcss`)
- **Prettier** (`esbenp.prettier-vscode`)

### Step 1 — Clone the repo

```bash
git clone https://github.com/scottterrance/PsychFlow_AI.git
cd PsychFlow_AI
```

### Step 2 — Get a free Gemini API key

1. Go to **<https://aistudio.google.com/apikey>**
2. Sign in with your Google account
3. Click **"Create API key"** → copy the key (no credit card required)

### Step 3 — Set up the backend

Open a terminal in the project root:

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv

# Activate it:
#   macOS / Linux:
source .venv/bin/activate
#   Windows (PowerShell):
.venv\Scripts\Activate.ps1
#   Windows (cmd):
.venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Create your .env file from the example
cp .env.example .env       # macOS/Linux
copy .env.example .env     # Windows
```

Now open `backend/.env` and paste your Gemini key:

```
GEMINI_API_KEY=paste_your_key_here
```

Run the backend:

```bash
uvicorn main:app --reload --port 8000
```

You should see:

```
Uvicorn running on http://127.0.0.1:8000
```

Test it in another terminal:

```bash
curl http://localhost:8000/api/health
# {"status":"ok"}
```

Auto-generated API docs are at **<http://localhost:8000/docs>**.

### Step 4 — Set up the frontend

Open a **second** terminal (keep the backend running):

```bash
cd frontend
npm install
npm run dev
```

You should see:

```
VITE v5.x  ready in NNN ms
Local:   http://localhost:5173/
```

Open **<http://localhost:5173>** in your browser. Paste:

- the recruiter message
- the job description
- your resume (plain text)

Click **Run analysis** — the 6 agents run, and the report appears below. You can also download it as a Markdown file.

---

## How it works

| # | Agent | Input | Output |
|---|---|---|---|
| 1 | Data Parser | recruiter msg + JD + resume | structured JSON |
| 2 | Interviewer Psychologist | parsed data | 4-6 bullet psychology profile |
| 3 | Company & JD Analyst | JD + company hint | top skills, values, culture clues |
| 4 | Question Predictor | everything from 1-3 + JD + resume | 8-10 ranked questions |
| 5 | Answer Crafter | questions + resume + JD | witty 3-5-sentence answers |
| 6 | Airflow Strategist | everything | 4-6 conversation-control "moves" |

Each agent's system prompt lives in its own file under `backend/psychflow/agents/` — tweak the prompts, restart `uvicorn`, and you're iterating.

## Configuration

`backend/.env` (and `.env.example`):

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | — (required) | Your free Gemini key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Override to use another free Gemini model |
| `ALLOWED_ORIGIN` | `http://localhost:5173` | CORS allow-list for the frontend |

## Free-tier limits — good to know

Gemini's free tier has a per-minute rate limit. One full pipeline run = **6 API calls**. If you run several in a row and hit the limit, just wait ~30 seconds and try again. See the [current limits](https://ai.google.dev/gemini-api/docs/rate-limits).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `GEMINI_API_KEY is not set` | Make sure `backend/.env` exists and contains your key. Restart `uvicorn`. |
| Frontend shows `Failed to fetch` | The backend isn't running, or it's on a different port. Confirm `http://localhost:8000/api/health` works. |
| `CORS` errors in the browser console | Make sure the frontend is on `http://localhost:5173`, or update `ALLOWED_ORIGIN` in `backend/.env`. |
| Pipeline takes very long / times out | Free Gemini can be slow at peak times. Try once more — if it still fails, switch to `gemini-2.0-flash-lite` via `GEMINI_MODEL`. |
| `pip install` fails on Windows | Make sure you activated the venv (`.venv\Scripts\Activate.ps1`) and have Python 3.10+. |

## License

MIT — see [LICENSE](LICENSE).
