#!/usr/bin/env python3
"""Fetch and display recent earthquake data from USGS."""

import requests
from datetime import datetime

API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"


def fetch_earthquakes():
    """Fetch earthquake data from USGS API."""
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()


def format_time(timestamp_ms):
    """Convert millisecond timestamp to readable format."""
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def display_earthquakes(data):
    """Display earthquake information."""
    features = data.get("features", [])

    if not features:
        print("No earthquakes recorded in the last hour.")
        return

    print(f"\nEarthquakes in the last hour: {len(features)}\n")
    print("-" * 70)

    for quake in features:
        props = quake["properties"]
        place = props.get("place", "Unknown location")
        magnitude = props.get("mag", "N/A")
        time = format_time(props["time"])

        print(f"Location:  {place}")
        print(f"Magnitude: {magnitude}")
        print(f"Time:      {time}")
        print("-" * 70)


def main():
    try:
        data = fetch_earthquakes()
        display_earthquakes(data)
    except requests.RequestException as e:
        print(f"Error fetching earthquake data: {e}")


if __name__ == "__main__":
    main()
