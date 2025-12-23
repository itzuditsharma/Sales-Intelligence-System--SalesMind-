import os
import time
import asyncio
import json
from django.core.management.base import BaseCommand
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.conf import settings

from ...upload_transcript.ingest import ingest_transcript
from ...active_deals.active_deals import find_active_deals
from ...objections.analyze_objections import find_objections
from ...analyze_transcript_llm_chart import analyze_transcript
from ...highlights import find_top_5_highlights
from ...active_sale_rep import count_sales_rep
from ...knowledge_graph import build_knowledge_graph
from ...generate_value import update_heatmap_json
from ...generate_json_call_logs import update_call_summaries_json
from ...views import update_total_deal_value_json  # import existing helper

# ----------- PATHS -----------
UPLOAD_DIR = os.path.join(settings.BASE_DIR, "uploaded_transcripts")
PROJECTS_JSON_PATH = os.path.join(settings.BASE_DIR, "salesmind_app/static/salesmind_app/data/projects.json")
OBJECTION_SUMMARY_FILE = os.path.join(settings.BASE_DIR, "objection_summary.json")

# ----------- Helper Functions -----------
def load_objection_summary():
    """Load objection summary JSON or return default structure."""
    if os.path.exists(OBJECTION_SUMMARY_FILE):
        try:
            with open(OBJECTION_SUMMARY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Corrupted objection_summary.json — resetting.")
    return {"price": 0, "feasibility": 0, "Tech Stack": 0, "Timeline": 0, "others": 0}


def save_objection_summary(summary):
    """Save updated objection summary JSON."""
    with open(OBJECTION_SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


# ----------- Watcher Event Handler -----------
class TranscriptHandler(FileSystemEventHandler):
    def on_created(self, event):
        """Triggered when a new file is added to uploaded_transcripts."""
        if event.is_directory or not event.src_path.endswith(('.txt', '.pdf', '.docx')):
            return

        file_path = event.src_path
        print(f"[Watcher] 📄 New transcript detected: {file_path}")

        async def process_transcript():
            try:
                # Ingest transcript
                ingest_result = ingest_transcript(file_path)
                print(f"[Watcher] Ingestion complete: {ingest_result}")

                # Read transcript content
                with open(file_path, "r", encoding="utf-8") as f:
                    transcript_text = f.read()

                # Detect active deals & objections concurrently
                deals_count, objections = await asyncio.gather(
                    find_active_deals(transcript_text),
                    find_objections(transcript_text)
                )

                print(f"[Watcher]  Active deals: {deals_count}")
                print(f"[Watcher]  Raw objections: {objections}")

                # Ensure objections is a valid dictionary
                if isinstance(objections, str):
                    try:
                        objections = json.loads(objections)
                    except json.JSONDecodeError:
                        print("[Watcher] Warning: objections returned a non-JSON string. Using defaults.")
                        objections = {"price": 0, "feasibility": 0, "Tech Stack": 0, "Timeline": 0, "others": 0}

                # Update objection summary file
                summary = load_objection_summary()
                for key, val in objections.items():
                    if key in summary and isinstance(val, int):
                        summary[key] += val
                save_objection_summary(summary)

                # Analyze transcript for proposal chart update
                proposal_json_path = os.path.join(
                    settings.BASE_DIR, "salesmind_app/static/salesmind_app/data/proposal_data.json"
                )
                analyze_transcript(file_path, proposal_json_path)

                # Update total deal value JSON
                total_value = update_total_deal_value_json()
                print(f"[Watcher] Updated total deal value: ₹{total_value}")

                # Update heatmap JSON
                heatmap_data = update_heatmap_json()
                print(f"[Watcher] Heatmap data updated.")

                # Update call summaries JSON
                call_summaries = update_call_summaries_json()
                print(f"[Watcher] Call summaries updated.")

                # Rebuild knowledge graph
                if os.path.exists(PROJECTS_JSON_PATH):
                    with open(PROJECTS_JSON_PATH, "r") as f:
                        projects = json.load(f)
                    project_names = [p["name"] for p in projects]
                    await build_knowledge_graph(file_path, project_names)
                    print(f"[Watcher] Knowledge graph rebuilt.")
                else:
                    print(f"[Watcher] No projects.json found at {PROJECTS_JSON_PATH}")

                # Generate highlights across all transcripts
                all_text = ""
                for filename in os.listdir(UPLOAD_DIR):
                    if filename.endswith(".txt"):
                        with open(os.path.join(UPLOAD_DIR, filename), "r", encoding="utf-8") as f:
                            all_text += f.read().strip() + "\n"
                await find_top_5_highlights(all_text)
                print(f"[Watcher] Top 5 highlights updated.")

                # Update active sales rep count
                count_sales_rep(UPLOAD_DIR)
                print(f"[Watcher] Sales rep count updated.")

                print(f"[Watcher] All tasks completed for {os.path.basename(file_path)}")

            except Exception as e:
                print(f"[Watcher] Error processing {file_path}: {e}")

        # Run the async task
        asyncio.run(process_transcript())


# ----------- Django Management Command -----------
class Command(BaseCommand):
    help = "Watch uploaded_transcripts folder and process transcripts automatically"

    def handle(self, *args, **options):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        event_handler = TranscriptHandler()
        observer = Observer()
        observer.schedule(event_handler, path=UPLOAD_DIR, recursive=False)
        observer.start()
        self.stdout.write(self.style.SUCCESS(f"Watching folder: {UPLOAD_DIR}"))

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
