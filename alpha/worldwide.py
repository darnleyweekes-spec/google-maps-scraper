"""Create bounded query batches for nationwide US and worldwide prospect research."""
import argparse
import json
from pathlib import Path

# Two or more search centers per state provide wider coverage than a single capital.
NATIONWIDE = [
    "Birmingham Alabama USA", "Mobile Alabama USA",
    "Anchorage Alaska USA", "Fairbanks Alaska USA",
    "Phoenix Arizona USA", "Tucson Arizona USA",
    "Little Rock Arkansas USA", "Fayetteville Arkansas USA",
    "Los Angeles California USA", "San Francisco California USA", "San Diego California USA", "Sacramento California USA",
    "Denver Colorado USA", "Colorado Springs Colorado USA",
    "Bridgeport Connecticut USA", "Hartford Connecticut USA",
    "Wilmington Delaware USA", "Dover Delaware USA",
    "Miami Florida USA", "Tampa Florida USA", "Orlando Florida USA", "Jacksonville Florida USA",
    "Atlanta Georgia USA", "Savannah Georgia USA",
    "Honolulu Hawaii USA", "Hilo Hawaii USA",
    "Boise Idaho USA", "Idaho Falls Idaho USA",
    "Chicago Illinois USA", "Springfield Illinois USA",
    "Indianapolis Indiana USA", "Fort Wayne Indiana USA",
    "Des Moines Iowa USA", "Cedar Rapids Iowa USA",
    "Wichita Kansas USA", "Topeka Kansas USA",
    "Louisville Kentucky USA", "Lexington Kentucky USA",
    "New Orleans Louisiana USA", "Baton Rouge Louisiana USA",
    "Portland Maine USA", "Bangor Maine USA",
    "Baltimore Maryland USA", "Rockville Maryland USA",
    "Boston Massachusetts USA", "Worcester Massachusetts USA",
    "Detroit Michigan USA", "Grand Rapids Michigan USA",
    "Minneapolis Minnesota USA", "Duluth Minnesota USA",
    "Jackson Mississippi USA", "Gulfport Mississippi USA",
    "Kansas City Missouri USA", "St Louis Missouri USA",
    "Billings Montana USA", "Missoula Montana USA",
    "Omaha Nebraska USA", "Lincoln Nebraska USA",
    "Las Vegas Nevada USA", "Reno Nevada USA",
    "Manchester New Hampshire USA", "Concord New Hampshire USA",
    "Newark New Jersey USA", "Trenton New Jersey USA",
    "Albuquerque New Mexico USA", "Santa Fe New Mexico USA",
    "New York New York USA", "Buffalo New York USA", "Albany New York USA",
    "Charlotte North Carolina USA", "Raleigh North Carolina USA",
    "Fargo North Dakota USA", "Bismarck North Dakota USA",
    "Columbus Ohio USA", "Cleveland Ohio USA",
    "Oklahoma City Oklahoma USA", "Tulsa Oklahoma USA",
    "Portland Oregon USA", "Eugene Oregon USA",
    "Philadelphia Pennsylvania USA", "Pittsburgh Pennsylvania USA",
    "Providence Rhode Island USA", "Warwick Rhode Island USA",
    "Charleston South Carolina USA", "Columbia South Carolina USA",
    "Sioux Falls South Dakota USA", "Rapid City South Dakota USA",
    "Nashville Tennessee USA", "Memphis Tennessee USA",
    "Houston Texas USA", "Dallas Texas USA", "Austin Texas USA", "San Antonio Texas USA",
    "Salt Lake City Utah USA", "Provo Utah USA",
    "Burlington Vermont USA", "Montpelier Vermont USA",
    "Richmond Virginia USA", "Virginia Beach Virginia USA",
    "Seattle Washington USA", "Spokane Washington USA",
    "Charleston West Virginia USA", "Huntington West Virginia USA",
    "Milwaukee Wisconsin USA", "Madison Wisconsin USA",
    "Cheyenne Wyoming USA", "Casper Wyoming USA",
    "Washington District of Columbia USA",
]

REGIONS = {
    "nationwide": NATIONWIDE,
    "north-america": ["New York USA", "Toronto Canada", "Mexico City Mexico", "Kingston Jamaica", "Portland Oregon USA", "Vancouver Washington USA", "Boise Idaho USA", "Austin Texas USA", "Pensacola Florida USA"],
    "south-america": ["Sao Paulo Brazil", "Buenos Aires Argentina", "Bogota Colombia", "Santiago Chile"],
    "europe": ["London UK", "Dublin Ireland", "Berlin Germany", "Paris France", "Madrid Spain", "Amsterdam Netherlands", "Stockholm Sweden", "Manchester UK"],
    "africa": ["Cape Town South Africa", "Nairobi Kenya", "Lagos Nigeria", "Accra Ghana", "Cairo Egypt"],
    "asia": ["Singapore", "Dubai UAE", "Mumbai India", "Kuala Lumpur Malaysia", "Tokyo Japan", "Manila Philippines", "Jakarta Indonesia"],
    "oceania": ["Auckland New Zealand", "Sydney Australia", "Suva Fiji", "Melbourne Australia"],
}
CATEGORIES = {
    "learn": ["independent branding studio", "boutique web design agency", "creative production studio"],
    "prime24ai": ["commercial cleaning", "property management", "bookkeeping"],
    "agents": ["commercial HVAC contractor", "plumbing contractor", "air conditioning service"],
    "mediamatch": ["craft chocolate maker", "specialty food producer", "independent skincare brand"],
}


def queries(project, region, offset, limit):
    regions = list(REGIONS) if region == "worldwide" else [region]
    cities = []
    for index in range(max(len(REGIONS[name]) for name in regions)):
        for name in regions:
            if index < len(REGIONS[name]):
                cities.append(REGIONS[name][index])

    categories = CATEGORIES[project]
    # Rotate categories across locations. The first batch reaches many places;
    # later offsets add the remaining categories for every location.
    candidates = []
    for category_round in range(len(categories)):
        for index, city in enumerate(cities):
            category = categories[(index + category_round) % len(categories)]
            candidates.append(f"{category} {city}")
    return candidates[offset:offset + limit]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", choices=CATEGORIES, required=True)
    parser.add_argument("--region", choices=["worldwide", *REGIONS], default="nationwide")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--output", default="queries.txt")
    args = parser.parse_args()
    if args.offset < 0 or not 1 <= args.limit <= 50:
        parser.error("offset must be non-negative and limit must be 1..50")
    result = queries(args.project, args.region, args.offset, args.limit)
    if not result:
        parser.error("No queries at this offset")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text("\n".join(result) + "\n", encoding="utf-8")
    print(json.dumps({
        "project": args.project,
        "region": args.region,
        "queries": len(result),
        "locations": len(NATIONWIDE) if args.region == "nationwide" else sum(len(REGIONS[name]) for name in REGIONS) if args.region == "worldwide" else len(REGIONS[args.region]),
        "batch_offset": args.offset,
    }))
