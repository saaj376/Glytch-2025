import osmnx as ox
import json
from shapely.geometry import LineString

# ------------------------------------------------------
# 1. DOWNLOAD OSM STREET NETWORK FOR ANNA NAGAR
# ------------------------------------------------------
def download_osm():
    print("Downloading OSM walking network for Anna Nagar...")
    G = ox.graph_from_place("Anna Nagar, Chennai, India", network_type="walk")
    print("Download complete.")
    return G


# ------------------------------------------------------
# 2. CONVERT OSM EDGES → SEGMENTS.JSON
# ------------------------------------------------------
def extract_segments(G):
    segments = []
    segment_id = 1

    print("Extracting street segments...")

    for u, v, key, data in G.edges(keys=True, data=True):

        # geometry
        if "geometry" in data:
            geom = data["geometry"]
        else:
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

    print(f"Extracted {len(segments)} segments.")
    return segments


# ------------------------------------------------------
# 3. BUILD NEIGHBORS.JSON (segments that touch each other)
# ------------------------------------------------------
def compute_neighbors(segments):
    print("Computing neighbors... (this may take some time)")

    from shapely.geometry import LineString

    line_map = {
        s["segment_id"]: LineString(s["coordinates"])
        for s in segments
    }

    neighbors = {}

    seg_ids = list(line_map.keys())

    for i in seg_ids:
        neighbors[i] = []
        line_i = line_map[i]

        for j in seg_ids:
            if i == j:
                continue

            if line_i.touches(line_map[j]):
                neighbors[i].append(j)

    print("Neighbor computation complete.")
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
    G = download_osm()

    segments = extract_segments(G)
    save_json("segments_2.json", segments)

    neighbors = compute_neighbors(segments)
    save_json("neighbors_2.json", neighbors)

    print("\n🎉 Person 1 tasks completed successfully!")
    print("Generated files: segments_2.json + neighbors_2.json")
