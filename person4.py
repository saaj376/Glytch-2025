# person4_scoring_engine.py
import json
import math
import time

# ⭐ Import Person 3 feedback collector
from person3 import run_feedback_loop   # <-- IMPORTANT


# ---------------------------------------------------------
# TAG MODIFIERS
# ---------------------------------------------------------
TAG_EFFECTS = {
    "dark": -0.20,
    "isolated": -0.15,
    "harassment": -0.35,
    "dogs": -0.10,
    "crowd": +0.05,
    "excellent": +0.20
}

def tag_adjust(tags):
    return sum(TAG_EFFECTS.get(tag, 0) for tag in tags)


# ---------------------------------------------------------
# PERSONA EFFECT
# ---------------------------------------------------------
def persona_adjust(persona, tags):
    if persona == "woman" and "harassment" in tags:
        return -0.10
    return 0


# ---------------------------------------------------------
# TIME DECAY (newer feedback = stronger)
# ---------------------------------------------------------
def time_decay(age_seconds):
    days = age_seconds / 86400
    return math.exp(-0.08 * days)


# ---------------------------------------------------------
# SAFETY SCORING ENGINE
# ---------------------------------------------------------
def compute_segment_scores(feedback_list):
    now = int(time.time())

    grouped = {}
    for fb in feedback_list:
        grouped.setdefault(fb["segment_id"], []).append(fb)

    final_scores = {}

    for seg_id, fb_items in grouped.items():

        WeightedSum = 0
        TotalWeight = 0
        N = len(fb_items)

        for fb in fb_items:

            # Normalize rating
            base = fb["rating"] / 5  

            # Apply impact of tags
            adj = base + tag_adjust(fb["tags"])

            # Apply persona sensitivity
            adj += persona_adjust(fb["persona"], fb["tags"])

            # Clamp between 0 and 1
            adj = max(0, min(1, adj))

            # Weight strength based on recency + trust
            age = now - fb["timestamp"]
            w = time_decay(age) * fb["trust_weight"]

            WeightedSum += adj * w
            TotalWeight += w

        score = WeightedSum / TotalWeight if TotalWeight > 0 else 0.5

        # Confidence: more feedback = higher confidence
        confidence = 1 - math.exp(-N / 4)

        final_scores[seg_id] = {
            "segment_id": seg_id,
            "score": round(score, 3),
            "confidence": round(confidence, 3),
            "num_feedback": N
        }

    return final_scores


# ---------------------------------------------------------
# SAVE FOR PERSON 5 & 6
# ---------------------------------------------------------
def save_scores(scores, file="segment_scores_2.json"):
    with open(file, "w") as f:
        json.dump(scores, f, indent=2)
    print(f"\n💾 Scores saved to {file}")


# ---------------------------------------------------------
# MAIN: CONNECT PERSON 3 → PERSON 4
# ---------------------------------------------------------
if __name__ == "__main__":

    # DEMO: Continuous walking path that follows real roads
    now = int(time.time())

    continuous_gps_stream = [
        {"lat": 13.0899141, "lng": 80.2109923, "timestamp": now},
        {"lat": 13.0898944, "lng": 80.211551, "timestamp": now + 3},
        {"lat": 13.09057, "lng": 80.2110279, "timestamp": now + 6},
        {"lat": 13.0892524, "lng": 80.210971, "timestamp": now + 9},
        {"lat": 13.0886916, "lng": 80.2109522, "timestamp": now + 12},
        {"lat": 13.0887585, "lng": 80.2097662, "timestamp": now + 15},
        {"lat": 13.0886916, "lng": 80.2109522, "timestamp": now + 18},
        {"lat": 13.090044, "lng": 80.2103802, "timestamp": now + 21},
        {"lat": 13.0901932, "lng": 80.2103876, "timestamp": now + 24},
        {"lat": 13.0905913, "lng": 80.2103922, "timestamp": now + 27},
        {"lat": 13.0872882, "lng": 80.2102796, "timestamp": now + 30},
        {"lat": 13.0870536, "lng": 80.2102676, "timestamp": now + 33},
        {"lat": 13.0870536, "lng": 80.2102676, "timestamp": now + 36},
        {"lat": 13.0870536, "lng": 80.2102676, "timestamp": now + 39},
    ]

    print("\n📥 Collecting feedback from Person 3...")
    feedback = run_feedback_loop(continuous_gps_stream)

    print("\n📊 Computing safety scores...")
    scores = compute_segment_scores(feedback)

    print("\n🎉 FINAL SCORES FOR ALL SEGMENTS:")
    print(json.dumps(scores, indent=2))

    save_scores(scores)
