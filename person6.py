# person6_heatmap.py
import json

# ----------------------------------------------------
# LOAD SEGMENTS (Person 1)
# ----------------------------------------------------
with open("segments_2.json") as f:
    SEGMENTS = json.load(f)

# ----------------------------------------------------
# LOAD SCORES (Person 4)
# ----------------------------------------------------
try:
    with open("segment_scores_2.json") as f:
        SCORES = json.load(f)
except:
    print("⚠️ segment_scores.json not found. Using default neutral scores.")
    SCORES = {}

# ----------------------------------------------------
# COLOR GRADIENT BASED ON SCORE
# ----------------------------------------------------
def score_to_color(score):
    """
    Convert a safety score (0 to 1) → color.
    
    0.8–1.0  → GREEN
    0.5–0.8  → YELLOW
    0.0–0.5  → RED
    None     → GRAY (no data)
    """
    if score is None:
        return "#666666"   # dark gray (no data)

    if score >= 0.8:
        return "#00ff00"   # bright green
    if score >= 0.5:
        return "#ffaa00"   # bright orange-yellow
    return "#ff0066"       # bright pink-red

# ----------------------------------------------------
# BUILD GEOJSON FEATURES
# ----------------------------------------------------
features = []

for seg in SEGMENTS:
    seg_id = seg["segment_id"]
    coords = seg["coordinates"]

    score_entry = SCORES.get(str(seg_id))
    score_value = score_entry["score"] if score_entry else None

    color = score_to_color(score_value)

    feature = {
        "type": "Feature",
        "properties": {
            "segment_id": seg_id,
            "score": score_value,
            "color": color
        },
        "geometry": {
            "type": "LineString",
            "coordinates": coords   # OSM coordinates from Person 1
        }
    }

    features.append(feature)

# ----------------------------------------------------
# WRITE GEOJSON OUTPUT
# ----------------------------------------------------
geojson_output = {
    "type": "FeatureCollection",
    "features": features
}

with open("safety_heatmap.geojson", "w") as f:
    json.dump(geojson_output, f, indent=2)

print("\n🎉 Heatmap generated: safety_heatmap.geojson")
print("Load this GeoJSON in any OSM/Leaflet/OpenLayers viewer.")
