# person5_routing.py
import json
from shapely.geometry import Point, LineString
import networkx as nx
import math


# --------------------------------------------------------------
# LOAD SEGMENTS FROM PERSON 1
# --------------------------------------------------------------
with open("segments_2.json") as f:
    SEGMENTS = json.load(f)

# Build graph for routing
G = nx.DiGraph()

for seg in SEGMENTS:
    u = seg["u"]
    v = seg["v"]
    length = seg["length"]
    seg_id = seg["segment_id"]

    # Add edge with basic attributes
    G.add_edge(u, v, length=length, segment_id=seg_id)
    G.add_edge(v, u, length=length, segment_id=seg_id)  # allow walking reverse


# --------------------------------------------------------------
# LOAD SAFETY SCORES FROM PERSON 4
# --------------------------------------------------------------
with open("segment_scores_2.json") as f:
    SCORES = json.load(f)


def get_safety_score(segment_id):
    if str(segment_id) in SCORES:
        return SCORES[str(segment_id)]["score"]
    return 0.5  # neutral score


# --------------------------------------------------------------
# GPS → FIND CLOSEST NODE IN GRAPH
# --------------------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    p = math.pi/180
    a = (0.5 - math.cos((lat2-lat1)*p)/2 +
         math.cos(lat1*p)*math.cos(lat2*p)*(1-math.cos((lon2-lon1)*p))/2)
    return 2 * R * math.asin(math.sqrt(a))


def find_closest_node(lat, lng):
    best_node = None
    best_dist = float("inf")

    for seg in SEGMENTS:
        for node in (seg["u"], seg["v"]):
            # We lookup node coordinates in SEGMENTS
            # Because Person 1's output has only segment coords,
            # we approximate node coord by segment endpoints.
            # So we need a static node->coord map
            pass

    # We must build a node coordinate lookup outside the loop
    return None  # fixed in next block


# --------------------------------------------------------------
# BUILD NODE COORD MAP ONCE
# --------------------------------------------------------------
NODE_COORDS = {}

for seg in SEGMENTS:
    u = seg["u"]
    v = seg["v"]
    coords = seg["coordinates"]

    if u not in NODE_COORDS:
        NODE_COORDS[u] = coords[0]
    if v not in NODE_COORDS:
        NODE_COORDS[v] = coords[-1]


def find_closest_node(lat, lng):
    best_node = None
    best_dist = float("inf")
    target = Point(lng, lat)

    for node, coord in NODE_COORDS.items():
        d = target.distance(Point(coord[0], coord[1]))
        if d < best_dist:
            best_dist = d
            best_node = node

    return best_node


# --------------------------------------------------------------
# SAFEST ROUTE WEIGHTING
# --------------------------------------------------------------
def compute_safest_route(G, start_node, end_node):
    G2 = G.copy()

    for u, v, data in G2.edges(data=True):
        seg_id = data["segment_id"]
        base_length = data["length"]
        score = get_safety_score(seg_id)

        # Higher score → safer → smaller weight
        # Weight formula:
        weight = base_length * (2 - score)

        data["weight"] = weight

    return nx.shortest_path(G2, start_node, end_node, weight="weight")


# --------------------------------------------------------------
# FASTEST ROUTE (LENGTH ONLY)
# --------------------------------------------------------------
def compute_fastest_route(G, start_node, end_node):
    return nx.shortest_path(G, start_node, end_node, weight="length")


# --------------------------------------------------------------
# CONVERT NODE ROUTE → COORDINATES (GEOJSON-READY)
# --------------------------------------------------------------
def route_to_coords(node_list):
    coords = []
    for node in node_list:
        x, y = NODE_COORDS[node]
        coords.append([x, y])
    return coords


# --------------------------------------------------------------
# GET SEGMENT IDS FROM NODE ROUTE
# --------------------------------------------------------------
def get_route_segment_ids(node_list):
    seg_ids = []
    for i in range(len(node_list)-1):
        u = node_list[i]
        v = node_list[i+1]
        seg_ids.append(G[u][v]["segment_id"])
    return seg_ids


# --------------------------------------------------------------
# MAIN FUNCTION FOR ROUTING
# --------------------------------------------------------------
def get_routes(start_lat, start_lng, end_lat, end_lng):
    start_node = find_closest_node(start_lat, start_lng)
    end_node = find_closest_node(end_lat, end_lng)

    print(f"Closest start node: {start_node}")
    print(f"Closest end node: {end_node}")

    fastest = compute_fastest_route(G, start_node, end_node)
    safest = compute_safest_route(G, start_node, end_node)

    return {
        "fastest_route": route_to_coords(fastest),
        "safest_route": route_to_coords(safest),
        "fastest_nodes": fastest,
        "safest_nodes": safest
    }


# --------------------------------------------------------------
# DEMO
# --------------------------------------------------------------
if __name__ == "__main__":
    start = (13.0870, 80.2100)
    end = (13.0895, 80.2125)

    routes = get_routes(start[0], start[1], end[0], end[1])

    print("\n🎉 FASTEST ROUTE COORDINATES:")
    print(routes["fastest_route"])

    print("\n🛡️ SAFEST ROUTE COORDINATES:")
    print(routes["safest_route"])

    print("\nFASTEST SEGMENTS:", get_route_segment_ids(routes["fastest_nodes"]))
    print("SAFEST SEGMENTS:", get_route_segment_ids(routes["safest_nodes"]))
