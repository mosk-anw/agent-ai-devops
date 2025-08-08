import json
import openai
import sys
from src.config import OPENAI_API_KEY

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY not found in .env file or environment variables.")
    sys.exit(1)
openai.api_key = OPENAI_API_KEY

def parse_intent_with_llm(user_input):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that parses user requests into structured JSON. Identify the intent and extract parameters."},
            {"role": "user", "content": f"""
            Analyze the following user request to identify the intent and extract relevant parameters.
            The intent should be 'create_resource' or 'create_github_action'.
            
            For 'create_resource' intent, parameters should include 'resource_type' (string, e.g., 'resource group', 'virtual machine', 'storage account', 'aks cluster') and other relevant parameters for the resource.
            
            For 'create_github_action' intent, parameters should include 'action_name' (string), 'trigger' (string, e.g., 'push', 'pull_request'), and 'workflow_description' (string, a brief description of what the action should do).
            
            Respond in JSON format. If a parameter is not found, omit it.
            
            Example for 'create_resource' (resource group):
            {{"intent": "create_resource", "parameters": {{"resource_type": "resource group", "name": "my-rg", "location": "eastus"}}}}
            
            Example for 'create_github_action':
            {{"intent": "create_github_action", "parameters": {{"action_name": "deploy-app", "trigger": "push", "workflow_description": "Build and deploy a Node.js application to Azure App Service."}}}}
            User Request: {user_input}
            """}
        ]
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # You can choose a different model like "gpt-4" if available
            messages=messages,
            response_format={ "type": "json_object" }
        )
        
        parsed_json = json.loads(response.choices[0].message.content)
        return parsed_json
    except Exception as e:
        print(f"ERROR: Error parsing intent with LLM: {e}")
        return {"intent": "unknown"}