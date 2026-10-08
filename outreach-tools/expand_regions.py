#!/usr/bin/env python3
"""Generate broad Maps queries without Docker or third-party packages."""
import argparse
import json
from pathlib import Path

CITIES = {
    "US": ["Portland Oregon", "Vancouver Washington", "Seattle Washington", "Boise Idaho", "Denver Colorado", "Phoenix Arizona", "Reno Nevada", "Salt Lake City Utah", "Dallas Texas", "Austin Texas", "Chicago Illinois", "Atlanta Georgia", "Miami Florida", "Boston Massachusetts", "New York New York"],
    "UK": ["Bristol", "Manchester", "Leeds", "Birmingham"],
    "IE": ["Dublin", "Cork"],
    "NZ": ["Auckland", "Wellington", "Christchurch"],
    "AU": ["Sydney", "Melbourne", "Brisbane"],
    "SG": ["Singapore"],
}
SECTORS = ["commercial cleaning company", "commercial HVAC contractor", "independent food producer"]

def queries(countries):
    return [f"{sector} in {city}, {country}" for country in countries for city in CITIES[country] for sector in SECTORS]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--countries", nargs="+", choices=sorted(CITIES), default=list(CITIES))
    parser.add_argument("--output", default="queries-worldwide.txt")
    args = parser.parse_args()
    result = queries(list(dict.fromkeys(args.countries)))
    Path(args.output).write_text("\n".join(result) + "\n", encoding="utf-8")
    print(json.dumps({"queries": len(result), "countries": len(set(args.countries)), "output": args.output}))

if __name__ == "__main__":
    main()
