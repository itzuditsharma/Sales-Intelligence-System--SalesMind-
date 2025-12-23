import os
import re
import json
from datetime import datetime

# List of months for consistent JSON structure
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def get_month_name(date_str):
    """
    Converts a YYYY-M-D string to full month name (e.g. 'September').
    Handles both single and double-digit months/days.
    """
    for fmt in ("%Y-%m-%d", "%Y-%m-%d", "%Y-%m-%d"):
        try:
            # Try to normalize single-digit months/days
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%B")
        except ValueError:
            # Handle single-digit months/days by zero-padding manually
            parts = date_str.split("-")
            if len(parts) == 3:
                y, m, d = parts
                date_str_fixed = f"{y}-{int(m):02d}-{int(d):02d}"
                try:
                    date_obj = datetime.strptime(date_str_fixed, "%Y-%m-%d")
                    return date_obj.strftime("%B")
                except Exception:
                    continue
    return None


def is_proposal_message(text):
    """
    Detects if a message is related to a proposal.
    You can expand this keyword list for more accuracy.
    """
    proposal_keywords = [
        "proposal", "quote", "pricing", "estimate", "offer",
        "plan", "package", "costing", "revised proposal",
        "sending proposal", "updated quote", "pricing sheet"
    ]

    text_lower = text.lower()
    return any(keyword in text_lower for keyword in proposal_keywords)


def analyze_transcript(TRANSCRIPT_PATH, OUTPUT_PATH):
    """
    Analyzes a sales transcript to count proposal-related messages per month
    and updates/creates a JSON file with monthly counts.
    """
    # Read transcript lines
    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Initialize monthly counter
    monthly_count = {m: 0 for m in MONTHS}

    # Regex to match lines like:
    pattern = r"(\d{4}-\d{1,2}-\d{1,2})\s+\d{1,2}:\d{2}\s+[–-]\s*([^:]+):\s+(.*)"

    for line in lines:
        match = re.match(pattern, line)
        if not match:
            continue

        date_str, person, text = match.groups()
        month_name = get_month_name(date_str)
        if not month_name:
            continue

        # Check if this message is proposal-related
        if is_proposal_message(text):
            monthly_count[month_name] += 1

    # Load existing JSON if available
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = {m: 0 for m in MONTHS}

    # Merge counts
    for month, count in monthly_count.items():
        existing_data[month] = existing_data.get(month, 0) + count

    # Save updated data
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

    print(f"Proposal counts updated successfully in {OUTPUT_PATH}")
    print(f"Monthly proposal counts: {monthly_count}")
