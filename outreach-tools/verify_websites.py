#!/usr/bin/env python3
"""Check imported Maps/website CSVs. Never infer email or buyer interest."""
import argparse
import csv
import datetime
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser

USER_AGENT = "Prime24AI-Research/1.0"
MAX_BYTES = 2_000_000
EMAIL = re.compile(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}")

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.text = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "a":
            self.links.append(dict(attrs).get("href", ""))
    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
    def handle_data(self, text):
        if not self.skip:
            self.text.append(text)

def parse_page(html):
    page = Page()
    page.feed(html)
    emails = set(EMAIL.findall(" ".join(page.text)))
    for link in page.links:
        if link.lower().startswith("mailto:"):
            emails.update(EMAIL.findall(urllib.parse.unquote(link[7:].split("?")[0])))
    return sorted(emails), page.links

def host(url):
    return (urllib.parse.urlsplit(url).hostname or "").lower().removeprefix("www.")

class SameSiteRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if host(req.full_url) != host(newurl):
            raise ValueError("Cross-domain redirect requires manual review")
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch(url):
    if urllib.parse.urlsplit(url).scheme not in ("http", "https"):
        raise ValueError("Only HTTP(S) websites are supported")
    opener = urllib.request.build_opener(SameSiteRedirect())
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(req, timeout=15) as response:
        if "text/html" not in response.headers.get("Content-Type", ""):
            raise ValueError("Not an HTML page")
        content = response.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            raise ValueError("Page exceeds byte limit")
        return response.geturl(), content.decode(response.headers.get_content_charset() or "utf-8", errors="replace")

def robots_allowed(url):
    root = urllib.parse.urlsplit(url)
    robots_url = urllib.parse.urlunsplit((root.scheme, root.netloc, "/robots.txt", "", ""))
    try:
        req = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.build_opener(SameSiteRedirect()).open(req, timeout=15) as response:
            rules = response.read(MAX_BYTES).decode("utf-8", errors="replace")
        parser = urllib.robotparser.RobotFileParser()
        parser.parse(rules.splitlines())
        return parser.can_fetch(USER_AGENT, url)
    except urllib.error.HTTPError as error:
        return error.code == 404
    except Exception:
        return False

def check(row):
    url = row.get("website", "").strip()
    result = dict(row, checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), published_emails=[], email_sources=[], status="HOLD", buyer_interest="unknown", errors=[])
    if not url:
        result["errors"].append("missing website")
        return result
    try:
        if not robots_allowed(url):
            raise ValueError("Robots access not allowed or unavailable")
        final, text = fetch(url)
        emails, links = parse_page(text)
        evidence = [{"email": email, "url": final} for email in emails]
        contacts = []
        for link in links:
            target = urllib.parse.urljoin(final, link)
            if host(target) == host(final) and re.search(r"contact|about|press", urllib.parse.urlsplit(target).path, re.I) and target not in contacts:
                contacts.append(target)
        for target in contacts[:3]:
            time.sleep(1)
            if not robots_allowed(target):
                continue
            try:
                landed, text = fetch(target)
                found, _ = parse_page(text)
                evidence.extend({"email": email, "url": landed} for email in found)
            except Exception as error:
                result["errors"].append(str(error))
        result["website"] = final
        result["published_emails"] = sorted({item["email"] for item in evidence})
        result["email_sources"] = evidence
        result["hold_reason"] = "Verify recent activity, buyer role, offer fit, existing solution, and prior contact before drafting. Public email does not prove deliverability."
    except Exception as error:
        result["errors"].append(str(error))
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="CSV with title/company and website; Maps export is supported")
    parser.add_argument("--output", default="website-evidence.jsonl")
    args = parser.parse_args()
    seen = set()
    count = 0
    with open(args.input, newline="", encoding="utf-8-sig") as source, open(args.output, "w", encoding="utf-8") as output:
        for row in csv.DictReader(source):
            domain = host(row.get("website", ""))
            if domain and domain in seen:
                continue
            seen.add(domain)
            output.write(json.dumps(check(row)) + "\n")
            output.flush()
            count += 1
            time.sleep(1)
    print(json.dumps({"checked": count, "output": args.output, "status": "manual qualification required"}))

if __name__ == "__main__":
    main()
