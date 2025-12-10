# person2_segment_stream.py
import json
import math
from shapely.geometry import Point, LineString

# ----------------------------------------------------
# LOAD SEGMENTS
# ----------------------------------------------------
with open("segments_2.json") as f:
    SEGMENTS = json.load(f)

SEG_LINES = {
    s["segment_id"]: LineString(s["coordinates"])
    for s in SEGMENTS
}

# ----------------------------------------------------
# HAVERSINE FOR TRIP START/END
# ----------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    p = math.pi/180
    a = 0.5 - math.cos((lat2-lat1)*p)/2 + \
        math.cos(lat1*p)*math.cos(lat2*p) * (1-math.cos((lon2-lon1)*p))/2
    return 2 * R * math.asin(math.sqrt(a))

# ----------------------------------------------------
# FIND CLOSEST SEGMENT TO GPS POINT
# ----------------------------------------------------
def find_segment(point):
    p = Point(point["lng"], point["lat"])
    closest = None
    min_d = float("inf")

    for seg_id, line in SEG_LINES.items():
        d = p.distance(line)
        if d < min_d:
            min_d = d
            closest = seg_id

    return closest


# ----------------------------------------------------
# MAIN STREAM ENGINE
# ----------------------------------------------------
def stream_segments(gps_stream):
    """
    Yields events whenever the user enters a new OSM segment.
    And yields the completed segment automatically.
    """

    prev_seg = None
    trip_started = False
    still_counter = 0
    prev_point = None

    for point in gps_stream:

        # ------------ TRIP START LOGIC ------------
        if prev_point:
            dist = haversine(prev_point["lat"], prev_point["lng"], point["lat"], point["lng"])
            dt = point["timestamp"] - prev_point["timestamp"]
            speed = dist / dt if dt > 0 else 0
        else:
            speed = 0

        if not trip_started and speed > 0.8:
            print("🚶‍♂️ Trip started!")
            trip_started = True

        if not trip_started:
            prev_point = point
            continue

        # ------------ SEGMENT DETECTION ------------
        current_seg = find_segment(point)

        if prev_seg is None:
            prev_seg = current_seg
            prev_point = point
            continue

        # SEGMENT CHANGED → USER FINISHED PREV SEGMENT
        if current_seg != prev_seg:
            yield {
                "completed_segment": prev_seg,
                "timestamp": point["timestamp"]
            }

        prev_seg = current_seg

        # ------------ TRIP END LOGIC ------------
        if speed < 0.5:
            still_counter += 1
            if still_counter > 2:
                print("🛑 Trip ended!")
                yield {"completed_segment": prev_seg, "timestamp": point["timestamp"]}
                return
        else:
            still_counter = 0

        prev_point = point
