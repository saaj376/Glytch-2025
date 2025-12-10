"""
Download Full Chennai Metropolitan Area Road Network from OpenStreetMap
"""
import osmnx as ox
import json
import time

print("=" * 60)
print("SafeTrace - Full Chennai Road Network Download")
print("=" * 60)

# Full Chennai Metropolitan Area bounding box
# North: 13.35, South: 12.75, West: 79.95, East: 80.35
NORTH = 13.35
SOUTH = 12.75
EAST = 80.35
WEST = 79.95

print(f"\nDownloading road network for Greater Chennai...")
print(f"Bounding Box: ({SOUTH}, {WEST}) to ({NORTH}, {EAST})")
print(f"This covers: Avadi, Ambattur, Airport, Tambaram, OMR, ECR, and more")
print("\nThis may take 5-10 minutes. Please wait...\n")

start_time = time.time()

# Configure OSMnx
ox.settings.log_console = True
ox.settings.use_cache = True  # Cache for faster subsequent runs
ox.settings.cache_folder = "./cache"

# Download the network - 'walk' mode for pedestrian paths
print("Step 1/4: Fetching road network from OpenStreetMap...")
try:
    G = ox.graph_from_bbox(
        bbox=(NORTH, SOUTH, EAST, WEST),
        network_type='walk',  # Pedestrian walkable roads
        simplify=True
    )
    print(f"✓ Downloaded graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
except Exception as e:
    print(f"Error downloading network: {e}")
    print("\nTrying with a smaller area (central Chennai only)...")
    # Fallback to smaller area
    G = ox.graph_from_bbox(
        bbox=(13.15, 12.90, 80.30, 80.15),
        network_type='walk',
        simplify=True
    )
    print(f"✓ Downloaded graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

# Convert to undirected for walking (can go both ways)
print("\nStep 2/4: Processing edges...")
G_undirected = ox.convert.to_undirected(G)

# Extract edges with geometry
print("Step 3/4: Extracting segment data...")
edges = ox.graph_to_gdfs(G_undirected, nodes=False)

segments = []
segment_id = 1

for idx, row in edges.iterrows():
    u, v, key = idx
    
    # Get coordinates from geometry
    if hasattr(row['geometry'], 'coords'):
        coords = list(row['geometry'].coords)
    else:
        # Fallback to node coordinates
        u_coords = (G_undirected.nodes[u]['x'], G_undirected.nodes[u]['y'])
        v_coords = (G_undirected.nodes[v]['x'], G_undirected.nodes[v]['y'])
        coords = [u_coords, v_coords]
    
    # Format coordinates as [lng, lat]
    coords_formatted = [[round(c[0], 7), round(c[1], 7)] for c in coords]
    
    segment = {
        "segment_id": segment_id,
        "osmid": row.get('osmid', row.get('osmid', 0)) if not isinstance(row.get('osmid'), list) else row.get('osmid')[0],
        "u": u,
        "v": v,
        "length": round(row.get('length', 0), 2),
        "coordinates": coords_formatted
    }
    
    # Add road name if available
    if 'name' in row and row['name']:
        segment['name'] = row['name'] if not isinstance(row['name'], list) else row['name'][0]
    
    segments.append(segment)
    segment_id += 1
    
    if segment_id % 50000 == 0:
        print(f"  Processed {segment_id} segments...")

print(f"✓ Extracted {len(segments)} segments")

# Save to file
print("\nStep 4/4: Saving to segments_full.json...")
with open('segments_full.json', 'w') as f:
    json.dump(segments, f)

# Also generate the heatmap
print("Generating safety_heatmap.geojson...")

def score_to_color(score):
    if score is None:
        return "#666666"
    if score >= 0.8:
        return "#00ff00"
    if score >= 0.5:
        return "#ffaa00"
    return "#ff0066"

features = []
for seg in segments:
    feature = {
        "type": "Feature",
        "properties": {
            "segment_id": seg["segment_id"],
            "score": None,
            "color": "#666666"
        },
        "geometry": {
            "type": "LineString",
            "coordinates": seg["coordinates"]
        }
    }
    features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open('safety_heatmap_full.geojson', 'w') as f:
    json.dump(geojson, f)

elapsed = time.time() - start_time
print(f"\n{'=' * 60}")
print(f"✅ DOWNLOAD COMPLETE!")
print(f"{'=' * 60}")
print(f"Time taken: {elapsed:.1f} seconds")
print(f"Total segments: {len(segments)}")
print(f"\nFiles created:")
print(f"  - segments_full.json")
print(f"  - safety_heatmap_full.geojson")
print(f"\nTo use this data, rename the files:")
print(f"  mv segments.json segments_old.json")
print(f"  mv segments_full.json segments.json")
print(f"  mv safety_heatmap.geojson safety_heatmap_old.geojson")
print(f"  mv safety_heatmap_full.geojson safety_heatmap.geojson")
print(f"\nThen restart the server!")
