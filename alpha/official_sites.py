"""Read supplied official sites without Docker, Go, Google Maps, or email sends."""
import argparse
import csv
import html
import json
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

MAX_BYTES = 2_000_000


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.text = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1
        values = dict(attrs)
        if tag == 'a' and values.get('href'):
            self.links.append(values['href'])

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, value):
        if not self.hidden and value.strip():
            self.text.append(value.strip())


def host(url):
    return (urlsplit(url).hostname or '').lower().removeprefix('www.')


def fetch(url):
    if urlsplit(url).scheme != 'https':
        raise ValueError('Only HTTPS official-site seeds are supported')
    request = Request(url, headers={'User-Agent': 'ALPHA-Official-Site-Research/1.0'})
    with urlopen(request, timeout=15) as response:
        final = response.geturl()
        if host(final) != host(url):
            raise ValueError('Cross-domain redirect needs manual review')
        if 'text/html' not in response.headers.get('Content-Type', ''):
            raise ValueError('Response is not HTML')
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ValueError('Page exceeds size limit')
        return body.decode('utf-8', errors='replace'), final


def research(name, seed, max_pages=3):
    queue = [seed]
    seen = set()
    pages, emails, errors = [], {}, []
    while queue and len(seen) < max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            source, final = fetch(url)
            page = Page()
            page.feed(source)
            visible = ' '.join(page.text)
            mailtos = [x[7:].split('?')[0] for x in page.links if x.startswith('mailto:')]
            for email in re.findall(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', html.unescape(visible + ' ' + ' '.join(mailtos))):
                emails.setdefault(email.lower(), []).append(final)
            pages.append({'url': final, 'text': visible[:20000]})
            for link in page.links:
                candidate = urljoin(final, link).split('#')[0]
                if (urlsplit(candidate).scheme == 'https' and host(candidate) == host(seed)
                        and re.search(r'contact|about|studio|work|project', urlsplit(candidate).path, re.I)
                        and candidate not in seen and candidate not in queue):
                    queue.append(candidate)
        except Exception as exc:
            errors.append({'url': url, 'error': str(exc)})
        if queue:
            time.sleep(0.25)
    return {'company': name, 'website': seed, 'checked_at': datetime.now(timezone.utc).isoformat(),
            'method': 'official-site research; not Google Maps data',
            'status': 'read' if pages else 'failed', 'emails': emails, 'pages': pages, 'errors': errors,
            'delivery_verified': False, 'purchase_intent_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seeds', required=True, help='CSV with company,website columns')
    parser.add_argument('--output', required=True, help='JSONL evidence output')
    parser.add_argument('--max-pages', type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.max_pages <= 5:
        parser.error('max-pages must be 1..5')
    with open(args.seeds, newline='', encoding='utf-8-sig') as source:
        rows = list(csv.DictReader(source))
    if not rows or len(rows) > 100 or any(not r.get('company') or not r.get('website') for r in rows):
        parser.error('Provide 1..100 rows with company and HTTPS website')
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    unique = {host(row['website']): row for row in rows}
    successes = 0
    with open(args.output, 'w', encoding='utf-8') as output:
        for row in unique.values():
            record = research(row['company'], row['website'], args.max_pages)
            output.write(json.dumps(record, ensure_ascii=False) + '\n')
            output.flush()
            successes += record['status'] == 'read'
            print(f"{row['company']}: {record['status']}; {len(record['emails'])} public emails", flush=True)
    if not successes:
        raise SystemExit('No sites read. Failures are recorded; no contacts inferred.')


if __name__ == '__main__':
    main()
