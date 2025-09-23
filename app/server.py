import os
import re
from datetime import datetime
from typing import List, Tuple

from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
from slack_sdk.signature import SignatureVerifier

from app.db import get_collection


load_dotenv()

app = Flask(__name__)

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "").strip()
signature_verifier = SignatureVerifier(signing_secret=SLACK_SIGNING_SECRET) if SLACK_SIGNING_SECRET else None


SUPPORTED_COLLECTIONS = {
    # user input -> collection name in MongoDB
    "newbrunswick": "new-brunswick",
    "new-brunswick": "new-brunswick",
    "princeton": "princeton",
    "jerseycity": "jersey-city",
    "jersey-city": "jersey-city",
    "newark": "newark",
    "camden": "camden",
}

ALL_KEYWORDS = {"nj", "all"}


def parse_args(text: str) -> Tuple[str, int]:
    """
    Parse arguments like: "newbrunswick 5" or "nj".
    Returns (region_or_all, limit)
    """
    text = (text or "").strip()
    if not text:
        return ("nj", 5)
    parts = re.split(r"\s+", text)
    region = parts[0].lower()
    limit = 5
    if len(parts) > 1:
        try:
            limit = max(1, min(50, int(parts[1])))
        except ValueError:
            limit = 5
    return (region, limit)


def query_events(region: str, limit: int) -> List[dict]:
    """Query MongoDB for recent events across one or all collections."""
    collections = []
    if region in ALL_KEYWORDS:
        collections = sorted(set(SUPPORTED_COLLECTIONS.values()))
    else:
        collection_name = SUPPORTED_COLLECTIONS.get(region)
        if not collection_name:
            return []
        collections = [collection_name]

    results: List[dict] = []
    for name in collections:
        col = get_collection(name)
        cursor = (
            col.find({}, {"_id": 0})
            .sort("scraped_at", -1)
            .limit(limit)
        )
        results.extend(list(cursor))

    # sort combined and trim to limit if querying ALL
    results.sort(key=lambda e: e.get("scraped_at", datetime.min), reverse=True)
    return results[:limit] if region in ALL_KEYWORDS else results


def format_events(region: str, events: List[dict]) -> str:
    if not events:
        if region in ALL_KEYWORDS:
            return "No recent events found across NJ collections."
        return f"No recent events found for '{region}'."

    lines = []
    for e in events:
        title = e.get("title", "Untitled")
        date = e.get("date", "Unknown date")
        location = e.get("location", "")
        url = e.get("url", "")
        loc = f" — {location}" if location else ""
        lines.append(f"• {title} — {date}{loc}\n{url}")
    return "\n\n".join(lines)


def verify_slack_request(req) -> bool:
    if not signature_verifier:
        # If no signing secret configured, reject for safety
        return False
    timestamp = req.headers.get("X-Slack-Request-Timestamp", "")
    signature = req.headers.get("X-Slack-Signature", "")
    body = req.get_data().decode("utf-8")
    return signature_verifier.is_valid(body=body, timestamp=timestamp, signature=signature)


@app.post("/slack/commands")
def slack_commands():
    if not verify_slack_request(request):
        abort(401)

    command = request.form.get("command", "")
    text = request.form.get("text", "")

    if command != "/events":
        return jsonify({
            "response_type": "ephemeral",
            "text": "Unsupported command. Try /events."
        })

    region, limit = parse_args(text)
    events = query_events(region, limit)
    response_text = format_events(region, events)

    # ephemeral response by default
    return jsonify({
        "response_type": "ephemeral",
        "text": response_text
    })


@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "time": datetime.utcnow().isoformat() + "Z"
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)


