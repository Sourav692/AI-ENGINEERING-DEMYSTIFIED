# Personalized Holiday Management Agent

Phase 13 project: FastAPI + AutoGen AgentChat (planner + researcher round-robin) for personalized holiday plans. Distinct from CrewAI's travel-advisor notebooks in Phase 10.

# Personalized-Holiday-Management-Agent 


1. Create a Virtual Environment
   ```bash
   conda create -n holiday_agent python=3.12 -y
   ```

2. Activate the Virtual Environment
   ```bash 
    conda activate holiday_agent
    ```

3. Install Required Packages
    ```bash
    pip install -r requirements.txt
    ```

4. Run the FastAPI Application
    ```bash
      uvicorn app:app --reload

      ```