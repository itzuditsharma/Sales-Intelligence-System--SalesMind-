import re
import json
from pathlib import Path

OUTPUT_JSON = "salesmind_app/static/salesmind_app/data/active_sales_reps.json"

def count_sales_rep(TRANSCRIPT_DIR):
    """
    Scans all transcript .txt files in a directory to extract unique sales rep names.
    Saves the count and names to OUTPUT_JSON.
    """
    all_text = ""
    for file in Path(TRANSCRIPT_DIR).glob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            all_text += f.read() + "\n"

    # Match both single-digit and double-digit months/days, and both dash types
    pattern = r"\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{2}\s+[–-]\s*([^:]+):"
    names = re.findall(pattern, all_text)

    # Clean up and deduplicate
    unique_names = sorted(set(name.strip() for name in names if name.strip()))

    # Prepare JSON data
    data = {
        "active_reps": len(unique_names),
        "names": unique_names
    }

    # Ensure output directory exists
    Path(OUTPUT_JSON).parent.mkdir(parents=True, exist_ok=True)

    # Save to JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Found {len(unique_names)} unique sales reps.")

    return data
