"""Create bounded worldwide query batches. Does not send email."""
import argparse
import json
from pathlib import Path

REGIONS = {
    "north-america": ["New York USA", "Toronto Canada", "Mexico City Mexico", "Kingston Jamaica"],
    "south-america": ["Sao Paulo Brazil", "Buenos Aires Argentina", "Bogota Colombia", "Santiago Chile"],
    "europe": ["London UK", "Dublin Ireland", "Berlin Germany", "Paris France", "Madrid Spain", "Amsterdam Netherlands", "Stockholm Sweden"],
    "africa": ["Cape Town South Africa", "Nairobi Kenya", "Lagos Nigeria", "Accra Ghana", "Cairo Egypt"],
    "asia": ["Singapore", "Dubai UAE", "Mumbai India", "Kuala Lumpur Malaysia", "Tokyo Japan", "Manila Philippines", "Jakarta Indonesia"],
    "oceania": ["Auckland New Zealand", "Sydney Australia", "Suva Fiji"],
}
CATEGORIES = {
    "prime24ai": ["commercial cleaning", "property management", "bookkeeping"],
    "agents": ["commercial HVAC contractor", "plumbing contractor", "air conditioning service"],
    "mediamatch": ["craft chocolate maker", "specialty food producer", "independent skincare brand"],
}

def queries(project, region, offset, limit):
    regions = list(REGIONS) if region == "worldwide" else [region]
    # Interleave regions so the first bounded batch covers six continents.
    cities = []
    for index in range(max(len(REGIONS[r]) for r in regions)):
        for r in regions:
            if index < len(REGIONS[r]):
                cities.append(REGIONS[r][index])
    candidates = [f"{category} {city}" for category in CATEGORIES[project] for city in cities]
    return candidates[offset:offset + limit]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", choices=CATEGORIES, required=True)
    parser.add_argument("--region", choices=["worldwide", *REGIONS], default="worldwide")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--output", default="queries.txt")
    args = parser.parse_args()
    if args.offset < 0 or not 1 <= args.limit <= 30:
        parser.error("offset must be non-negative and limit must be 1..30")
    result = queries(args.project, args.region, args.offset, args.limit)
    if not result:
        parser.error("No queries at this offset")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text("\n".join(result) + "\n", encoding="utf-8")
    print(json.dumps({"project": args.project, "region": args.region, "queries": len(result), "cities": sum(map(len, REGIONS.values()))}))
