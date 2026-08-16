# Tools

## OSINT Scraper

`osint-scraper.py` — Async parallel web scraper for gathering primary sources.

## Usage

```bash
python3 osint-scraper.py "Zecharia Sitchin Anunnaki" "Ebu Gogo folklore" "Claude Fable 5 safeguards"
```

## Features
- Asyncio + Semaphore(4) for parallel fetching
- curl backend with --connect-timeout 2 --max-time 8
- Regex href extraction
- JSON line output
