# Realistic walking demo along connected segments
import time

# Create GPS points that follow the actual connected segments
now = int(time.time())

# This follows segments: 768 -> 837 -> 857 -> 1081
realistic_gps_stream = [
    # Start of segment 768
    {"lat": 13.0887156, "lng": 80.2103283, "timestamp": now},
    {"lat": 13.0885000, "lng": 80.2103000, "timestamp": now + 3},
    {"lat": 13.0882882, "lng": 80.2102796, "timestamp": now + 6},  # End of 768
    
    # Transition to segment 837
    {"lat": 13.0882349, "lng": 80.2108935, "timestamp": now + 9},
    {"lat": 13.0881500, "lng": 80.2109000, "timestamp": now + 12},
    {"lat": 13.0881228, "lng": 80.2109293, "timestamp": now + 15},  # End of 837
    
    # Transition to segment 857  
    {"lat": 13.0886711, "lng": 80.2114846, "timestamp": now + 18},
    {"lat": 13.0886500, "lng": 80.2114000, "timestamp": now + 21},
    {"lat": 13.0886397, "lng": 80.2123000, "timestamp": now + 24},  # End of 857
    
    # Transition to segment 1081
    {"lat": 13.0892326, "lng": 80.2115159, "timestamp": now + 27},
    {"lat": 13.0892000, "lng": 80.2118000, "timestamp": now + 30},
    {"lat": 13.0892033, "lng": 80.2123262, "timestamp": now + 33},  # End of 1081
    
    # Stop moving
    {"lat": 13.0892033, "lng": 80.2123262, "timestamp": now + 36},
    {"lat": 13.0892033, "lng": 80.2123262, "timestamp": now + 39},
    {"lat": 13.0892033, "lng": 80.2123262, "timestamp": now + 42},
]

print("realistic_gps_stream = [")
for point in realistic_gps_stream:
    print(f'    {{"lat": {point["lat"]}, "lng": {point["lng"]}, "timestamp": {point["timestamp"]}}},')
print("]")
