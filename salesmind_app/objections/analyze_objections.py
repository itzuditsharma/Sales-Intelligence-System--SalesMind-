from agents import Agent, Runner
from dotenv import load_dotenv
load_dotenv()
 
async def find_objections(text):
    instructions = """You are an efficient Objection Detector.
    Your task is to read a conversation transcript and detect if the client raised any objections. 
    An "objection" means any form of hesitation, disagreement, or concern expressed by the client.

    You must classify the detected objections into the following categories and mark each with either 1 (present) or 0 (not present):

    {
        "price": 0 or 1,         # Client expresses concern about price, cost, or budget.
        "feasibility": 0 or 1,   # Client doubts the practicality, success, or fit of the solution.
        "Tech Stack": 0 or 1,    # Client questions or objects based on technical compatibility or technology choice.
        "Timeline": 0 or 1,      # Client raises concern about project duration, delivery, or deadlines.
        "others": 0 or 1         # Client raises any other type of objection not covered above.
    }

    Return your output **strictly as a valid JSON object** in the exact format shown below — 
    no explanations, no additional text, no formatting, and no introductory or trailing text.

    Example Output:
    {
        "price": 1,
        "feasibility": 0,
        "Tech Stack": 1,
        "Timeline": 0,
        "others": 0
    }
    """

    objection_identifier_agent = Agent(
        name = "Objection Detection",
        instructions=instructions,
        model = "gpt-4",
    )

    result = await Runner.run(objection_identifier_agent, text)     #This might use asyncio in main function 
    return result.final_output