# Debug script to check segment connections
import json

with open('segments_2.json') as f:
    segments = json.load(f)

rated_segments = [1762, 838, 836, 857, 1052]

print("Checking connections between rated segments:")
print("=" * 50)

# Create a map of endpoints to segments
endpoints = {}
for seg in segments:
    if seg['segment_id'] in rated_segments:
        coords = seg['coordinates']
        start = tuple(coords[0])
        end = tuple(coords[-1])
        
        if start not in endpoints:
            endpoints[start] = []
        if end not in endpoints:
            endpoints[end] = []
        
        endpoints[start].append(seg['segment_id'])
        endpoints[end].append(seg['segment_id'])

print("Shared endpoints:")
for point, segs in endpoints.items():
    if len(segs) > 1:
        print(f"Point {point}: Segments {segs} are connected!")

print("\nSegment paths:")
for seg_id in rated_segments:
    for seg in segments:
        if seg['segment_id'] == seg_id:
            coords = seg['coordinates']
            print(f"Segment {seg_id}: {len(coords)} points")
            print(f"  Start: {coords[0]}")
            print(f"  End: {coords[-1]}")
            break
