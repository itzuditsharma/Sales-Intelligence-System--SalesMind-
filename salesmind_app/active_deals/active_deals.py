from agents import Agent, Runner
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import List
import json

load_dotenv()


DEALS_FILE = os.path.join(os.path.dirname(__file__), "deals.json")

def load_deals():
    if os.path.exists(DEALS_FILE):
        with open(DEALS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [] 

def save_deals(deals_list):
    with open(DEALS_FILE, "w", encoding="utf-8") as f:
        json.dump(deals_list, f, indent=2)

def add_new_deals(new_deals):
    deals = load_deals()
    for deal in new_deals:
        if deal not in deals:
            deals.append(deal)
    save_deals(deals)
    return deals


async def find_active_deals(text):
    class DealOutput(BaseModel):
        deals : List[str]
    
    instructions = "You are a Deal Identifier. You read transcripts and identify the hot deals that are being discussed. \
    You then return the name of those clients in form of a list. You return nothing else but just the deals that are being discussed."

    deal_identifier_agent = Agent(
        name = "Deal Identifier Agent",
        instructions=instructions,
        model = "gpt-4o-mini", 
        output_type = DealOutput
    )

    result = await Runner.run(deal_identifier_agent, text)
    print("This is res")
    print(result.final_output)
    fetched_deals = result.final_output.deals
    deals = add_new_deals(fetched_deals)
    print("Updated deals list:", deals)
    return len(deals)