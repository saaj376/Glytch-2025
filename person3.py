# person3_interactive_feedback.py
import time
from person2 import stream_segments

# --------------------------------------------------------
# TIME OF DAY
# --------------------------------------------------------
def time_of_day():
    hour = time.localtime().tm_hour
    if 5 <= hour < 11: return "morning"
    if 11 <= hour < 17: return "afternoon"
    if 17 <= hour < 22: return "evening"
    return "night"

# --------------------------------------------------------
# SIMPLE TRUST WEIGHT
# --------------------------------------------------------
def compute_trust():
    return 1.0  # can be extended later

# --------------------------------------------------------
# PERSON 3 MAIN LOOP
# --------------------------------------------------------
def run_feedback_loop(gps_stream):
    feedback_list = []

    for event in stream_segments(gps_stream):
        seg = event["completed_segment"]

        print(f"\n📍 You just completed segment {seg}.")

        user_input = input("Rate 1–5 or press Enter to skip: ").strip()

        # SKIP OPTION
        if user_input == "":
            print("Skipping this segment…")
            continue

        # USER RATED THIS SEGMENT
        rating = int(user_input)

        tags_input = input("Tags (dark, isolated, dogs…) or Enter to skip tags: ").strip()
        tags = [t.strip() for t in tags_input.split(",")] if tags_input else []

        feedback = {
            "segment_id": seg,
            "rating": rating,
            "tags": tags,
            "timestamp": event["timestamp"],
            "time_of_day": time_of_day(),
            "persona": "walker",
            "trust_weight": compute_trust()
        }

        feedback_list.append(feedback)

        print("💾 Saved rating:", feedback)

    print("\n🎉 All feedback collected:")
    print(feedback_list)
    return feedback_list


# --------------------------------------------------------
# DEMO GPS STREAM
# --------------------------------------------------------
if __name__ == "__main__":
    gps_stream = [
        {"lat": 13.0870, "lng": 80.2100, "timestamp": 1},  # Segment A
        {"lat": 13.0875, "lng": 80.2105, "timestamp": 5},  # Still Segment A  
        {"lat": 13.0880, "lng": 80.2110, "timestamp": 10}, # Segment A → Segment B
        {"lat": 13.0885, "lng": 80.2115, "timestamp": 15}, # Segment B
        {"lat": 13.0890, "lng": 80.2120, "timestamp": 20}, # Segment B → Segment C
        {"lat": 13.0895, "lng": 80.2125, "timestamp": 25}, # Segment C
    ]

    run_feedback_loop(gps_stream)
