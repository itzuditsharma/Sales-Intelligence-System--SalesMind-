import os
import json
import openai
from dotenv import load_dotenv
load_dotenv
# Make sure you have set your OpenAI API key in environment
# export OPENAI_API_KEY="your_api_key_here"
openai.api_key = os.getenv("OPENAI_API_KEY")
# openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_call_summary(filepath):
    """
    Uses OpenAI to extract:
    - team: all speaker names (agents + customer)
    - customer: main customer
    - discussion: 1-2 line concise summary of the call
    """
    call_id = os.path.splitext(os.path.basename(filepath))[0]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            transcript_text = f.read().strip()
        
        prompt = f"""
        You are an AI assistant. Extract the following from the sales call transcript below:

        1. "team": a list of all speaker names (agents + customers)
        2. "customer": main customer contact (the person NOT on the sales team)
        3. "discussion": a concise 1-2 line summary of the call highlighting key points, objections, negotiations, or deal outcome.

        Transcript:
        \"\"\"
        {transcript_text}
        \"\"\"

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
        
        # Some models may return extra text, try to find JSON part
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            # Extract first { ... } block from text
            import re
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

def process_directory(input_dir, output_file="call_summaries.json"):
    """
    Process all .txt transcripts in a directory and extract summaries with team & customer info.
    """
    all_calls = []

    for filename in os.listdir(input_dir):
        filepath = os.path.join(input_dir, filename)
        if os.path.isfile(filepath) and filename.endswith(".txt"):
            print(f"Processing {filename}...")
            call_data = extract_call_summary(filepath)
            if call_data:
                all_calls.append(call_data)
    
    if all_calls:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_calls, f, indent=2)
        print(f"✅ Extraction complete! Saved {len(all_calls)} calls to {output_file}")
    else:
        print("⚠️ No calls were extracted.")

# --- Execution ---
if __name__ == "__main__":
    CALL_DIRECTORY = "./Transcripts_data"  # Folder with your transcript txt files
    if not os.path.exists(CALL_DIRECTORY):
        os.makedirs(CALL_DIRECTORY)
        print(f"Created directory {CALL_DIRECTORY}. Place transcript .txt files inside.")
    
    process_directory(CALL_DIRECTORY)