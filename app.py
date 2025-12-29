#!/usr/bin/env python3
"""Simple web server to display earthquake data."""

from flask import Flask, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Recent Earthquakes</title>
    <meta http-equiv="refresh" content="60">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        .quake { border-bottom: 1px solid #ddd; padding: 15px 0; }
        .location { font-weight: bold; font-size: 1.1em; }
        .magnitude { color: #c00; }
        .time { color: #666; font-size: 0.9em; }
        .updated { color: #999; font-size: 0.8em; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Earthquakes in the Last Hour</h1>
    <p>Total: {{ quakes|length }}</p>
    {% if quakes %}
    {% for quake in quakes %}
    <div class="quake">
        <div class="location">{{ quake.place }}</div>
        <div class="magnitude">Magnitude: {{ quake.magnitude }}</div>
        <div class="time">{{ quake.time }}</div>
    </div>
    {% endfor %}
    {% else %}
    <p>No earthquakes recorded in the last hour.</p>
    {% endif %}
    <p class="updated">Last updated: {{ updated }} (refreshes every minute)</p>
</body>
</html>
"""


def fetch_earthquakes():
    """Fetch and parse earthquake data."""
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()

    quakes = []
    for feature in data.get("features", []):
        props = feature["properties"]
        quakes.append({
            "place": props.get("place", "Unknown location"),
            "magnitude": props.get("mag", "N/A"),
            "time": datetime.fromtimestamp(props["time"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        })
    return quakes


@app.route("/")
def index():
    quakes = fetch_earthquakes()
    updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template_string(HTML_TEMPLATE, quakes=quakes, updated=updated)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
