# YouTube Research Agent

An AI-powered agentic system that researches YouTube channels using a multi-step LangGraph workflow, enriches data via the YouTube Data API, and generates structured insights using Google Gemini.

Built as a production-grade AI capstone demonstrating multi-step agentic workflows, real API integrations, structured outputs, retry logic, observability, and clean architecture.

---

## What It Does

Given a search query, the agent:

1. **Searches** YouTube for relevant channels
2. **Enriches** each channel with detailed metadata and top videos
3. **Analyses** each channel using Gemini LLM — generates summaries, content themes, engagement rates, and posting frequency
4. **Synthesises** overall insights and actionable recommendations across all channels
5. **Notifies** via Slack (optional)

---

## Architecture

```text
POST /api/v1/research
        │
        ▼
┌─────────────────────────────────────────┐
│           LangGraph Agent               │
│                                         │
│  search_node → enrich_node →            │
│  summarise_node → notify_node           │
└─────────────────────────────────────────┘
        │              │              │
        ▼              ▼              ▼
  YouTube API     YouTube API     Gemini LLM
  (search)        (details +      (analysis +
                   videos)         insights)
```
## Agent Nodes
| Node | Responsibility |
|---|---|
| `search_node` | Searches YouTube for channels matching query |
| `enrich_node` | Fetches full channel details and top videos |
| `summarise_node` | Calls Gemini to analyse each channel and generate insights |
| `notify_node` | Sends Slack notification if enabled |


## Tech Stack

| Component | Technology | Why |
|---|---|---|
| API Framework | FastAPI | Async, fast, OpenAPI built-in |
| Agent Orchestration | LangGraph | Stateful multi-step agentic workflows |
| LLM | Google Gemini 2.0 Flash Lite | Structured JSON output, cost-efficient |
| Data Validation | Pydantic v2 | Strict typed models throughout |
| YouTube Data | YouTube Data API v3 | Official channel + video metadata |
| Notifications | Slack Webhook | Real-time research alerts |
| Logging | structlog | Structured JSON logs for observability |
| Retry Logic | tenacity | Exponential backoff on LLM failures |



## Project Structure
```text

youtube-research-agent/
├── app/
│   ├── api/
│   │   ├── health.py          # Deep health check endpoint
│   │   └── research.py        # Research endpoint
│   ├── agents/
│   │   ├── graph.py           # LangGraph workflow definition
│   │   └── nodes.py           # Agent node implementations
│   ├── core/
│   │   ├── config.py          # Settings and env vars
│   │   └── logger.py          # Structured logging setup
│   ├── models/
│   │   ├── agent.py           # AgentState model
│   │   ├── research.py        # Request/response models
│   │   └── youtube.py         # YouTube data models
│   ├── tools/
│   │   ├── gemini.py          # Gemini LLM integration
│   │   ├── youtube.py         # YouTube API integration
│   │   └── slack.py           # Slack webhook integration
│   └── main.py                # FastAPI app entry point
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

### Prerequisites

- Python 3.11+
- YouTube Data API v3 key
- Google Gemini API key
- Slack webhook URL (optional)

# Clone the repo
git clone https://github.com/yourhandle/youtube-research-agent.git
cd youtube-research-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Edit 
.env with your API keys

Environment Variables
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
SLACK_WEBHOOK_URL=your_slack_webhook_url

Run
bash
uvicorn app.main:app --reload

API Endpoints
POST /api/v1/research
Research YouTube channels for a given query.

Request:

json
{
  "query": "machine learning tutorials",
  "max_channels": 3,
  "max_videos_per_channel": 5,
  "notify_slack": false
}

Response:

json
{
  "query": "machine learning tutorials",
  "status": "completed",
  "channels": [
    {
      "channel": {
        "name": "Example Channel",
        "subscriber_count": 150000,
        "video_count": 320
      },
      "summary": "A channel focused on practical ML engineering...",
      "content_themes": ["Machine Learning", "Python", "Neural Networks"],
      "engagement_rate": 3.42,
      "posting_frequency": "Weekly",
      "top_videos": []
    }
  ],
  "overall_insights": "The ML tutorial space is dominated by...",
  "recommendations": [
    "Focus on hands-on project-based content",
    "Cover LLM fine-tuning — high demand, low supply",
    "Short-form clips of longer tutorials drive discovery"
  ]
}

GET /health
Deep health check — verifies all dependencies.

Response:

json
{
  "status": "ok",
  "version": "0.1.0",
  "dependencies": {
    "youtube": {"status": "ok", "reachable": true},
    "gemini": {"status": "ok", "reachable": true}
  }
}

Production Features
Feature	Implementation
Retry logic	Tenacity exponential backoff on Gemini calls
Graceful fallbacks	LLM failure returns basic metadata, never crashes
Structured logging	structlog JSON logs on every agent step
Input validation	Pydantic models on all inputs and outputs
Dependency health	/health checks YouTube + Gemini independently
Error isolation	Each agent node catches and logs failures independently
Observability
Every agent step emits a structured log:

json
{"event": "agent_step", "step": "search", "query": "python tutorials"}
{"event": "channel_enriched", "channel": "Example Channel"}
{"event": "gemini_channel_analysed", "channel": "Example Channel", "themes": []}
{"event": "gemini_insights_generated", "query": "python tutorials"}

Roadmap
 Docker + docker-compose setup
 Async parallel channel enrichment
 Response caching layer
 Evaluation harness for LLM output quality
 Cloud deployment (Railway / Render / AWS)
