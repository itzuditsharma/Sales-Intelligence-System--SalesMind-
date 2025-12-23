import os
import json
from collections import defaultdict
from openai import OpenAI
from django.conf import settings 
client = OpenAI()  # make sure your API key is configured

SYSTEM_PROMPT = """
You are an analyst. You will receive a transcript between a sales representative and a potential client.
Your job is to detect:
1. If the deal was lost.
2. If yes, extract the name of the COMPETITOR they selected or leaned towards.

Return only strict JSON in this exact format:
{
  "deal_lost": true/false,
  "competitor": "CompetitorName" or null
}
"""

def analyze_with_openai(text):
    """Send transcript to OpenAI and parse result."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print("⚠ Error processing with OpenAI:", e)
        return {"deal_lost": False, "competitor": None}

def update_heatmap_json():
    """Scan all uploaded transcripts and update deals_lost.json automatically"""
    uploaded_dir = os.path.join(settings.BASE_DIR, "uploaded_transcripts")
    loss_records = defaultdict(int)

    for filename in os.listdir(uploaded_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(uploaded_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                transcript = f.read()
                result = analyze_with_openai(transcript)
                print(f"Debug [{filename}]:", result)
                if result.get("deal_lost") and result.get("competitor"):
                    loss_records[result["competitor"]] += 1

    output_data = {
        "competitors": [{"name": name, "deals_lost": count} for name, count in loss_records.items()]
    }

    # Save JSON in static folder for front-end heatmap
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(APP_DIR, "static/salesmind_app/data/deals_lost.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("✅ Heatmap data updated automatically")
    return output_data
