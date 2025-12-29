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
    <meta charset="utf-8">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        #map { height: 400px; width: 100%; margin-bottom: 20px; border-radius: 8px; border: 1px solid #ccc; }
        .quake { border-bottom: 1px solid #ddd; padding: 15px 0; }
        .location { font-weight: bold; font-size: 1.1em; }
        .magnitude { color: #c00; }
        .time { color: #666; font-size: 0.9em; }
        .coords { color: #666; font-size: 0.85em; }
        .updated { color: #999; font-size: 0.8em; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Earthquakes in the Last Hour</h1>
    <div id="map"></div>
    <p>Total: {{ quakes|length }}</p>
    {% if quakes %}
    {% for quake in quakes %}
    <div class="quake">
        <div class="location">{{ quake.place }}</div>
        <div class="magnitude">Magnitude: {{ quake.magnitude }}</div>
        <div class="time">{{ quake.time }}</div>
        <div class="coords">Coordinates: {{ quake.lat }}, {{ quake.lon }}</div>
    </div>
    {% endfor %}
    {% else %}
    <p>No earthquakes recorded in the last hour.</p>
    {% endif %}
    <p class="updated">Last updated: {{ updated }} (refreshes every minute)</p>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        try {
            var map = L.map('map').setView([39, -98], 4);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);

            var quakes = {{ quakes_json|safe }};
            var bounds = [];
            quakes.forEach(function(q) {
                if (q.lat && q.lon) {
                    bounds.push([q.lat, q.lon]);
                    var marker = L.circleMarker([q.lat, q.lon], {
                        radius: Math.max(q.magnitude * 3, 5),
                        color: '#c00',
                        fillColor: '#c00',
                        fillOpacity: 0.5
                    }).addTo(map);
                    marker.bindPopup('<b>' + q.place + '</b><br>Magnitude: ' + q.magnitude + '<br>' + q.time);
                }
            });
            if (bounds.length > 0) {
                map.fitBounds(bounds, {padding: [20, 20]});
            }
        } catch(e) {
            document.getElementById('map').innerHTML = '<p style="padding:20px;color:#c00;">Map failed to load: ' + e.message + '</p>';
        }
    </script>
</body>
</html>
"""


def fetch_earthquakes():
    """Fetch and parse earthquake data."""
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()

    quakes = []
    for feature in data.get("features", []):
        props = feature["properties"]
        coords = feature.get("geometry", {}).get("coordinates", [])

        timestamp = props.get("time")
        if timestamp:
            time_str = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = "Unknown"

        mag = props.get("mag")

        quakes.append({
            "place": props.get("place", "Unknown location"),
            "magnitude": mag if mag is not None else 0,
            "time": time_str,
            "lon": coords[0] if len(coords) > 0 else None,
            "lat": coords[1] if len(coords) > 1 else None
        })
    return quakes


@app.route("/")
def index():
    import json
    try:
        quakes = fetch_earthquakes()
    except requests.RequestException as e:
        return f"<h1>Error fetching earthquake data</h1><p>{e}</p>", 500

    updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template_string(HTML_TEMPLATE, quakes=quakes, quakes_json=json.dumps(quakes), updated=updated)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
