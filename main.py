import sys
import requests

from src.config import MCP_SERVER_URL
from src.intent_analyzer import parse_intent_with_llm
from src.terraform_generator import generate_terraform_code
from src.github_actions_generator import generate_github_action_workflow
from src.git_manager import handle_git_operations
from src.resource_schemas import RESOURCE_SCHEMAS

def main():
    print("Hello from Agent AI DevOps! I can help you create and manage cloud resources.")

    print("What cloud resource would you like to create today? (e.g., 'an Azure resource group', 'a virtual machine')")
    user_input = input("> ")

    parsed_data = parse_intent_with_llm(user_input)
    print(f"DEBUG: Parsed Data: {parsed_data}")
    intent = parsed_data.get("intent")
    parameters = parsed_data.get("parameters", {})
    print(f"DEBUG: Intent: {intent}, Parameters: {parameters}")

    if intent == "create_resource":
        resource_type = parameters.get("resource_type")
        if not resource_type:
            print("Error: Resource type not identified. Please specify what type of resource you want to create.")
            return

        schema = RESOURCE_SCHEMAS.get(resource_type)
        if not schema:
            print(f"Error: Unsupported resource type: {resource_type}")
            return

        # Collect missing required parameters
        for param_name, param_info in schema.items():
            if param_info["required"] and param_name not in parameters:
                user_provided_value = input(f"{param_info["prompt"]} ")
                parameters[param_name] = user_provided_value

        print(f"Generating Terraform code for {resource_type}...")
        tf_code_to_add = generate_terraform_code(resource_type, parameters)
        print("Terraform code generated. Ready for Git operations.")
        handle_git_operations(f"feat-azure-{resource_type.replace(' ', '-')}-{parameters.get('name')}", tf_code_to_add, "main.tf")
    elif intent == "create_github_action":
        print("Okay, you want to create a GitHub Action.")

        action_name = parameters.get("action_name")
        trigger = parameters.get("trigger")
        workflow_description = parameters.get("workflow_description")

        if not action_name:
            action_name = input("What would you like to name the GitHub Action? ")
        if not trigger:
            trigger = input("What should trigger this action? (e.g., push, pull_request) ")
        if not workflow_description:
            workflow_description = input("Briefly describe what this action should do: ")

        print(f"Generating GitHub Action workflow for '{action_name}'...")
        workflow_content = generate_github_action_workflow(action_name, trigger, workflow_description)
        
        # Define the target file path for the GitHub Action workflow
        target_file_path = f".github/workflows/{action_name.lower().replace(' ', '-')}.yml"

        print("GitHub Action workflow generated. Ready for Git operations.")
        handle_git_operations(f"feat-github-action-{action_name.lower().replace(' ', '-')}", workflow_content, target_file_path)
    else:
        print("I'm not sure how to create that resource yet. Please try describing it differently.")

if __name__ == "__main__":
    main()