import os
import json
import re
import openai
from django.conf import settings

# Make sure you have set your OpenAI API key in environment
# export OPENAI_API_KEY="your_api_key_here"
openai.api_key = "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"
# openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_call_summary(filepath):
    """Uses OpenAI to extract team, customer, and discussion summary."""
    call_id = os.path.splitext(os.path.basename(filepath))[0]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            transcript_text = f.read().strip()

        prompt = f"""
        You are an AI assistant. Extract the following from the sales call transcript below:

        1. "team": list all speaker names (agents + customers)
        2. "customer": main customer contact (the person NOT on the sales team)
        3. "discussion": a concise 1-2 line summary of the call highlighting key points, objections, negotiations, or deal outcome.

        Transcript:
        \"\"\"{transcript_text}\"\"\"

        Return only a JSON object with keys: "id", "team", "customer", "discussion".
        Use the filename as "id": "{call_id}".
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that extracts structured JSON from sales call transcripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        json_text = response.choices[0].message.content.strip()

        # Ensure we only parse JSON
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', json_text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
            else:
                print(f"❌ Failed to parse JSON for {filepath}")
                data = None

        return data

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None


def update_call_summaries_json():
    """Scan all uploaded transcripts and update call_summaries.json automatically."""
    uploaded_dir = os.path.join(settings.BASE_DIR, "uploaded_transcripts")
    all_calls = []

    for filename in os.listdir(uploaded_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(uploaded_dir, filename)
            print(f"Processing {filename} for call summary...")
            call_data = extract_call_summary(filepath)
            if call_data:
                all_calls.append(call_data)

    # Save JSON in static folder
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(APP_DIR, "static/salesmind_app/data/call_logs.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_calls, f, indent=2, ensure_ascii=False)

    print(f"✅ Call summaries updated automatically. Total calls: {len(all_calls)}")
    return all_calls
