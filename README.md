## SalesMind
SalesMind is a GenAI-powered analytics system that helps organization analyze sales call transcripts, identify active deals, track competitors, and summarize key meeting outcomes - all through AI Agents (OpenAI Agents SDK), Retrieval-Augmented Generation (RAG) and Knowledge Graphs. It uses Django as its web interface.

The platform enables sales leaders to:

- Query transcript records
- Identify trending projects and proposals
- Track objections (pricing, feasibility, timeline, etc.)
- Discover competitor mentions
- View deal highlights and sales metrics
- Explore an interactive dashboard summarizing all deals and performance KPIs


## Directory Structure
 - SalesMind
    - salesmind_app : Main app
        - static:   [css, js-scripts, data{json-files}]
        - templates: All the html files
        - upload_transcripts: Files related to data ingestion, query. 

    - Transcripts_data : The transcripts files of all the calls.
    - manage.py

## Flow: 
![alt text](image-1.png)

## Steps to run:
    1. Clone the repo
    2. Create a python/conda environment
    3. Activate the environment
    4. Navigate to the SalesMind folder in terminal and install the dependencies in your created environment using: pip install -r requirements.txt
    5. Open two terminals, ensure the environment is activated in both and execute the below mentioned scripts.
        - Terminal 1: python manage.py runserver
        - Terminal 2: python manage.py watch_new_files
    6. Open the application using port specified in the terminal. Example (http://127.0.0.1:8000)

## Screenshots
### Dashboard page:
<img width="1895" height="827" alt="image" src="https://github.com/user-attachments/assets/ad51e273-da28-4f2e-835e-6d669ea95357" />
<img width="1866" height="822" alt="image (2)" src="https://github.com/user-attachments/assets/8aadccca-8f3d-41b7-ad85-fab40a729544" />

### AI Assistant
<img width="1919" height="829" alt="image (9)" src="https://github.com/user-attachments/assets/f3aa84e0-2920-4191-a656-1bab87419d1b" />


### Call Logs 
<img width="1897" height="824" alt="image (3)" src="https://github.com/user-attachments/assets/7ff05643-5926-446a-9d5c-f9bd91ef49b1" />

### Knowledge Graph
<img width="1915" height="829" alt="image (4)" src="https://github.com/user-attachments/assets/939e9730-632b-4697-808f-1829a3b07508" />
<img width="1602" height="830" alt="image (5)" src="https://github.com/user-attachments/assets/5b029b32-dba0-4407-b90f-275cfcefcaa5" />
<img width="905" height="790" alt="image (6)" src="https://github.com/user-attachments/assets/1e960ab0-efe7-4eb2-8e09-379da57efd14" />
<img width="748" height="665" alt="image (7)" src="https://github.com/user-attachments/assets/4a9fc113-127e-4941-9fd2-57cce8f87c5a" />

### File Upload
<img width="1918" height="828" alt="image (8)" src="https://github.com/user-attachments/assets/3001c3ea-372f-442a-ac0a-1e146c0cdabe" />


    
