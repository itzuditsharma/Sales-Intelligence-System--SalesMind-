from django.shortcuts import render
import json
import os
import re
from django.conf import settings 
from django.http import JsonResponse

from .upload_transcript.ingest import ingest_transcript
from .upload_transcript.query import query_transcripts, generate_report, init_agent, create_document_chain

OBJECTION_SUMMARY_FILE = os.path.join(settings.BASE_DIR, "objection_summary.json")
UPLOADED_TRANSCRIPTS_PATH = os.path.join(settings.BASE_DIR,"uploaded_transcripts")

APP_DIR = os.path.dirname(os.path.abspath(__file__))

def index(request):
    file_path = os.path.join(APP_DIR, 'active_deals', 'deals.json')

    # Check if file exists and is not empty
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r') as f:
            try:
                deals = json.load(f)
            except json.JSONDecodeError:
                deals = []
    else:
        deals = []

    count = len(deals) if deals else 0
    json_path = os.path.join(os.path.dirname(__file__), "static/salesmind_app/data/proposal_data.json")
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return JsonResponse({"error": "JSON file not found"}, status=404)

    # Sum only numeric values
    proposal_count = sum(v for v in data.values() if isinstance(v, (int, float)))
    return render(request, 'index.html', {"active_deals": count, "proposal_count" : proposal_count})


def chat(request):
    return render(request, 'chat.html')

def knowledge_graph(request):
    return render(request, 'knowledge_graph.html')

def load_call_logs_data():
    
    json_file_path = os.path.join(settings.DATA_DIR, "call_logs.json")
    print(f"DEBUG: Attempting to load JSON from path: {json_file_path}") # CHECK 1
    
    try:
        with open(json_file_path, "r") as f:
            data = json.load(f)
            print(f"DEBUG: Successfully loaded {len(data)} items.") # CHECK 2
            return data
    except FileNotFoundError:
        print(f"Error: call.json not found at {json_file_path}. Returning empty list.")
        return []
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from call.json.")
        return []
    


# Regex to detect deal amounts
DEAL_REGEX = re.compile(
    r"(?:₹\s*|INR\s*)?([\d,]+(?:\.\d+)?(?:\s*Lakh[s]?)?)", 
    re.IGNORECASE
)

def parse_amount(match_str):
    """Convert extracted string to integer amount in INR safely"""
    match_str = match_str.replace(",", "").strip()
    if not match_str:
        return 0
    if "Lakh" in match_str or "Lakhs" in match_str:
        number = re.sub(r"[^\d.]", "", match_str)
        # print("Number", number)
        return int(float(number) * 100000)
    else:
        return int(float(match_str))
    

def update_total_deal_value_json():
    """Scan all uploaded transcripts and update total_deal_value.json"""
    uploaded_dir = os.path.join(settings.BASE_DIR, "uploaded_transcripts")
    total_value = 0
    deals = []

    for filename in os.listdir(uploaded_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(uploaded_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                for m in DEAL_REGEX.finditer(text):
                    amount = parse_amount(m.group(1))
                    total_value += amount
                    deals.append({"file": filename, "amount": amount})

    # Save JSON in static folder
    json_path = os.path.join(APP_DIR, "static/salesmind_app/data/total_deal_value.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"total_value": total_value}, f, indent=2, ensure_ascii=False)

    print(f"Total deal value updated automatically: ₹{total_value}")
    return total_value


def call_logs_list(request):
    call_logs = load_call_logs_data()
    
    context = {
        'call_logs_data_json': json.dumps(call_logs)
    }
    return render(request, 'call_logs.html', context)


def upload_transcript(request):
    if request.method != "POST" or "file" not in request.FILES:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    uploaded_file = request.FILES["file"]

    # Save uploaded file
    upload_dir = os.path.join(settings.BASE_DIR, "uploaded_transcripts")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, uploaded_file.name)

    try:
        with open(file_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
    except Exception as e:
        return JsonResponse({"error": f"Failed to save file: {e}"}, status=500)

    # Return JSON response
    return JsonResponse({
        "message": f"{uploaded_file.name} uploaded successfully!"
    })


def objections_summary(request):
    if os.path.exists(OBJECTION_SUMMARY_FILE):
        try:
            with open(OBJECTION_SUMMARY_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {
                "price": 0,
                "feasibility": 0,
                "Tech Stack": 0,
                "Timeline": 0,
                "others": 0
            }
    else:
        data = {
            "price": 0,
            "feasibility": 0,
            "Tech Stack": 0,
            "Timeline": 0,
            "others": 0
        }
    return JsonResponse(data)

def chat_query(request):
    """Handle chat queries from the frontend securely."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("message", "")
            
            if not question.strip():
                return JsonResponse({"error": "Empty message."}, status=400)
            
            _, llm = create_document_chain()
            tools = [query_transcripts, generate_report]
            agent_executor = init_agent(tools, llm)
            response = agent_executor.invoke({"input": question})
            return JsonResponse({"response": response["output"]})
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method."}, status=405)