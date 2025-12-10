# Create a continuous walking path that follows real roads
import json
import time

# Load segments to find a real continuous path
with open('segments_2.json') as f:
    segments = json.load(f)

# Find segments that form a continuous path
# Let's find a path starting from a central point
target_area = [13.088, 80.211]  # Anna Nagar center

print("Finding continuous path segments...")
connected_segments = []

# Look for segments that can form a connected path
for seg in segments:
    coords = seg['coordinates']
    # Check if segment is near our target area
    if (abs(coords[0][1] - target_area[0]) < 0.002 and 
        abs(coords[0][0] - target_area[1]) < 0.002):
        connected_segments.append(seg)
        if len(connected_segments) >= 10:  # Get 10 connected segments
            break

print(f"Found {len(connected_segments)} segments for continuous path")

# Create GPS points that follow these segments
gps_stream = []
now = int(time.time())

for i, seg in enumerate(connected_segments[:8]):  # Use first 8 segments
    coords = seg['coordinates']
    # Add GPS points along this segment
    for j, coord in enumerate(coords):
        if j == 0 and i > 0:  # Skip duplicate start points (except first segment)
            continue
        gps_stream.append({
            "lat": coord[1], 
            "lng": coord[0], 
            "timestamp": now + len(gps_stream) * 3
        })

print("Continuous GPS stream:")
for point in gps_stream:
    print(f'    {{"lat": {point["lat"]}, "lng": {point["lng"]}, "timestamp": {point["timestamp"]}}},')
