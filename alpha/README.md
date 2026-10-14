# Prospect research scraper

The native GitHub Actions workflow supports a broad United States search across
all 50 states and the District of Columbia. Its catalog uses more than 100
search locations, with multiple centers in each state. Select **nationwide** in
Actions > Google Maps nationwide and worldwide scraper.

Each run is bounded to 30 queries per project by default (up to 50). To cover
all categories and locations, run batches with offsets 0, 50, 100, 150, 200,
250, and 300. Start with depth 1 and concurrency 2. The workflow saves the
query list and CSV as artifacts. Google may limit results or block requests;
failed runs remain visible. Do not treat scraped contacts as verified delivery
addresses.

The original regional and worldwide modes remain available. The worldwide
catalog covers six continents and 37 cities/countries. English queries are a
first pass, not complete coverage of every country. Add local-language terms
and locations as needed.

The workflow builds the Go scraper and installs its matching Playwright
Chromium version on a GitHub Actions runner. Docker is not used. Nothing must
be installed on the user's Intel Mac.

Before outreach: verify the official site, recent activity, and public business
email; deduplicate by company, domain, and email against sent mail and drafts;
suppress bounces and opt-outs; and confirm recipient-region sending rules.
Scraped contacts are candidates for research, not verified recipients.
MediaMatch prospects also need a real announcement and a plausible story.
Draft only until approved.

Local Linux alternative: install the Go version required by go.mod, then run
`go build -o google-maps-scraper .`; install matching Playwright Chromium with
dependencies; create queries with
`python3 alpha/worldwide.py --project agents --region nationwide --limit 30`;
run `./google-maps-scraper -input queries.txt -results results.csv -depth 1 -c 2 -email -exit-on-inactivity 3m`.
macOS Monterey compatibility is not tested.

Python fallback (no Docker, Go, browser, Google Maps, or paid API): supply an
official-site CSV with `company,website` columns, then run:
`python3 alpha/official_sites.py --seeds seeds.csv --output evidence.jsonl`.
It reads up to three same-domain pages, records public email sources and errors,
and deduplicates input domains. It does not discover Maps listings, guess
emails, verify mail delivery, verify purchase intent, or send messages.
