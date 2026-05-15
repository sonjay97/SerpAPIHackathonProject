import argparse
import os

from dataclasses import dataclass
from urllib.parse import urlparse

import serpapi
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

REPUTABLE_DOMAINS = {
    "reuters.com": "Reuters",
    "apnews.com": "Associated Press",
    "bbc.com": "BBC",
    "bbc.co.uk": "BBC",
    "nytimes.com": "New York Times",
    "washingtonpost.com": "Washington Post",
    "theguardian.com": "The Guardian",
    "npr.org": "NPR",
    "wsj.com": "Wall Street Journal",
    "bloomberg.com": "Bloomberg",
    "ft.com": "Financial Times",
    "economist.com": "The Economist",
    "cnn.com": "CNN",
    "nbcnews.com": "NBC News",
    "cbsnews.com": "CBS News",
    "abcnews.go.com": "ABC News",
    "axios.com": "Axios",
    "politico.com": "Politico",
}

@dataclass
class Story:
    title: str
    source: str
    domain: str
    link: str
    snippet: str
    date: str
    reputable: bool

def domain_of(url: str) -> str:
    """Grab URL"""

    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host

def to_story(item: dict) -> Story:
    """return Story item from link"""

    link = item.get("link") or ""
    domain = domain_of(link)
    source = (
        item.get("source", {}).get("name")
        if isinstance(item.get("source"), dict)
        else item.get("source")
    ) or REPUTABLE_DOMAINS.get(domain, domain or "Unknown")
    return Story(
        title=item.get("title", "(no title)"),
        source=source,
        domain=domain,
        link=link,
        snippet=item.get("snippet", "") or item.get("description", ""),
        date=item.get("date", ""),
        reputable=domain in REPUTABLE_DOMAINS
    )

def fetch(client: serpapi.Client, claim: str, max_results=5) -> list[Story]:
    """use serpapi lib to search for news article from reputable sources"""

    news = news = client.search({
        "engine": "google",
        "q": claim,
        "tbm": "nws",
        "hl": "en",
        "num": max_results
    })
    web = client.search({"engine": "google", "q": claim, "hl": "en", "num": 10})

    stories: list[Story] = []

    for item in news.get("news_results", [])[:10]:
        stories.append(to_story(item))
        for sub in item.get("stories", []) or []:
            stories.append(to_story(sub))

    for item in web.get("organic_results", [])[:10]:
        stories.append(to_story(item))
    seen, deduped = set(), []

    for s in stories:
        if s.link and s.link not in seen:
            seen.add(s.link)
            deduped.append(s)
    return deduped

def verdict(stories: list[Story]) -> tuple[str, str]:
    """return grade on if story is legitimate or not widely reported by mainstream media"""

    reputable = [s for s in stories if s.reputable]
    n_rep = len({s.domain for s in reputable})
    if n_rep >= 3:
        return "WIDELY REPORTED", "green"
    if n_rep >= 1:
        return "LIMITED MAINSTREAM COVERAGE", "yellow"
    if stories:
        return "NOT IN MAINSTREAM SOURCES — VERIFY CAREFULLY", "red"
    return "NO COVERAGE FOUND", "red"   

def render(console: Console, claim: str, stories: list[Story]) -> None:
    """Return list of stories and their fact checked grades"""

    label, color = verdict(stories)

    console.print(Panel.fit(f"[bold]Claim:[/bold] {claim}\n[bold {color}]{label}[/]", border_style=color))

    table = Table(title="Top coverage", show_lines=False)
    table.add_column("Tier", style="bold")
    table.add_column("Source")
    table.add_column("Headline")
    table.add_column("Date", style="dim")

    for s in stories[:10]:
        tier = "[green]Reputable[/]" if s.reputable else "[dim]Other[/]"
        table.add_row(tier, s.source, f"[link={s.link}]{s.title}[/link]", s.date)

    console.print(table)

def make_client() -> serpapi.Client:
    """Load SERPAPI_KEY from environment and return a configured client."""

    load_dotenv()
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise SystemExit("Missing SERPAPI_KEY. Copy .env.example to .env and set your key.")
    return serpapi.Client(api_key=api_key)


def main() -> None:
    parser = argparse.ArgumentParser(description="Quick news fact-check via SerpAPI.")
    parser.add_argument("claim", help="The claim or headline to check.")
    args = parser.parse_args()

    client = make_client()
    stories = fetch(client, args.claim)
    render(Console(), args.claim, stories)

if __name__ == "__main__":
    main()