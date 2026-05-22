# PsychFlow AI

A **6-agent interview prep pipeline** that turns a recruiter message + job description + resume into a complete, US-tech-interview playbook: psychological profile of your interviewer, predicted questions, witty answers, and conversation-control tactics.

100% free stack — runs locally with a free [Groq](https://groq.com/) API key (any email, no Google account, no credit card).

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
| LLM | [Groq](https://console.groq.com/) running `openai/gpt-oss-120b` (free tier, no credit card) |
| Backend | Python 3.10+, FastAPI, `groq` SDK |
| Frontend | React 18, Vite, Tailwind CSS |
| Orchestration | `asyncio` (steps 2 & 3 run in parallel; 5 & 6 run in parallel) |

## Project layout

```
PsychFlow_AI/
├── backend/
│   ├── psychflow/
│   │   ├── agents/         # 6 agent files (one per agent)
│   │   ├── llm.py          # Groq wrapper
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

### Step 2 — Get a free Groq API key

1. Go to **<https://console.groq.com/keys>**
2. Sign up with **any email address** (Yahoo, Outlook, ProtonMail, work email — anything works)
3. Verify your email, then click **"Create API Key"** → name it anything (e.g. `psychflow`) → copy the key
4. The key starts with `gsk_...`. **No credit card, no Google account required.**

> Groq's free tier is genuinely usable for this project: huge daily token allowance and 5-10x faster output than most other providers.

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

Now open `backend/.env` and paste your Groq key:

```
GROQ_API_KEY=gsk_paste_your_key_here
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

The pipeline runs **6 Groq chat completions** per analysis. Steps 2/3 and 5/6 run in parallel for speed (typical run: 5-15 seconds).

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
| `GROQ_API_KEY` | — (required) | Your free Groq key (starts with `gsk_`) |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Swap in any free Groq model (see options below) |
| `ALLOWED_ORIGIN` | `http://localhost:5173` | CORS allow-list for the frontend |

### Other free Groq models you can try

Just change `GROQ_MODEL` in `backend/.env` and restart `uvicorn`:

| Model | When to use |
|---|---|
| `openai/gpt-oss-120b` | **Default** — strongest free model on Groq (OpenAI's open 120B) |
| `moonshotai/kimi-k2-instruct` | Very strong, long context |
| `llama-3.3-70b-versatile` | Solid all-rounder, faster than 120b |
| `qwen/qwen3-32b` | Strong reasoning |
| `llama-3.1-8b-instant` | Fastest, lowest quality (use for quick iteration) |

See the full list at <https://console.groq.com/docs/models>.

## Free-tier limits — good to know

Groq's free tier has a per-minute rate limit. One full pipeline run = **6 API calls**. If you run several runs back-to-back and hit the limit, just wait ~30-60 seconds and try again. See [current limits](https://console.groq.com/docs/rate-limits).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `GROQ_API_KEY is not set` | Make sure `backend/.env` exists and contains your key. Restart `uvicorn`. |
| `401 Unauthorized` from Groq | The key is wrong or got truncated when you pasted. Re-copy it from <https://console.groq.com/keys>. |
| `429 Too Many Requests` | You hit the free-tier rate limit — wait ~60 seconds. |
| `model_decommissioned` or "model not found" | Switch `GROQ_MODEL` in `backend/.env` to one from the list above. |
| Frontend shows `Failed to fetch` | The backend isn't running, or it's on a different port. Confirm `http://localhost:8000/api/health` works. |
| `CORS` errors in the browser console | Make sure the frontend is on `http://localhost:5173`, or update `ALLOWED_ORIGIN` in `backend/.env`. |
| `pip install` fails on Windows | Make sure you activated the venv (`.venv\Scripts\Activate.ps1`) and have Python 3.10+. |

## License

MIT — see [LICENSE](LICENSE).
