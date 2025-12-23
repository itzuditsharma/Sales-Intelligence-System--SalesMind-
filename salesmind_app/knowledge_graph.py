from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput, AgentOutputSchema
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import Dict
import os
from pydantic import BaseModel
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
import json
from openai import OpenAI
load_dotenv()

from .create_graph import create_graph

async def build_knowledge_graph(transcript, org_names):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    with open(transcript, "r", encoding="utf-8") as file:
        text = file.read()
    
    org_names_processed = [name.lower() for name in org_names]
    org_names_processed = [name.replace(" ", "_") for name in org_names]

    folder = 'KnowledgeGraph/organisations'
    os.makedirs(folder, exist_ok=True)

    for org in org_names_processed:
        file_path = os.path.join(folder, f"{org}.txt")
        
        if not os.path.exists(file_path):
            # Create an empty file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"All the people below are related to {org}\n")
            print(f"Created: {file_path}")
        else:
            print(f"File already exists: {file_path}")

    instructions = f"""
    You are an efficient message classifier.
    
    For each line of the transcript, identify which organisation(s) from the following list it belongs to by understanding the context from other conversation chats
    {org_names_processed}
    
    create a output in this format for every line. Make sure to include the name of person speaking in the line as well:
    {{"name_of_org": "the transcript line"}}'
    
    for example:
    {{"NovaHealth_Systems" : "AE (Liam):  Morning everyone. Thanks for joining. I’ve got Sarah from Legal, Ritesh from Pricing, and Emily, our Product Specialist, joining from our side. The goal today is to finalize commercial terms for the Cloud AI Suite pilot with NovaHealth Systems and address objections raised by Procurement. We’ll also touch on contract structure and competitor comparisons. Does that sound good?"}}

    Do this for every line in the transcript. Do not miss any line.
    """

    classifier_agent = Agent(
        name = "Classifier Agent",
        instructions=instructions,
        model = "gpt-5"
    )

    llm_output = await Runner.run(classifier_agent, text)

    llm_output = llm_output.final_output
    
    lines = [line.strip() for line in llm_output.split("\n") if line.strip()]

    output_dir = "KnowledgeGraph/organisations"
    for line in lines:
        try:
            # Try to parse each line as JSON
            data = json.loads(line)
            if not isinstance(data, dict):
                print(f"Skipping non-dict line: {line}")
                continue

            for org, message in data.items():
                # --- Step 2: Create org file if not exists ---
                file_path = os.path.join(output_dir, f"{org}.txt")
                if not os.path.exists(file_path):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(f"All the people involved in the following conversation are related to {org}\n")

                # --- Step 3: Append the message ---
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(message.strip() + "\n")

        except json.JSONDecodeError:
            print(f"Skipping invalid JSON line:\n{line}\n")
    
    print("Appended data to the right organisation file")

    print("Knowledge Graph process initiated")
    llm = ChatOpenAI(temperature=0, model="gpt-4o")
    
    system_template = """
    You are a highly intelligent graph extractor. 
    Your task is to read a meeting transcript line by line and extract relationships only between people (speakers) and clients mentioned in the conversation.
    if the script contains line like: All the people below are related to {some organisation name}, then only create relations of people related to that organisation. 
    The graph must only focus on one client and other speakers associated to it. 
    Instructions:
    1. Identify every person speaking (e.g., "AE (Liam)", "Prospect (Aisha)") as a 'Person' node.
    2. Identify the main client or organisation mentioned as a 'Client' node.
    3. Create a relationship only between a Person and the main Client if it exists.
    4. Ignore relationships between Person-Person or Client-Client.
    5. Preserve any relationship type if obvious (e.g., CLIENT, PROSPECT).
    6. Only include one client in graph that is main.

    - Include nodes (Person, Client) and edges (relationships) between them.
    """
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template)
    ])

    allowed_nodes = ["Person", "Client"]  # Only these node types will be extracted
    graph_transformer = LLMGraphTransformer(llm=llm, allowed_nodes=allowed_nodes)

    for x in org_names_processed:
        await create_graph(x, graph_transformer)



    
