# ALPHA outreach research without Docker

These scripts use Python 3.9+ and the standard library. They can run on an Intel Mac with Monterey. They do not require Go, Chromium, Docker, an API key, or a paid service.

Generate 84 search queries across 28 cities in six countries:

```sh
python3 outreach-tools/expand_regions.py
```

For Google Maps collection, pass that query file to an existing native scraper binary. The current fork's go.mod requires Go 1.27.1. The README's older minimum is inconsistent. Browser dependencies are still required for native Maps scraping; compatibility with Monterey has not been tested here.

```sh
./google-maps-scraper -input queries-worldwide.txt -results maps.csv -email -c 2 -depth 1 -exit-on-inactivity 3m
```

Alternative: use public web search to find official company URLs, save a CSV with `company,website`, then run the website checker. This route replaces Maps discovery and works without a browser. It does not pretend to have scraped Maps.

```sh
python3 outreach-tools/verify_websites.py companies.csv --output website-evidence.jsonl
```

Every result stays on HOLD. A public email is evidence of publication, not consent, delivery, buying intent, or a missing automation system. Verify buyer role, a dated recent event, one narrow paid scope, and mailbox history before a draft. Keep the exact source URL for every claim. Never invent dates, names, emails, savings, client results, or media coverage. Keep pain points conditional. Client approval remains required for external actions.

For these offers: Prime24AI installs one service request workflow; Prime24AI Agent runs one lead-to-next-action workflow; MediaMatch supplies one sourced press-fit report and pitch draft. MediaMatch does not send pitches or guarantee coverage. Geography is a discovery scope, not proof that each company is a suitable buyer.
