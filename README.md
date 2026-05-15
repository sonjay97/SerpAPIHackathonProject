# SerpAPI News Fact-Check Demo

A small demo project that uses the [SerpAPI](https://serpapi.com) Python library to check how widely a claim or headline is reported by mainstream news outlets. Ships as both a CLI and a Streamlit web UI.

> **Note:** This tool measures _coverage_, not _truth_. Wide mainstream coverage is strong evidence a story is real, but the heuristic cannot detect nuance like "reputable outlets reported the claim and then debunked it." Always read the sources.

## What it does

Given a claim (e.g. `"NASA found liquid water on Mars"`), the app:

1. Queries Google News via SerpAPI.
2. Tags each result as **Reputable** (Reuters, AP, BBC, NYT, NPR, WaPo, Guardian, WSJ, Bloomberg, FT, etc.) or **Other**.
3. Returns a simple verdict based on how many reputable outlets cover the story:
   - 3+ reputable outlets → **Widely reported**
   - 1–2 reputable outlets → **Limited mainstream coverage**
   - 0 reputable outlets but results exist → **Not in mainstream sources — verify carefully**
   - 0 results → **No coverage found**

## Setup

Requires Python 3.13+ and [uv](https://github.com/astral-sh/uv).

```bash
uv sync
```

Create a `.env` file in the project root with your SerpAPI key (get one at [serpapi.com](https://serpapi.com/users/sign_up?plan=free)):

```text
SERPAPI_KEY=your_serpapi_key_here
```

`API_KEY` is also accepted as a fallback variable name.

## Usage

### Web UI (recommended)

```bash
uv run streamlit run app.py
```

Opens at `http://localhost:8501`. Enter a claim, pick how many results you want, and click **Check it**.

### CLI

```bash
uv run python fact_check.py "NASA found liquid water on Mars"
```

Prints a colored verdict panel and a table of top headlines in the terminal.

## Project structure

```
.
├── app.py           # Streamlit web UI
├── fact_check.py    # Core logic: SerpAPI fetch, verdict heuristic, CLI entry point
├── pyproject.toml   # uv-managed dependencies
└── README.md
```

## Ideas to extend

- LLM-based agreement/contradiction summary across the top snippets (mini Perplexity).
- Export results as JSON for downstream pipelines.
- Batch mode: feed a CSV of claims and produce a coverage report.
- Add Google Trends data to show interest-over-time alongside news coverage.
