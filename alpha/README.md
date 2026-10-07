# Worldwide prospect research

The native GitHub Actions runner builds this fork with the Go version in go.mod.
It installs Chromium through the matching Playwright Go dependency. Docker is
not used. Nothing must be installed on the user's Intel Mac.

The initial run covers six continents, with six queries per project. The catalog
contains 30 cities/countries and three business categories per project. Use the
region, offset and query_limit inputs for later bounded batches. English queries
are a first pass, not complete coverage of every country. Add local-language
categories and cities when needed. Google can limit results or block requests.

Actions > Google Maps worldwide native scraper > Run workflow. Use depth 1 and
concurrency 2 first. Download the CSV and query-file artifacts. A failed or
blocked scrape must remain visible; use official-site web research as the
fallback. Never label fallback research as Maps data.

Before outreach: verify official site, dated activity and public business email;
deduplicate by company/domain/email against sent mail and drafts; suppress
bounces and opt-outs; confirm recipient-region sending rules. Scraped contacts
are research candidates, not verified delivery addresses. MediaMatch prospects
also need a real announcement and a plausible story. Draft only until approved.

Local Linux alternative: install the Go version required by go.mod, then run
`go build -o google-maps-scraper .`; install matching Playwright Chromium with
dependencies; create queries with `python3 alpha/worldwide.py --project agents`;
run `./google-maps-scraper -input queries.txt -results results.csv -depth 1 -c 2
-email -exit-on-inactivity 3m`. macOS Monterey compatibility is not tested.
