import osmnx as ox
import json
from shapely.geometry import LineString

# ------------------------------------------------------
# 1. DOWNLOAD OSM GRAPH - Greater Chennai Metropolitan Area
# ------------------------------------------------------
def download_osm(place=None):
    print("Downloading OSM road network for Greater Chennai Metropolitan Area...")
    
    # Greater Chennai bounds including:
    # - North: Avadi, Ambattur, Red Hills (13.35)
    # - South: Tambaram, Chromepet, Pallavaram (12.85)
    # - West: Airport, Poonamallee (80.05)
    # - East: OMR, ECR, Marina (80.35)
    
    NORTH = 13.35
    SOUTH = 12.85
    EAST = 80.35
    WEST = 80.05
    
    print(f"Bounding box: ({SOUTH}, {WEST}) to ({NORTH}, {EAST})")
    print("Covers: Avadi, Tambaram, Airport, OMR, ECR, and all of Chennai")
    
    G = ox.graph_from_bbox(bbox=(NORTH, SOUTH, EAST, WEST), network_type="drive")
    print(f"Downloaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G

# ------------------------------------------------------
# 2. CONVERT OSM EDGES INTO SEGMENTS.JSON
# ------------------------------------------------------
def extract_segments(G):
    segments = []
    segment_id = 1

    for u, v, key, data in G.edges(keys=True, data=True):
        # Geometry
        if "geometry" in data:
            geom = data["geometry"]
        else:
            # Construct simple geometry from nodes
            p1 = (G.nodes[u]["x"], G.nodes[u]["y"])
            p2 = (G.nodes[v]["x"], G.nodes[v]["y"])
            geom = LineString([p1, p2])

        coords = list(geom.coords)
        length = data.get("length", geom.length)
        osmid = data.get("osmid", None)

        segments.append({
            "segment_id": segment_id,
            "osmid": osmid,
            "u": u,
            "v": v,
            "length": length,
            "coordinates": coords
        })

        segment_id += 1

    return segments

# ------------------------------------------------------
# 3. BUILD NEIGHBOR RELATIONSHIPS
# ------------------------------------------------------
def compute_neighbors(segments):
    neighbors = {}

    # Convert coords to shapely lines
    shapely_segments = {
        s["segment_id"]: LineString(s["coordinates"])
        for s in segments
    }

    ids = list(shapely_segments.keys())

    print("Computing neighbors (this may take a moment)...")

    for i in ids:
        neighbors[i] = []
        for j in ids:
            if i == j: 
                continue
            # If two segments touch, they are neighbors
            if shapely_segments[i].touches(shapely_segments[j]):
                neighbors[i].append(j)

    return neighbors

# ------------------------------------------------------
# 4. SAVE JSON FILES
# ------------------------------------------------------
def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {filename}")

# ------------------------------------------------------
# MAIN
# ------------------------------------------------------
if __name__ == "__main__":
    G = download_osm("Chennai, Tamil Nadu, India")

    segments = extract_segments(G)
    save_json("segments.json", segments)

    #neighbors = compute_neighbors(segments)
    #save_json("neighbors.json", neighbors)

    print("Person 1 tasks completed successfully!")
