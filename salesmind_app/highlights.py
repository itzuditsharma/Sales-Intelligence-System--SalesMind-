from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput, AgentOutputSchema
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import Dict
import os
from pydantic import BaseModel
from typing import List
load_dotenv()

async def find_top_5_highlights(text):
    class HighlightProjOutput(BaseModel):
        project_highlights: Dict[str, str]
    
    instructions = """
    You are an efficient Trending Project Finder.

    You will be given a transcript of an internal organizational or sales meeting.

    Your task:
    1. Read the transcript carefully.
    2. Identify any important or trending topics such as:
    - Project launches, updates, or completions
    - Deal finalizations, renewals, or expansions
    - Achievements, milestones, or performance highlights (e.g., revenue numbers, success rates, targets met)
    3. For each identified topic, create a **key-value pair** where:
    - The key is a short, catchy highlight (like a headline)
    - The value is a brief (1–2 line) summary explaining the context or impact.

    <context>
    {context}
    </context>

    Return your output **only** in the form of a Python dictionary, where each key is a highlight and each value is its corresponding summary.

    Do not include any explanations, reasoning, or extra text.

    Return your output only in the form of a Python list of dictionaries.
    Each dictionary must have two keys:
    - "highlight": the main topic or achievement
    - "summary": its brief explanation.

    Return your output only as a **JSON object** with a single key `project_highlights`,
    where the value is a dictionary of highlight-summary pairs.

    Example:
    {
    "project_highlights": {
        "Ventron Healthcare deal finalized for Q4 rollout": "The team confirmed deal closure and expects rollout by end of Q4.",
        "Hydra Labs achieved 93% accuracy in AI diagnostics": "Performance metrics for the diagnostic model were validated."
    }
    }

    """
    schema = AgentOutputSchema(HighlightProjOutput, strict_json_schema=False)
    project_highlights_identifier_agent = Agent(
        name = "Project Highlights Identifier Agent",
        instructions=instructions,
        model = "gpt-4o", 
        output_type = schema
    )

    result = await Runner.run(project_highlights_identifier_agent, text)
    result = result.final_output.project_highlights
    top_5_highlights = dict(list(result.items())[:5])
    # Define config path
    CONFIG_PATH = "salesmind_app/static/salesmind_app/data/project_highlights.json"
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    # Save to file
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(top_5_highlights, f, indent=4, ensure_ascii=False)

    print(f"Saved top {len(top_5_highlights)} highlights to {CONFIG_PATH}")